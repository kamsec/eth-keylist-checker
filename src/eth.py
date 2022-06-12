"""
This file contains the code to handle eth-like chains.
"""

import os
import threading
import asyncio
from web3 import Web3
from web3.eth import AsyncEth
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils.curried import combomethod

from settings import KEYLIST, SECRETS, setup_logger

class ConfigEth:
    def __init__(self, BLOCKCHAIN_NAME):
        self.BLOCKCHAIN_NAME = BLOCKCHAIN_NAME
        if self.BLOCKCHAIN_NAME == 'eth':
            self.PROVIDER = SECRETS['PROVIDER_ETH']
        elif self.BLOCKCHAIN_NAME == 'rinkeby':
            self.PROVIDER = SECRETS['PROVIDER_RINKEBY']
        elif self.BLOCKCHAIN_NAME == 'polygon':
            self.PROVIDER = SECRETS['PROVIDER_POLYGON']
        elif self.BLOCKCHAIN_NAME == 'mumbai':
            self.PROVIDER = SECRETS['PROVIDER_MUMBAI']

        self.PRIVATE_KEY = '0x' + SECRETS['PRIVATE_KEY']

        self.w3_sync = Web3(Web3.HTTPProvider(self.PROVIDER))
        self.w3 = Web3(Web3.AsyncHTTPProvider(self.PROVIDER), modules={'eth': (AsyncEth,)}, middlewares=[])

        self.DEFAULT_GAS = 21000

        self.CHAINS = {'eth': 1,
                       'rinkeby': 4,
                       'polygon': 137,
                       'mumbai': 80001
                       }

        self.CHAIN_ID = self.CHAINS[BLOCKCHAIN_NAME]


class AccountExt(Account):
    @combomethod
    def from_key(self, private_key, BLOCKCHAIN_NAME):
        key = self._parsePrivateKey(private_key)
        return LocalAccountExt(key, self, BLOCKCHAIN_NAME=BLOCKCHAIN_NAME)


class LocalAccountExt(LocalAccount, ConfigEth):
    def __init__(self, *args, BLOCKCHAIN_NAME):
        # https://stackoverflow.com/questions/9575409/calling-parent-class-init-with-multiple-inheritance-whats-the-right-way
        LocalAccount.__init__(self, *args)  # explicit calls without super
        ConfigEth.__init__(self, BLOCKCHAIN_NAME)

    async def get_balance(self):
        return await self.w3.eth.get_balance(self.address)

    async def get_nonce(self):
        return await self.w3.eth.get_transaction_count(self.address)

    async def send(self, receiver, amount, gas_price = None, nonce = None):
        if nonce is None:
            nonce = await self.get_nonce()
        if gas_price is None:
            gas_price = await self.w3.eth.gas_price
        tx = {
            'to': receiver.address,
            'value': int(amount),
            'nonce': nonce,
            'gas': self.DEFAULT_GAS,
            'gasPrice': gas_price,
            'chainId': self.CHAIN_ID
        }
        signed_tx = self.w3_sync.eth.account.sign_transaction(tx, self.key.hex())
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()

def load_accounts(BLOCKCHAIN_NAME):
    accounts = [AccountExt.from_key('0x' + sk, BLOCKCHAIN_NAME) for sk in KEYLIST]
    return accounts

async def check_balance(**kwargs):
    w3 = kwargs['accounts'][0].w3
    DEFAULT_GAS = kwargs['accounts'][0].DEFAULT_GAS
    futures = [account.get_balance() for account in kwargs['accounts']] + [w3.eth.gas_price]
    results = await asyncio.gather(*futures)
    balances = results[:-1]
    gas_price = results[-1]
    tx_fee = gas_price * DEFAULT_GAS
    balances_minus_fees = [balance - tx_fee for balance in balances]
    if kwargs['DEBUG'] is True:
        print(f'\nBlockchain: {kwargs["accounts"][0].BLOCKCHAIN_NAME}, PID: {os.getpid()}, Thread ID: {threading.get_ident()}, Balances:')
        print(balances)
    if any(balance > 0 for balance in balances_minus_fees):
        accounts_with_balance = [(account, balance) for account, balance 
                                                    in zip(kwargs['accounts'], balances_minus_fees) if balance > 0]
        return accounts_with_balance, gas_price
    return None, None

async def send_to_master_account(accounts_with_balance, gas_price, **kwargs):
    PRIVATE_KEY = '0x' + SECRETS['PRIVATE_KEY']
    master_account = AccountExt.from_key(PRIVATE_KEY, kwargs['BLOCKCHAIN_NAME'])
    logger = setup_logger(kwargs['BLOCKCHAIN_NAME'])  # required in order to get single record per file
    try:
        futures = [account_balance_tuple[0].send(master_account, account_balance_tuple[1], gas_price) for 
            account_balance_tuple in accounts_with_balance]
        transactions = await asyncio.gather(*futures)
        if transactions != []:
            logger.info(f'Transactions sent: {transactions}')
            if kwargs['DEBUG'] is True:
                print(f'Transactions sent: {transactions}')
        return transactions
    except Exception as e:
        logger.warning(f'Exception: {e}')

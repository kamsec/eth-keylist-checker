
import secrets
import asyncio
# from bit import Key, PrivateKeyTestnet
# btc things commented out to remove bit lib dependency - not checking btc  in run.py anyway
from src.eth import AccountExt

KEYLIST = [  # for tests without changing keylist.json
    "00000000000000000000000000000000000000000000000013c96a3742f64906",
    "000000000000000000000000000000000000000000000000363d541eb611abee"
    ]

def gen_new():
    sk = secrets.token_hex(32)
    # acc_btc = Key.from_hex(sk)
    # acc_btc_testnet = PrivateKeyTestnet.from_hex(sk)
    acc_eth = AccountExt.from_key('0x' + sk, 'eth')

    print(f'Private key: {sk}')
    # print(f' - BTC         - address: {acc_btc.address}')
    # print(f' - BTC_testnet - address: {acc_btc_testnet.address}')
    print(f' - ETH         - address: {acc_eth.address}')
# gen_new()

async def check_addresses_total_tx():
    # loop = asyncio.get_running_loop()

    # btc_accounts = [Key.from_hex(sk) for sk in KEYLIST]
    # btc_futures = [loop.run_in_executor(None, account.get_transactions) for account in btc_accounts]
    # btc_tx_counts = await asyncio.gather(*btc_futures)
    # btc_tx_counts = [len(txs) if txs is not None else 0 for txs in btc_tx_counts]

    eth_accounts = [AccountExt.from_key('0x' + sk, 'eth') for sk in KEYLIST]
    eth_futures = [account.get_nonce() for account in eth_accounts]
    eth_tx_counts = await asyncio.gather(*eth_futures)

    polygon_accounts = [AccountExt.from_key('0x' + sk, 'polygon') for sk in KEYLIST]
    polygon_futures = [account.get_nonce() for account in polygon_accounts]
    polygon_tx_counts = await asyncio.gather(*polygon_futures)

    for i in range(len(KEYLIST)):
        print(f'Private key: {KEYLIST[i]}')
        # print(f' - BTC     - address: {btc_accounts[i].address}, txs: {btc_tx_counts[i]}')
        print(f' - ETH     - address: {eth_accounts[i].address}, txs: {eth_tx_counts[i]}')
        print(f' - POLYGON - address: {polygon_accounts[i].address}, txs: {polygon_tx_counts[i]}')

# asyncio.run(check_addresses_total_tx())

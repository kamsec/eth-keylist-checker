"""
Main script - run with:
python run.py
or
python run.py --debug
"""

import sys
import threading
import asyncio
import time
import platform
from sched import scheduler
from src.eth import load_accounts, check_balance, send_to_master_account
from settings import CHOSEN_ETH_NETWORKS, DELAYS

if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def daemon(local_handler, **kwargs):
    # this function works in separate threads
    # using only asyncio.run() causes "event loop closed" exception on windows, have to do it this way
    # seems like 1 event loop per thread is the way to go 
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
        accounts_with_balance, gas_price = loop.run_until_complete(check_balance(**kwargs))
        if accounts_with_balance is not None:
            loop.run_until_complete(send_to_master_account(accounts_with_balance, gas_price, **kwargs))
    except asyncio.exceptions.TimeoutError as e:
        print('Exception: ', e)
        pass
    local_handler.enter(kwargs['delay'], 1, daemon, (local_handler,), kwargs)

def main(DEBUG):
    ### ETH-like networks
    handlers = [scheduler(time.time, time.sleep) for _ in CHOSEN_ETH_NETWORKS]
    # accounts on different eth-like networks differ by used w3 and w3_sync objects
    accounts = [load_accounts(x) for x in CHOSEN_ETH_NETWORKS]
    kwargs_list = [{'accounts': acc,
                    'delay': delay,
                    'BLOCKCHAIN_NAME': network,
                    'DEBUG': DEBUG} for network, delay, acc in zip(CHOSEN_ETH_NETWORKS, DELAYS, accounts)]
    [handler.enter(0, 1, daemon, (handler,), kwargs) for handler, kwargs in zip(handlers, kwargs_list)]
    # decided to use threading instead of ThreadPoolExecutor because these threads have to be of daemon type
    threads = [threading.Thread(target=handler.run, daemon=True) for handler in handlers]
    [thread.start() for thread in threads]

    ### BTC-like networks
    ...  # not implemented

    print('To run in debug mode, use:')
    print('python run.py --debug') 
    print('Threads are running in the background...')
    print("Press ctrl+c to stop. ")

    # threads in the background do all the work, but if main thread is terminated, they are terminated as well
    # signal.pause() works on linux, but doesn't work on windows
    # input('Enter "s" to stop.') results in EOFError when running on linux as a service from systemd
    # [thread.join() for thread in threads] disables ctrl+c on main thread
    # ThreadPoolExecutor disables ctrl+c on main thread as well
    # so I ended up with threading module and:

    time.sleep(10800)
    # this makes main thread and additional threads run for 3 hours, and then will be restarted by systemd
    # when doing it in while True:, main thread is working but after around 8h the other threads seem to not work 
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--debug':
            main(DEBUG=True)
    else:
        main(DEBUG=False)

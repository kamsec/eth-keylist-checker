
import os
import json
import logging
import time

# Supported networks: 'eth', 'rinkeby', 'polygon', 'mumbai' 
CHOSEN_ETH_NETWORKS = ['eth', 'polygon']
DELAYS = [14, 3]  # delays in seconds between checks on CHOSEN_ETH_NETWORKS

if not os.path.exists('logs'):
    os.mkdir('logs')

LOG_FILENAME = 'logs/log_{}_{}.txt'

def setup_logger(BLOCKCHAIN_NAME):
    logger = logging.getLogger()  # root logger
    [logger.removeHandler(x) for x in logger.handlers[:]]
    handler = logging.FileHandler(
        LOG_FILENAME.format(
            time.strftime(
                "%Y-%m-%d_%H-%M-%S", time.localtime()
            ),
            BLOCKCHAIN_NAME
        ),
    delay=True)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", '%Y-%m-%d %H:%M:%S'))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger

with open('secrets.json') as f:
    SECRETS = json.load(f)

with open('keylist.json') as f:
    KEYLIST = json.load(f)['keylist']

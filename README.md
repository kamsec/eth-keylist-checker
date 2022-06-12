# eth-keylist-checker

This script periodically checks the balances of addresses corresponding to given private keys, and sends them to single address.
At this moment supports `Ethereum` and `Polygon`. Also works with testnets `Rinkeby` and `Mumbai`. Built wth Python, desgined for RaspberryPi and Windows.

## Description:
Script checks the balances of addresses corresponding to the private keys defined in `keylist.json `
on the networks chosen in `CHOSEN_ETH_NETWORKS` in `DELAYS` time delays in `settings.py`.
After any positive balance (over estimated tx fee) is found, the transaction to address defined in
`secrets.json` is sent. After the transaciton is sent, log is saved in `logs/` directory.

Script utilizes `threading`, `asyncio` and `sched` modules, as well as asynchronous class functions from web3.py, to minimalize delays and make possible to run it efficiently on Raspberry Pi Zero W.

## Requirements:
- Python 3.8
- web3.py

## Installation:
```
git clone https://github.com/kamsec/eth-keylist-checker.git
pip install web3
```
In case of "error: Microsoft Visual C++ 14.0 or greater is required" when installing web3, <a href="https://docs.microsoft.com/en-us/answers/questions/136595/error-microsoft-visual-c-140-or-greater-is-require.html">this link</a> might be useful.


## Setup:
1. In `keylist.json` set up the private keys to be checked for positive balance.
2. In `secrets.json` set up your private key to receive coins if any balance found on keylist private keys.
3. In `secrets.json` set up networks providers connection strings (at least one)
4. In `settings.py` set up `CHOSEN_ETH_NETWORKS` and `DELAYS`.
    - `CHOSEN_ETH_NETWORKS` have to correspond to connection strings provided in previous step. Available values: `'eth', 'rinkeby', 'polygon', 'mumbai'`
    - `DELAYS` is list of the delays in seconds, with order corresponding to order in `CHOSEN_ETH_NETWORKS`.

    
For example (in `settings.py`):
```
CHOSEN_ETH_NETWORKS = ['eth', 'polygon']
DELAYS = [15, 5]
```
Script will check the balances (and attempt to send positive amounts to single address) on Ethereum every 15 seconds, and on Polygon every 5 seconds.



## Usage:
```
python run.py
```
or
```
python run.py --debug
```

## Usage on Raspberry Pi:
Set it as a service!

```
sudo nano /etc/systemd/system/eth-keylist-checker.service
```

Enter the following content:
```ini
[Unit]
Description=eth-keylist-checker
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/eth-keylist-checker
ExecStart=/usr/bin/python3 /home/pi/eth-keylist-checker/run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then use:
```
sudo systemctl daemon-reload
sudo systemctl enable eth-keylist-checker.service
sudo systemctl start eth-keylist-checker.service
```
That's it. Now the process will run for 3 hours and if it finishes, systemd will start it again.

For debugging, these are usefull:
```
sudo systemctl status eth-keylist-checker.service
sudo systemctl stop eth-keylist-checker.service
journalctl -u eth-keylist-checker.service --until "2022-02-21 23:00:00"
journalctl -u eth-keylist-checker.service --no-pager
```
## Notes:
- The next step would be to integrate it with bitcoin-like blockchains.
I did that with <a href="https://github.com/ofek/bit">bit</a> library, but it doesn't handle async requests and is too slow, removed btc support for now.
- In case of positive balance found (over minimum tx fee) sometimes trying to
execute .send() function, will result with `replacement transaction underpriced`. It means
that there is other transaction with higher 'gasPrice' and lower 'value'.
We could recalculate values and resend the transaction to outbid it but it's not implemented. These transactions would have to be sent in the same block with lowest delay possible, and for that purpose async requests with remote node might not be enough - could require full eth node instead of external provider. This is another area for improvements.
- `utils.py` contains functions that were helpfull during development

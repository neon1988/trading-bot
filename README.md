Trading bot
=========================

### Install requirements

``pip install -r requirements.txt``

### Create db

```shell
sudo -u postgres psql
create database trading_bot;
create user trading_bot_user with encrypted password 'password';
grant all privileges on database trading_bot to trading_bot_user;
exit
sudo -u postgres psql -d trading_bot -c "CREATE EXTENSION pg_trgm;"
```

### Run migration
``python3 manage.py migrate``
### Download data
``python3 manage.py download_data ATOM_USDT 365 1h``
### Run strategy
``python3 manage.py run_strategy rsi_buy_hold_strategy AVAX_USDT 1h --exchange=gate_io_exchange``



### Supervisor config

``sudo nano /etc/supervisor/conf.d/trading_bot_avax_usdt.conf``

```
[program:trading-bot-avax-usdt]
directory=/home/user/trading-bot
command = python3 manage.py run_strategy rsi_buy_hold_strategy AVAX_USDT 1h --exchange=gate_io_exchange
startsecs = 0
user=user
autostart=true
autorestart=true
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stderr_logfile=/home/user/trading-bot/storage/log/avax-usdt.err.log
stdout_logfile=/home/user/trading-bot/storage/log/avax-usdt.out.log
```

``sudo nano /etc/supervisor/conf.d/trading_bot_atom_usdt.conf``

```
[program:trading-bot-atom-usdt]
directory=/home/user/trading-bot
command = python3 manage.py run_strategy rsi_buy_hold_strategy ATOM_USDT 1h --exchange=gate_io_exchange
startsecs = 0
user=user
autostart=true
autorestart=true
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stderr_logfile=/home/user/trading-bot/storage/log/atom-usdt.err.log
stdout_logfile=/home/user/trading-bot/storage/log/atom-usdt.out.log
```

```
sudo supervisorctl update
sudo supervisorctl start trading-bot-avax-usdt
sudo supervisorctl status all
```

```
sudo supervisorctl start trading-bot-avax-usdt
sudo supervisorctl start trading-bot-atom-usdt
```

```
sudo supervisorctl stop trading-bot-avax-usdt
sudo supervisorctl stop trading-bot-atom-usdt
```

```
sudo supervisorctl restart trading-bot-avax-usdt
sudo supervisorctl restart trading-bot-atom-usdt
```

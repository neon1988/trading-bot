import unittest

from trading_bot.trading.exchanges.backtest_exchange import BacktestExchange
import datetime


class BacktestExchangeGetCurrencyAvailableBalanceTest(unittest.TestCase):

    def test_closed_buy_trade(self):
        exchange = BacktestExchange(start_balance=1000, balance_currency='USDT')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'))

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', price=0.68, amount=51.07, side='buy', time=time, status='closed')

        self.assertAlmostEquals(50.96786, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(exchange.start_balance - 34.7276, exchange.get_balance('USDT'), 2)

    def test2(self):
        exchange = BacktestExchange(start_balance=1000, balance_currency='USDT')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'))
        self.assertAlmostEquals(exchange.start_balance, exchange.get_balance('USDT'), 2)

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')

        self.assertAlmostEquals(50.96786, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(965.2724, exchange.get_balance('USDT'), 2)

        exchange.create_trade('OGN_USDT', 0.75, 50.967, 'sell', time, status='closed')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(1003.42119, exchange.get_balance('USDT'), 2)

        exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')

        self.assertAlmostEquals(50.96786, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(968.6935, exchange.get_balance('USDT'), 2)

        exchange.create_trade('OGN_USDT', 0.75, 50.967, 'sell', time, status='closed')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(1006.8423, exchange.get_balance('USDT'), 2)

    def test_include_open_trade(self):

        exchange = BacktestExchange(start_balance=1000, balance_currency='USDT')

        time = datetime.datetime.now()

        self.assertAlmostEquals(0, exchange.get_balance('OGN'))
        self.assertAlmostEquals(exchange.start_balance, exchange.get_balance('USDT'), 2)

        trade1 = exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='open')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(exchange.start_balance - 34.7276, exchange.get_balance('USDT'), 2)

        trade2 = exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='open')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(exchange.start_balance - 69.4552, exchange.get_balance('USDT'), 2)

        exchange.cancel_trade(trade1, 'OGN_USDT')
        exchange.cancel_trade(trade2, 'OGN_USDT')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'))
        self.assertAlmostEquals(exchange.start_balance, exchange.get_balance('USDT'), 2)

    def test_open_sell_trade(self):

        exchange = BacktestExchange(start_balance=1000, balance_currency='USDT')

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', price=0.68, amount=51.07, side='buy', time=time, status="closed")

        self.assertAlmostEquals(50.96786, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(965.2724, exchange.get_balance('USDT'), 2)

        exchange.create_trade('OGN_USDT', price=0.75, amount=50.967, side='sell', time=time, status="open")

        self.assertAlmostEquals(0, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(965.2724, exchange.get_balance('USDT'), 2)



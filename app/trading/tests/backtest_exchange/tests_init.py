import unittest

from app.trading.exchanges.backtest_exchange import BacktestExchange
from app.trading.strategy import Strategy
import datetime


class BacktestExchangeInitTest(unittest.TestCase):

    def test_start_balance_and_currency(self):

        exchange = BacktestExchange(start_balance=123, balance_currency='CATE')

        self.assertEquals(123, exchange.start_balance)
        self.assertEquals('CATE', exchange.balance_currency)

        balance = exchange.balances.loc[0]

        self.assertEquals(123, balance['balance'])
        self.assertEquals('CATE', balance['currency'])

    def test_set_get_balance(self):

        exchange = BacktestExchange(start_balance=123, balance_currency='USDT')

        exchange.set_balance('CATE', 32)

        self.assertEquals(2, len(exchange.balances))
        self.assertEquals(32, exchange.get_balance('CATE'))

        exchange.set_balance('CATE', 42)

        self.assertEquals(2, len(exchange.balances))
        self.assertEquals(42, exchange.get_balance('CATE'))

        exchange.set_balance('BTC', 52)

        self.assertEquals(3, len(exchange.balances))
        self.assertEquals(52, exchange.get_balance('BTC'))



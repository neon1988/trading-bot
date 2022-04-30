import unittest

from app.trading.exchanges.backtest_exchange import BacktestExchange
from app.trading.strategy import Strategy
import datetime


class BacktestExchangeTickTest(unittest.TestCase):

    def test_close_opened_order(self):

        strategy = Strategy(exchange=BacktestExchange(start_balance=1000))

        time = datetime.datetime.now()

        self.assertEquals(1000, strategy.exchange.get_balance('USDT'))

        strategy.exchange.create_trade('OGN_USDT', 200, 2, 'buy', time, status='closed')

        self.assertEquals(0, len(strategy.exchange.get_open_trades()))

        strategy.exchange.create_trade('OGN_USDT', 100, 1, 'sell', time)

        self.assertEquals(1, len(strategy.exchange.get_open_trades()))

        strategy.backtest_before_tick({'high': 98, 'low': 95, 'datetime': 'close_time'})

        self.assertEquals(1, len(strategy.exchange.get_open_trades()))

        strategy.backtest_before_tick({'high': 101, 'low': 99, 'datetime': 'close_time'})

        self.assertEquals(0, len(strategy.exchange.get_open_trades()))

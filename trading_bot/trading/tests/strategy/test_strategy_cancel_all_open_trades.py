import unittest

from trading_bot.trading.exchanges.backtest_exchange import BacktestExchange
from trading_bot.strategies.strategy import Strategy
import datetime

class StrategyCancelAllOpenTradesTest(unittest.TestCase):

    def test_load_dataframe(self):

        strategy = Strategy(exchange=BacktestExchange(start_balance=1000))

        time = datetime.datetime.now()

        strategy.exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='open')

        self.assertEquals(1, strategy.exchange.get_open_trades_count())

        strategy.cancel_all_open_trades()

        self.assertEquals(0, strategy.exchange.get_open_trades_count())








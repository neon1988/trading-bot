import unittest

import pandas as pd

from trading_bot.trading.exchanges.backtest_exchange import BacktestExchange
from trading_bot.strategies.strategy import Strategy


class StrategyTest(unittest.TestCase):

    def test_load_dataframe(self):

        df = pd.DataFrame([])

        strategy = Strategy(exchange=BacktestExchange(start_balance=1000))
        strategy.load_dataframe(df, 'ATOM_USDT', 3600)

        self.assertEquals(0, len(strategy.df))
        self.assertEquals(3600, strategy.interval)
        self.assertEquals('ATOM_USDT', strategy.currency_pair)








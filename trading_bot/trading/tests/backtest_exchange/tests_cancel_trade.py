import unittest

from trading_bot.trading.exchanges.backtest_exchange import BacktestExchange
import datetime

class BacktestExchangeCancelTradeTest(unittest.TestCase):

    def test_cancel_buy_trade(self):
        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        id = exchange.create_trade('OGN_USDT', price=0.68, amount=51.07, side='buy', time=time, status="open")

        self.assertAlmostEquals(0, exchange.get_balance('OGN'))
        self.assertAlmostEquals(965.2724, exchange.get_balance('USDT'), 2)

        exchange.cancel_trade(id, 'OGN_USDT')

        self.assertAlmostEquals(0, exchange.get_balance('OGN'))
        self.assertAlmostEquals(1000, exchange.get_balance('USDT'), 2)

    def test_cancel_sell_trade(self):

        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', price=0.68, amount=51.07, side='buy', time=time, status="closed")

        self.assertAlmostEquals(50.96786, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(965.2724, exchange.get_balance('USDT'), 2)

        id = exchange.create_trade('OGN_USDT', price=0.75, amount=50.967, side='sell', time=time, status="open")

        self.assertAlmostEquals(0, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(965.2724, exchange.get_balance('USDT'), 2)

        exchange.cancel_trade(id, 'OGN_USDT')

        self.assertAlmostEquals(50.96786, exchange.get_balance('OGN'), 2)
        self.assertAlmostEquals(965.2724, exchange.get_balance('USDT'), 2)


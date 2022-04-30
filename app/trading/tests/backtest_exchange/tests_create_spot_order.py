import unittest

from app.trading.exchanges.backtest_exchange import BacktestExchange
from app.trading.strategy import Strategy
import datetime


class BacktestExchangeCreateSpotOrderTest(unittest.TestCase):

    def test_create_buy_order(self):
        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        id = exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')

        trade = exchange.get_trade(id, 'OGN_USDT')

        self.assertAlmostEquals(0.68, trade.price)
        self.assertAlmostEquals(51.07, trade.amount)
        self.assertEquals('buy', trade.side)
        self.assertAlmostEquals(0.10214, trade.fee, 2)
        self.assertEquals('OGN', trade.fee_currency)
        self.assertEquals(34.7276, trade.fill_price)
        self.assertEquals(time, trade.create_time)

    def test_create_sell_order(self):
        exchange = BacktestExchange()

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', 0.75, 60, 'buy', time, status='closed')

        id = exchange.create_trade('OGN_USDT', 0.75, 50.967, 'sell', time, status='closed')

        trade = exchange.get_trade(id, 'OGN_USDT')

        self.assertAlmostEquals(0.75, trade.price)
        self.assertAlmostEquals(50.967, trade.amount)
        self.assertEquals('sell', trade.side)
        self.assertAlmostEquals(0.0764505, trade.fee, 2)
        self.assertEquals('USDT', trade.fee_currency)
        self.assertEquals(38.22525, trade.fill_price)
        self.assertEquals(time, trade.create_time)

    def test_create_open_order(self):
        exchange = BacktestExchange()

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', 0.75, 60, 'buy', time, status='closed')

        id = exchange.create_trade('OGN_USDT', 0.75, 50.967, 'sell', time)

        trade = exchange.get_trade(id, 'OGN_USDT')

        self.assertAlmostEquals(0.75, trade.price)
        self.assertAlmostEquals(50.967, trade.amount)
        self.assertEquals('sell', trade.side)
        self.assertAlmostEquals(0, trade.fee, 2)
        self.assertEquals('USDT', trade.fee_currency)
        self.assertEquals(0, trade.fill_price)
        self.assertEquals(time, trade.create_time)

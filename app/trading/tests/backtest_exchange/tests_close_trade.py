import unittest

from app.trading.exchanges.backtest_exchange import BacktestExchange
from app.trading.strategy import Strategy
import datetime


class BacktestExchangeCloseTradeTest(unittest.TestCase):

    def test_open_and_close_trade(self):
        exchange = BacktestExchange()

        time = datetime.datetime.now()

        id = exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time)

        self.assertEquals(1, exchange.get_open_trades_count())
        self.assertFalse(exchange.is_trade_closed(id, 'OGN_USDT'))

        exchange.close_trade(id, 'OGN_USDT')

        trade = exchange.get_trade(id, 'OGN_USDT')

        self.assertAlmostEquals(0.10214, trade.fee, 2)
        self.assertEquals('OGN', trade.fee_currency)
        self.assertEquals(34.7276, trade.fill_price)

        self.assertEquals(0, exchange.get_open_trades_count())
        self.assertTrue(exchange.is_trade_closed(id, 'OGN_USDT'))

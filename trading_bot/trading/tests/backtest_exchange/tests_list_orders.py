import unittest

from trading_bot.trading.exchanges.backtest_exchange import BacktestExchange
import datetime


class BacktestExchangeListOrdersTest(unittest.TestCase):

    def test_list_orders(self):
        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')
        exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')

        self.assertEquals(2, len(exchange.list_orders('OGN_USDT', 'closed')))

        items = iter(exchange.list_orders('OGN_USDT', 'closed'))

        trade1 = next(items)
        trade2 = next(items)

        self.assertTrue(trade1.is_closed())
        self.assertTrue(trade2.is_closed())

    def test_side_param(self):
        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')

        self.assertEquals(1, len(exchange.list_orders('OGN_USDT', status='closed', side='buy')))
        self.assertEquals(0, len(exchange.list_orders('OGN_USDT', status='closed', side='sell')))

    def test_from_param(self):
        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')

        self.assertEquals(1, len(exchange.list_orders('OGN_USDT', status='closed', _from=time - datetime.timedelta(seconds=10))))
        self.assertEquals(0, len(exchange.list_orders('OGN_USDT', status='closed', _from=time + datetime.timedelta(seconds=10))))

    def test_to_param(self):
        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        exchange.create_trade('OGN_USDT', 0.68, 51.07, 'buy', time, status='closed')

        self.assertEquals(1, len(exchange.list_orders('OGN_USDT', status='closed', to=time + datetime.timedelta(seconds=10))))
        self.assertEquals(0, len(exchange.list_orders('OGN_USDT', status='closed', to=time - datetime.timedelta(seconds=10))))
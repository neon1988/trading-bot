import unittest

from trading_bot.trading.exchanges.backtest_exchange import BacktestExchange
import datetime


class BacktestExchangeGetProfitFromClosedTradesTest(unittest.TestCase):

    def test(self):

        exchange = BacktestExchange(start_balance=1000)

        time = datetime.datetime.now()

        text = str(int(datetime.datetime.now().timestamp() * 1000000))

        exchange.create_trade('OGN_USDT', 0.75, 60, 'buy', time, status='closed', text=text)

        id = exchange.create_trade('OGN_USDT', 1.4, 50.967, 'sell', time, status='closed', text=text)

        profit = exchange.get_profit_from_closed_trades()

        self.assertAlmostEquals(26.3537, profit, 2)

        text = str(int(datetime.datetime.now().timestamp() * 1000000))

        exchange.create_trade('OGN_USDT', 0.75, 60, 'buy', time, status='closed', text=text)

        id = exchange.create_trade('OGN_USDT', 1.5, 50.967, 'sell', time, status='closed', text=text)

        profit = exchange.get_profit_from_closed_trades()

        self.assertAlmostEquals(57.8043, profit, 2)

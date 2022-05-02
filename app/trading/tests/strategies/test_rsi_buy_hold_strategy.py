from app.strategies.rsi_buy_hold_strategy import RsiBuyHoldStrategy
from app.trading.exchanges.backtest_exchange import BacktestExchange
import unittest
import datetime


class RSIBuyHoldStrategyTest(unittest.TestCase):

    def test_disable_to_open_double_trade(self):

        strategy = RsiBuyHoldStrategy(exchange=BacktestExchange(start_balance=1000))
        strategy.interval = 3600
        strategy.currency_pair = 'ATOM_USDT'

        tick = strategy.tick({'buy': 1, 'close': 32, 'datetime': datetime.datetime.fromisoformat('2021-04-26 15:30:00')})

        self.assertTrue(tick)
        self.assertEquals(1, strategy.exchange.get_closed_trades_count())

        tick = strategy.tick({'buy': 1, 'close': 32, 'datetime': datetime.datetime.fromisoformat('2021-04-26 15:31:00')})

        self.assertEquals(1, strategy.exchange.get_closed_trades_count())
        self.assertFalse(tick)

    def test_buy_trade_and_sell_open_trade(self):

        strategy = RsiBuyHoldStrategy(exchange=BacktestExchange(start_balance=1000))
        strategy.interval = 3600
        strategy.currency_pair = 'ATOM_USDT'
        strategy.max_simultaneous_open_trades_limit = 20
        strategy.take_profit_percentage = 7
        strategy.fee = 0.2

        tick = strategy.tick(
            {'buy': 1, 'close': 32, 'datetime': datetime.datetime.fromisoformat('2021-04-26 15:30:00')})

        closed_trades = strategy.exchange.list_orders('ATOM_USDT', "closed", 1)

        self.assertEquals(1, len(closed_trades))

        trade = next(iter(closed_trades))

        self.assertTrue(trade.is_closed())
        self.assertEquals(1.5625, trade.amount)
        self.assertEquals(32, trade.price)
        self.assertEquals('closed', trade.status)
        self.assertEquals('buy', trade.side)

        open_trades = strategy.exchange.list_orders('ATOM_USDT', "open", 1)

        self.assertEquals(1, len(open_trades))

        trade2 = next(iter(open_trades))

        self.assertFalse(trade2.is_closed())
        self.assertAlmostEquals(1.547825625, trade2.amount, 4)
        self.assertEquals(34.24, trade2.price)
        self.assertEquals('open', trade2.status)
        self.assertEquals('sell', trade2.side)

        self.assertEquals(trade.text, trade2.text)





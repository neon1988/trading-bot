from pandas import DataFrame

from app.trading.strategy import Strategy
import pandas_ta as ta
import numpy as np
import datetime


class RsiBuyHoldStrategy(Strategy):
    fee = 0.2
    rsi = 6
    rsi_buy_limit = 42
    take_profit_percentage = 7
    max_simultaneous_open_trades_limit = 20

    def append_indicators(self):
        df = self.df

        df.ta.rsi(length=self.rsi, append=True)

        df = df.fillna(0)

        df = (df.replace((np.inf, -np.inf), np.nan).dropna())

        df['buy'] = 0
        df.loc[df[f'RSI_{self.rsi}'] < self.rsi_buy_limit, 'buy'] = 1
        df.loc[df[f'RSI_{self.rsi}'] == 0, 'buy'] = 0

        df['buy_shift'] = df['buy'].shift(periods=1)
        df.loc[df['buy'] == df['buy_shift'], 'buy'] = 0

        del df['buy_shift']

        self.df = df

        return self.df

    def tick(self, candlestick) -> bool:

        if candlestick[f'buy'] > 0:

            recent_opened_trades = self.exchange.list_orders(currency_pair=self.currency_pair,
                                                             status="closed", limit=1,
                                                             _from=candlestick['datetime'] - datetime.timedelta(seconds=self.interval),
                                                             side="buy")

            if len(recent_opened_trades) > 0:
                return False

            quantity = self.exchange.get_currency_available_balance('USDT') / self.max_simultaneous_open_trades_limit

            amount = quantity / candlestick['close']

            id = self.exchange.create_trade(
                self.currency_pair,
                price=candlestick['close'], amount=amount, side='buy',
                time=candlestick['datetime'], status="closed")

            trade = self.exchange.get_trade(id, self.currency_pair)

            if trade.is_closed():
                amount = trade.amount - trade.fee - 0.01

                price = (100 + self.take_profit_percentage) * candlestick['close'] / 100

                self.exchange.create_trade(
                    self.currency_pair,
                    price=price, amount=amount, side='sell',
                    time=candlestick['datetime'], status="open")
            else:
                raise Exception('Trade is still open')

        return True

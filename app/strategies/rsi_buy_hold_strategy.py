from pandas import DataFrame

from app.trading.strategy import Strategy
import pandas_ta as ta
import numpy as np
import datetime


class RsiBuyHoldStrategy(Strategy):
    fee = 0.2
    rsi = 21
    rsi_buy_limit = 30
    take_profit_percentage = 13
    max_simultaneous_open_trades_limit = 20
    min_quantity = 1.1

    def load_dataframe(self, *args, **kwargs):
        super(RsiBuyHoldStrategy, self).load_dataframe(*args, **kwargs)

        if self.currency_pair.upper() == 'ATOM_USDT':
            self.rsi = 20
            self.rsi_buy_limit = 40
            self.take_profit_percentage = 13

        if self.currency_pair.upper() == 'AVAX_USDT':
            self.rsi = 20
            self.rsi_buy_limit = 40
            self.take_profit_percentage = 50

        #print(f'rsi {self.rsi} rsi_buy_limit {self.rsi_buy_limit} take_profit_percentage {self.take_profit_percentage}')

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

            if quantity < self.min_quantity:
                return False

            text = self.get_trade_group_id()

            id = self.exchange.create_trade(
                self.currency_pair,
                price=candlestick['close'], amount=amount, side='buy',
                time=candlestick['datetime'], status="closed", text=text)

            trade = self.exchange.get_trade(id, self.currency_pair)

            if trade.is_closed():
                amount = trade.amount - trade.fee

                amount = amount - amount * 0.1 / 100   # minus 0.1 percent

                price = (100 + self.take_profit_percentage) * candlestick['close'] / 100

                self.exchange.create_trade(
                    self.currency_pair,
                    price=price, amount=amount, side='sell',
                    time=candlestick['datetime'], status="open", text=text)
            else:
                print('Trade is still open')

                self.exchange.cancel_trade(id, self.currency_pair)

        return True

    def get_trade_group_id(self) -> int:
        return int(datetime.datetime.now().timestamp() * 1000000)
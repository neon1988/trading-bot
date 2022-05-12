from pandas import DataFrame

from trading_bot.strategies.strategy import Strategy
import numpy as np


class MyStrategy(Strategy):
    # HIGH PROFIT 1 Minute Chart Scalping Strategy Proven 100 Trades - RSI+ 200 EMA+ Engulfing
    # https://www.youtube.com/watch?v=AM52D58vGQk
    # Нет работает даже с низкой комиссией

    fee = 0.2
    order_id = None

    def append_indicators(self) -> DataFrame:

        df = self.df

        if df is None:
            raise Exception('Dataframe is None')

        df.ta.rsi(append=True)
        df.ta.ema(length=10, append=True)

        df.ta.cdl_pattern('engulfing', append=True)
        engulfing_shift = df.ta.cdl_pattern('engulfing').shift(1).fillna(0)
        df.loc[engulfing_shift['CDL_ENGULFING'] != 0, 'CDL_ENGULFING'] = engulfing_shift

        df['EMA_10_shift'] = df['EMA_10'] - df['EMA_10'].shift(1)

        df = df.fillna(0)

        df = (df.replace((np.inf, -np.inf), np.nan).dropna())

        self.df = df

        return df

    def tick(self, candlestick):

        if candlestick['RSI_14'] > 50 and candlestick['CDL_ENGULFING'] > 0 and candlestick['EMA_10_shift'] > 0:

            if self.exchange.get_open_trades_count() < 1:

                stop_loss_percentage = (100 - candlestick['low'] * 100 / candlestick['close'])
                take_profit_percentage = (100 - candlestick['low'] * 100 / candlestick['close']) * 2

                if take_profit_percentage > self.fee + 0.2:
                    self.exchange.create_trade(
                        self.currency_pair,
                        price=candlestick['close'], amount=1, side='buy',
                        time=candlestick['datetime'], status="closed")

                # if self.has_opened_orders():
                #     if row['RSI_14'] > 60:
                #         self.close_order(
                #             index=self.order_id,
                #             price=row['close'],
                #             datetime=row['datetime']
                #         )

        # print(self.get_opened_orders_count())

        # self.get_opened_orders()

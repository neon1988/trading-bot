from pandas import DataFrame

from trading_bot.strategies.strategy import Strategy
import numpy as np


class MACDCrossEMA200Strategy(Strategy):

    # прибыль не приносит
    fee = 0.1
    order_id = None
    order_was_opened_after_lines_crossed = False

    def append_indicators(self, df: DataFrame) -> DataFrame:
        df.ta.macd(append=True)
        df.ta.ema(length=200, append=True)

        df = df.fillna(0)

        df = (df.replace((np.inf, -np.inf), np.nan).dropna())

        df['EMA_200_shift'] = df['EMA_200'] - df['EMA_200'].shift(1)

        return df

    def tick(self, candlestick):
        super().tick(candlestick)

        if candlestick['MACDh_12_26_9'] < 0:
            self.order_was_opened_after_lines_crossed = False

        if not self.has_opened_orders() and self.order_was_opened_after_lines_crossed == False:
            if candlestick['EMA_200'] > 0 and candlestick['EMA_200_shift'] > 0:
                if candlestick['MACDh_12_26_9'] > 0:

                    distance_percentage = (100 - candlestick['EMA_200'] * 100 / candlestick['close'])

                    if distance_percentage > 3:
                        distance_percentage = 3

                    take_profit_percentage = distance_percentage * 1.5
                    stop_loss_percentage = distance_percentage + 0.3

                    if stop_loss_percentage > 1:
                        self.order_id = self.open_order(
                            type='long',
                            price=candlestick['close'],
                            datetime=candlestick['datetime'],
                            take_profit_percentage=take_profit_percentage,
                            stop_loss_percentage=stop_loss_percentage
                        )

                        self.order_was_opened_after_lines_crossed = True

                # if self.has_opened_orders():
                #     if row['RSI_14'] > 60:
                #         self.close_order(
                #             index=self.order_id,
                #             price=row['close'],
                #             datetime=row['datetime']
                #         )

        # print(self.get_opened_orders_count())

        # self.get_opened_orders()
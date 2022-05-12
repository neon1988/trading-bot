from pandas import DataFrame

from trading_bot.strategies.strategy import Strategy
import numpy as np


class CrossEMALinesStrategy(Strategy):
    # EASY Day Trading Strategy for BTC Tested! [81% WINRATE]
    # https://www.youtube.com/watch?v=BN01TrCeY5g
    # За год дает около 50% выигрышей

    fee = 0.1
    order_id = None
    order_was_opened_after_lines_crossed = False

    def append_indicators(self, df: DataFrame) -> DataFrame:
        df.ta.ema(length=25, append=True)
        df.ta.ema(length=50, append=True)

        df = df.fillna(0)

        df = (df.replace((np.inf, -np.inf), np.nan).dropna())

        return df

    def tick(self, candlestick):
        super().tick(candlestick)

        if candlestick['EMA_50'] > candlestick['EMA_25']:
            self.order_was_opened_after_lines_crossed = False

        if not self.has_opened_orders() and self.order_was_opened_after_lines_crossed == False:
            if candlestick['EMA_25'] > candlestick['EMA_50']:
                self.order_id = self.open_order(
                    type='long',
                    price=candlestick['close'],
                    datetime=candlestick['datetime'],
                    take_profit_percentage=2 + self.fee * 2,
                    stop_loss_percentage=2 - self.fee * 2
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
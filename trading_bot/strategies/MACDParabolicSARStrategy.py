from pandas import DataFrame

from trading_bot.strategies.strategy import Strategy
import numpy as np

class MACDParabolicSARStrategy(Strategy):
    # 70% Win Rate Highly Profitable MACD + Parabolic SAR + 200 EMA Trading Strategy (Proven 100 Trades)
    # https://www.youtube.com/watch?v=sbKTRVWppZY
    # Проверял на 15m, 30m и 1h. Прибыль не приносит

    fee = 0.1
    order_id = None
    latest_macd_cross_trade_was_opened = False

    def append_indicators(self, df: DataFrame) -> DataFrame:
        df.ta.psar(append=True)
        df.ta.ema(length=200, append=True)
        df.ta.macd(append=True)

        df['EMA_200_shift'] = df['EMA_200'] - df['EMA_200'].shift(1)

        df = df.fillna(0)

        df = (df.replace((np.inf, -np.inf), np.nan).dropna())

        return df

    def tick(self, candlestick):
        super().tick(candlestick)

        if self.latest_macd_cross_trade_was_opened and candlestick['MACDh_12_26_9'] < 0:
          self.latest_macd_cross_trade_was_opened = False

        if self.latest_macd_cross_trade_was_opened == False and not self.has_opened_orders():
          # Если цена находится выше 200 EMA
          if candlestick['close'] > candlestick['EMA_200']:
            # Если пересекаются линии MACD вверх
            if candlestick['MACDh_12_26_9'] > 0:
              # Если точки индиактора psar находятся под ценой
              if candlestick['PSARl_0.02_0.2'] > 0:

                stop_loss_price = candlestick['PSARl_0.02_0.2']
                stop_loss_percentage = (100 - stop_loss_price * 100 / candlestick['close'])

                if stop_loss_percentage > 0.7:
                  stop_loss_percentage = 0.7

                take_profit_percentage = stop_loss_percentage

                if take_profit_percentage > self.fee * 2:

                  self.order_id = self.open_order(
                      type='long',
                      price=candlestick['close'],
                      datetime=candlestick['datetime'],
                      take_profit_percentage=take_profit_percentage + self.fee * 2,
                      stop_loss_percentage=stop_loss_percentage
                  )

                  self.latest_macd_cross_trade_was_opened = True

            # if self.has_opened_orders():
            #     if row['RSI_14'] > 60:
            #         self.close_order(
            #             index=self.order_id,
            #             price=row['close'],
            #             datetime=row['datetime']
            #         )

        # print(self.get_opened_orders_count())

        # self.get_opened_orders()
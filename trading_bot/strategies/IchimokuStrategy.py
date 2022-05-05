from pandas import DataFrame

from trading_bot.strategies.strategy import Strategy
import numpy as np


class IchimokuStrategy(Strategy):

    # На часовом графике приносит прибыль со совсем немного. Возможно просто погрешность

    fee = 0.1
    order_id = None
    opened = False

    def append_indicators(self, df: DataFrame) -> DataFrame:
        df.ta.ichimoku(append=True, lookahead=False)
        df.ta.ema(length=200, append=True)
        df.ta.rsi(append=True)

        df = df.fillna(0)

        df = (df.replace((np.inf, -np.inf), np.nan).dropna())

        return df

    def tick(self, candlestick):
        super().tick(candlestick)

        # ISA cloud fast
        # ISB cloud slow
        # ITS tenkan fast
        # IKS kijun slow

        if not self.has_opened_orders():
            if candlestick['close'] < candlestick['ISA_9']:
                self.opened = False

        if not self.has_opened_orders() and self.opened == False:
            # если линия tenkan выше чем kijun
            if candlestick['ITS_9'] > candlestick['IKS_26']:
                # если цена закрытия выше облака
                if candlestick['close'] > candlestick['ISA_9'] and candlestick['close'] > candlestick['ISB_26']:

                    stop_loss_percentage = 100 - candlestick['ISB_26'] * 100 / candlestick['close'] + 0.2

                    if stop_loss_percentage > 2:
                        stop_loss_percentage = 2

                    if stop_loss_percentage > 0.6:
                        self.order_id = self.open_order(
                            type='long',
                            price=candlestick['close'],
                            datetime=candlestick['datetime'],
                            take_profit_percentage=8,
                            stop_loss_percentage=stop_loss_percentage
                        )

                        self.opened = True

        if self.has_opened_orders():
            if candlestick['ITS_9'] < candlestick['IKS_26']:
                self.close_order(
                    index=self.order_id,
                    price=candlestick['close'],
                    datetime=candlestick['datetime']
                )

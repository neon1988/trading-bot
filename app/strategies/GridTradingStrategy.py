from pandas import DataFrame

from app.trading.strategy import Strategy
import pandas_ta as ta
import numpy as np
import pandas as pd


class GridTradingStrategy(Strategy):
    fee = 0.2
    take_profit_percentage = 10
    low_price = None
    high_price = None
    grid_count = 50

    def __init__(self, low_price, high_price, *args, **kwargs):
        super(GridTradingStrategy, self).__init__(*args, **kwargs)

        self.low_price = low_price
        self.high_price = high_price

        self.step = round((self.high_price - self.low_price) / self.grid_count)

        if self.step < 1:
            raise 'Step must be higher than 1'

        grid = []

        for i in range(self.low_price, self.high_price, self.step):
            grid.append([i, i + self.step])

        print(grid)

        self.grid = pd.DataFrame(grid, columns=['low_price', 'high_price']) \
            .astype({'low_price': np.float32, 'high_price': np.float32})

        quantity = round(self.start_balance / self.grid_count)

        for index, row in self.grid.iterrows():
            take_profit_percentage = (row['high_price'] * 100 / row['low_price']) - 100

            self.create_trade(
                type='long',
                price=row['low_price'],
                take_profit_percentage=take_profit_percentage,
                quantity=quantity
            )

    def get_grid(self):
        return self.grid

    def tick(self, candlestick):
        super().tick(candlestick)

        range = self.grid[
            (self.grid['low_price'] < candlestick['close']) & (self.grid['high_price'] > candlestick['close'])]

        if len(range) > 0:

            orders = self.get_orders()

            order = orders[(orders['close_price'].isna()) & (orders['open_price'] == int(range['low_price']))]

            if len(order) < 1:
                quantity = self.get_available_balance() / self.grid_count

                take_profit_percentage = (int(range['high_price']) * 100 / int(range['low_price'])) - 100

                self.create_trade(
                    type='long',
                    price=int(range['low_price']),
                    take_profit_percentage=take_profit_percentage,
                    quantity=quantity
                )

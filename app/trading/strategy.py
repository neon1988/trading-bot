import pandas as pd
import numpy as np
from pandas import DataFrame
from tqdm import tqdm
import time


class Strategy:
    fee = 0.2
    # limit on the maximum number of open trades
    max_simultaneous_open_trades_limit = 1
    # the maximum number of transactions that were opened at the same time
    max_simultaneous_open_trades_count = 0

    def __init__(self, exchange, start_balance=1000):
        self.interval = None
        self.currency_pair = None
        self.df = None
        self.exchange = exchange
        self.start_balance = start_balance
        self.balance = start_balance

    def load_dataframe(self, df: DataFrame, currency_pair: str, interval: int):
        self.df = df
        self.currency_pair = str(currency_pair)
        self.interval = int(interval)

        if len(self.df) > 0:
            self.df = self.df.astype({
                'datetime': 'datetime64[ns]', 'open': np.float32, 'close': np.float32, 'low': np.float32,
                'high': np.float32, 'volume': np.float32
            })

    def append_indicators(self) -> DataFrame:
        return self.df

    def has_opened_orders(self) -> bool:
        return len(self.exchange.get_open_orders()) > 0

    def get_max_simultaneous_open_trades_count(self):
        return self.max_simultaneous_open_trades_count

    def open_order(self, index: int, open_datetime: np.str):
        self.exchange.orders.at[index, 'open_datetime'] = open_datetime

    def tick(self, candlestick) -> bool:
        return True

    def backtest(self):
        pbar = tqdm(self.df.iterrows(), total=len(self.df), colour='green')

        for index, candlestick in pbar:
            self.backtest_before_tick(candlestick=candlestick)
            self.tick(candlestick=candlestick)
            pbar.set_description(
                f"Strategy backtesting {index} Balance: {self.exchange.get_balance('USDT')} Open trades: {self.exchange.get_open_trades_count()} ")

    def backtest_before_tick(self, candlestick) -> bool:

        open_trades = self.exchange.get_open_trades()

        if len(open_trades) > 0:

            for index, item in open_trades[(candlestick['low'] < open_trades['price']) & (
                    candlestick['high'] > open_trades['price'])].iterrows():
                self.exchange.close_trade(item['id'], time=candlestick['datetime'], currency_pair=item['currency_pair'])

        return True

    def cancel_all_open_trades(self):
        open_trades = self.exchange.get_open_trades()

        for index, item in open_trades.iterrows():
            self.exchange.cancel_trade(item['id'], item['currency_pair'])

    def get_available_balance(self) -> float:
        return self.balance

    def get_start_balance(self) -> float:
        return self.start_balance

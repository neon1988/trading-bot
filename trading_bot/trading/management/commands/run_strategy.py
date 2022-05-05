from django.core.management.base import BaseCommand

from trading_bot.trading.enums.intervals import Intervals
from trading_bot.trading.models import Candlestick
from typing import List
from django.core.management import call_command
import pandas as pd
import importlib
import humps
import time

class Command(BaseCommand):
    help = 'Run strategy'
    timeout = 5

    def add_arguments(self, parser):
        parser.add_argument('strategy', type=str, help='Name of strategy')
        parser.add_argument('pair', type=str, help='Pair')
        parser.add_argument('interval', type=str, help='Interval')
        parser.add_argument('--exchange', type=str, help='Exchange for trade', default='backtest_exchange')
        parser.add_argument('--candlesticks_count', type=int, help='Interval', default=100)

    def handle(self, *args, **options):

        print(f'Interval in seconds {self.get_interval_in_seconds(options)}')

        while True:

            self.update_candlesticks(options)
            dataframe = self.get_candlesticks(options)
            self.strategy(dataframe, options)

            time.sleep(self.get_interval_in_seconds(options))

    def strategy(self, dataframe, options):
        strategy_name = options['strategy']

        exchange = self.load_class('trading_bot.trading.exchanges', options['exchange'])()

        strategy = self.load_class('trading_bot.strategies', strategy_name)(exchange=exchange)
        strategy.load_dataframe(dataframe, options['pair'], self.get_interval_in_seconds(options))
        strategy.append_indicators()

        print(strategy.df.tail(5))

        latest_candle = strategy.df.iloc[-1]

        strategy.tick(latest_candle)

    def update_candlesticks(self, options):
        call_command('download_data', options['pair'], 1, options['interval'])
        self.stdout.write(f"Data for the day has been updated")

    def get_candlesticks(self, options):
        query = Candlestick.objects \
            .filter(interval=options['interval']) \
            .filter(pair=options['pair']) \
            .order_by('-datetime')

        candlesticks_count = options['candlesticks_count']

        candlesticks = query[:candlesticks_count]

        dataframe = pd.DataFrame(list(candlesticks.values())) \
            .sort_values(by='datetime') \
            .reset_index()

        dataframe = dataframe[['datetime', 'open', 'close', 'low', 'high', 'volume']]

        if len(candlesticks) < candlesticks_count:
            raise Exception('Query result lower than candlesticks count')

        return dataframe

    def load_class(self, path: str, name: str):
        module = importlib.import_module(f"{path}.{name}")
        return getattr(module, humps.pascalize(name))

    def get_interval_in_seconds(self, options) -> int:
        return Intervals.dict[options['interval']]

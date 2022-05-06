from datetime import datetime
from pandas import DataFrame

from django.core.management.base import BaseCommand

from trading_bot.trading.enums.intervals import Intervals
from trading_bot.trading.exchanges.backtest_exchange import BacktestExchange
from trading_bot.trading.models import Candlestick
import importlib
import pandas as pd
import humps

class Command(BaseCommand):
    help = 'Backtest strategy on historical data'

    def add_arguments(self, parser):
        # parser.add_argument('strategy_path', type=str)
        parser.add_argument('strategy', type=str)
        parser.add_argument('pair', type=str)
        parser.add_argument('days', type=int)
        parser.add_argument('interval', type=str)

    def handle(self, *args, **options):

        dataframe = self.candlesticks_dataframe(options)

        exchange = BacktestExchange(start_balance=1000)

        self.strategy = self.load_class('trading_bot.strategies', options['strategy'])(exchange=exchange)

        options['interval'] = Intervals.dict[options['interval']]

        self.strategy.load_dataframe(dataframe, options['pair'], options['interval'])
        self.strategy.append_indicators()

        self.stdout.write(self.style.SUCCESS('Testing of the strategy is started'))

        self.strategy.backtest()

        self.stdout.write(self.style.SUCCESS('Testing of the strategy is completed'))

        self.strategy.cancel_all_open_trades()

        self.report(options)

    def report(self, options):

        currency_pair = options['pair']

        currency1, currency2 = currency_pair.upper().split("_")

        self.stdout.write(f'{currency1} balance: {round(self.strategy.exchange.get_balance(currency1), 3)}')
        self.stdout.write(f'{currency2} balance: {round(self.strategy.exchange.get_balance(currency2), 3)}')

    def load_class(self, path: str, name: str):
        module = importlib.import_module(f"{path}.{name}")
        return getattr(module, humps.pascalize(name))

    def candlesticks_dataframe(self, options) -> DataFrame:

        query = Candlestick.objects \
            .filter(interval=options['interval']) \
            .filter(pair=options['pair'].upper()) \
            .order_by('-datetime')

        if len(query) < 1:
            return self.stdout.write(self.style.ERROR('Latest candlestick not found'))

        latest_candle = query[0]

        to = int(latest_candle.datetime.timestamp())
        _from = int(to - (options['days'] * 60 * 60 * 24))

        candlesticks = Candlestick.objects \
            .filter(interval=options['interval']) \
            .filter(pair=options['pair'].upper()) \
            .filter(datetime__range=(datetime.fromtimestamp(_from), datetime.fromtimestamp(to))) \
            .order_by('datetime')

        if candlesticks.count() < 1:
            return self.stdout.write(self.style.ERROR('Empty candlestick history'))

        dataframe = pd.DataFrame(list(candlesticks.values())) \
            .sort_values(by='datetime')

        dataframe = dataframe[['datetime', 'open', 'close', 'low', 'high', 'volume']]

        return dataframe

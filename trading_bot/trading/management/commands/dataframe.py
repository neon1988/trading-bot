from datetime import datetime

from django.core.management.base import BaseCommand

from trading_bot.trading.models import Candlestick
import pandas as pd

# python3 manage.py dataframe btc_usdt_60 BTC_USDT 21 1m

class Command(BaseCommand):
    help = 'Backtest strategy on historical data'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('pair', type=str)
        parser.add_argument('days', type=int)
        parser.add_argument('interval', type=str)

    def handle(self, *args, **options):

        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 100)

        query = Candlestick.objects \
            .filter(interval=options['interval']) \
            .filter(pair=options['pair']) \
            .order_by('-datetime')

        if len(query) < 1:
            return self.stdout.write(self.style.ERROR('Latest candlestick not found'))

        latest_candle = query[0]

        to = int(latest_candle.datetime.timestamp())
        _from = int(to - (options['days'] * 60 * 60 * 24))

        candlesticks = Candlestick.objects \
            .filter(interval=options['interval']) \
            .filter(pair=options['pair']) \
            .filter(datetime__range=(datetime.fromtimestamp(_from), datetime.fromtimestamp(to))) \
            .order_by('datetime')

        if candlesticks.count() < 1:
            return self.stdout.write(self.style.ERROR('Empty candlestick history'))

        dataframe = pd.DataFrame(list(candlesticks.values())) \
            .sort_values(by='datetime')

        dataframe = dataframe[['datetime', 'open', 'close', 'low', 'high', 'volume']]

        dataframe.to_csv(
            path_or_buf=f'csv/{options["name"]}.csv.zip',
            index=False,
            compression=dict(method='zip', archive_name=f'{options["name"]}.csv')
        )

        self.stdout.write(self.style.SUCCESS(f'File {options["name"]}.csv.zip created'))
        self.stdout.write(self.style.SUCCESS(f'{len(dataframe)} rows written'))
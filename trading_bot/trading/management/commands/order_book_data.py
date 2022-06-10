from datetime import datetime

from django.core.management.base import BaseCommand

from trading_bot.trading.models import Candlestick, OrderBook
import pandas as pd
import os

# python3 manage.py order_book_data order_book_binance_BTC_USDT_60 BTC_USDT 100 binance 60

class Command(BaseCommand):
    help = 'Create an order book data file'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str)
        parser.add_argument('pair', type=str)
        parser.add_argument('days', type=int)
        parser.add_argument('exchange', type=str)
        parser.add_argument('interval', type=str)

    def handle(self, *args, **options):

        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 100)

        query = OrderBook.objects \
            .filter(exchange=options['exchange']) \
            .filter(interval=options['interval']) \
            .filter(pair=options['pair']) \
            .order_by('-datetime')

        if len(query) < 1:
            return self.stdout.write(self.style.ERROR('Latest order book not found'))

        latest_order_book = query[0]

        to = int(latest_order_book.datetime.timestamp())
        _from = int(to - (options['days'] * 60 * 60 * 24))

        order_book = OrderBook.objects \
            .filter(exchange=options['exchange']) \
            .filter(interval=options['interval']) \
            .filter(pair=options['pair']) \
            .filter(datetime__range=(datetime.fromtimestamp(_from), datetime.fromtimestamp(to))) \
            .order_by('datetime')

        if order_book.count() < 1:
            return self.stdout.write(self.style.ERROR('Empty order book history'))

        dataframe = pd.DataFrame(list(order_book.values())) \
            .sort_values(by='datetime')

        dataframe = dataframe[['datetime', 'asks', 'bids']]

        if not os.path.exists('csv/order_book'):
            os.mkdir('csv/order_book')

        dataframe.to_csv(
            path_or_buf=f'csv/order_book/{options["name"]}.csv.zip',
            index=False,
            compression=dict(method='zip', archive_name=f'{options["name"]}.csv')
        )

        self.stdout.write(self.style.SUCCESS(f'File {options["name"]}.csv.zip created'))
        self.stdout.write(self.style.SUCCESS(f'{len(dataframe)} rows written'))

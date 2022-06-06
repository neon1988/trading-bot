import time
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from gate_api import ApiClient, SpotApi, Configuration

from trading_bot.trading.enums.intervals import Intervals
from trading_bot.trading.models import Candlestick
from trading_bot.service.gate_io_api import api_client
from typing import List
import math
import requests
import pandas as pd
import io
from pandas import DataFrame

class Command(BaseCommand):
    help = 'Downloading cryptocurrency exchange rate'

    def add_arguments(self, parser):
        parser.add_argument('pair', type=str, help='Cryptocurrency pair')
        parser.add_argument('days', type=int, help='Number of days')
        parser.add_argument('interval', type=str, help='Interval')

        parser.add_argument(
            '--batch-size',
            default=999,
            type=int,
            help='Batch size',
        )

    def handle(self, *args, **options):

        spot_api = SpotApi(api_client)

        to = int(time.time())
        _from = int(to - (options['days'] * 60 * 60 * 24))

        batch_seconds = Intervals.dict[options['interval']] * options['batch_size']

        for batch in self.batch_time(_from, to, batch_seconds):

            candlesticks = self.gate_io_request_candlesticks(
                currency_pair=options['pair'],
                interval=Intervals.dict[options['interval']],
                _from=batch[0],
                to=batch[1]
            )

            items = []

            for index, candlestick in candlesticks.iterrows():

                dt = datetime.fromtimestamp(int(candlestick['date']), tz=timezone.utc)

                try:
                    obj = Candlestick.objects.get(
                        pair=options['pair'],
                        interval=options['interval'],
                        datetime=dt
                    )
                except Candlestick.DoesNotExist:
                    items.append(Candlestick(
                        open=candlestick['open'],
                        close=candlestick['close'],
                        high=candlestick['high'],
                        low=candlestick['low'],
                        volume=candlestick['volume'],
                        pair=options['pair'],
                        interval=options['interval'],
                        datetime=dt
                    ))

            Candlestick.objects.bulk_create(items)

            self.stdout.write(f"Getting data from {batch[0]} to {batch[1]} done")

    def batch_time(self, _from: int, to: int, batch: int) -> List:

        array = []

        count = math.ceil((to - _from) / batch)

        for i in range(count):
            begin = i * batch + _from
            end = (i + 1) * batch + _from

            if end > to:
                end = to

            array.append([begin, end])

        return array

    def gate_io_request_candlesticks(self, currency_pair, interval, _from, to) -> DataFrame:

        params = dict(
            type='tvkline',
            symbol=currency_pair.lower(),
            to = to,
            interval = interval
        )

        params['from'] = _from

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

        response = requests.get('https://www.gate.io/json_svr/query/', params, timeout=10, headers=headers)

        response.raise_for_status()

        df = pd.read_csv(io.StringIO(response.text))

        df['date'] = df['date'] / 1000

        return df

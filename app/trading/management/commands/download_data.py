import time
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from gate_api import ApiClient, SpotApi, Configuration

from app.trading.enums.intervals import Intervals
from app.trading.models import Candlestick
from app.service.gate_io_api import api_client
from typing import List
import math

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

            candlesticks = spot_api.list_candlesticks(
                currency_pair=options['pair'],
                interval=options['interval'],
                _from=batch[0],
                to=batch[1]
            )

            items = []

            for candlestick in candlesticks:

                dt = datetime.fromtimestamp(int(candlestick[0]), tz=timezone.utc)

                try:
                    obj = Candlestick.objects.get(
                        pair=options['pair'],
                        interval=options['interval'],
                        datetime=dt
                    )
                except Candlestick.DoesNotExist:
                    items.append(Candlestick(
                        open=candlestick[5],
                        close=candlestick[2],
                        high=candlestick[3],
                        low=candlestick[4],
                        volume=candlestick[1],
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

import time
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from gate_api import ApiClient, SpotApi, Configuration

from trading_bot.trading.enums.intervals import Intervals
from trading_bot.trading.models import Candlestick, Exchanges
from trading_bot.service.gate_io_api import api_client
from typing import List
import math
import requests
import pandas as pd
import io
from pandas import DataFrame
import json
import numpy as np

# python3 manage.py download_data BTC_USDT 100 1m binance

class Command(BaseCommand):
    help = 'Downloading cryptocurrency exchange rate'

    batch_size = 950

    def add_arguments(self, parser):
        parser.add_argument('pair', type=str, help='Cryptocurrency pair')
        parser.add_argument('days', type=int, help='Number of days')
        parser.add_argument('interval', type=str, help='Interval')
        parser.add_argument('exchange', type=str, help='Exchange')

        parser.add_argument(
            '--batch-size',
            default=950,
            type=int,
            help='Batch size',
        )

    def handle(self, *args, **options):

        self.batch_size = int(options['batch_size'])

        to = int(time.time())
        _from = int(to - (options['days'] * 60 * 60 * 24))

        batch_seconds = Intervals.dict[options['interval']] * options['batch_size']

        exchange = Exchanges[options['exchange'].upper()]

        for batch in self.batch_time(_from, to, batch_seconds):

            candlesticks = self.get_candlesticks(
                exchange=exchange, pair=options['pair'],
                interval=options['interval'], _from=batch[0], to=batch[1])

            items_for_create = []
            items_for_update = []

            for index, candlestick in candlesticks.iterrows():

                dt = datetime.fromtimestamp(int(candlestick['date']), tz=timezone.utc)

                try:
                    obj = Candlestick.objects.get(
                        pair=options['pair'],
                        interval=options['interval'],
                        datetime=dt,
                        exchange=exchange
                    )

                    if obj.open != candlestick['open'] or obj.close != candlestick['close'] or \
                        obj.high != candlestick['high'] or obj.low != candlestick['low'] or \
                        obj.volume != candlestick['volume']:

                        obj.open = candlestick['open']
                        obj.close = candlestick['close']
                        obj.high = candlestick['high']
                        obj.low = candlestick['low']
                        obj.volume = candlestick['volume']

                        items_for_update.append(obj)

                except Candlestick.DoesNotExist:
                    items_for_create.append(Candlestick(
                        open=candlestick['open'],
                        close=candlestick['close'],
                        high=candlestick['high'],
                        low=candlestick['low'],
                        volume=candlestick['volume'],
                        pair=options['pair'],
                        interval=options['interval'],
                        datetime=dt,
                        exchange=exchange
                    ))

            Candlestick.objects.bulk_create(items_for_create)
            Candlestick.objects.bulk_update(items_for_update, ['open', 'close', 'high', 'low', 'volume'])

            self.stdout.write(f"Getting data from {batch[0]} to {batch[1]} done. Created items {len(items_for_create)}. Updated items {len(items_for_update)} ")

    def get_candlesticks(self, exchange: str, pair: str, interval: str, _from: int, to: int) -> DataFrame:

        if exchange == Exchanges.GATE_IO:
            candlesticks = self.gate_io_request_candlesticks(
                currency_pair=pair,
                interval=Intervals.dict[interval],
                _from=_from,
                to=to
            )
        elif exchange == Exchanges.BINANCE:
            candlesticks = self.binance_request_candlesticks(
                currency_pair=pair,
                interval=interval,
                _from=_from,
                to=to
            )
        else:
            raise Exception(f'Exchange {exchange} not found')

        candlesticks = candlesticks.astype({
            'date': np.int, 'open': np.float, 'close': np.float, 'high': np.float, 'low': np.float, 'volume': np.float
        })

        return candlesticks

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

    def binance_request_candlesticks(self, currency_pair: str, interval: str, _from: int, to: int):

        currency_pair = currency_pair.replace('_', '').upper()

        params = dict(
            startTime=_from * 1000,
            endTime=to * 1000,
            limit=self.batch_size + 1,
            symbol=currency_pair,
            interval=interval
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

        response = requests.get('https://www.binance.com/api/v3/uiKlines', params, timeout=10, headers=headers)

        response.raise_for_status()

        json_dict = json.loads(response.text)

        df = pd.DataFrame.from_dict(json_dict)\
            .rename(columns={0: "date", 1: "open", 2: "high", 3: "low", 4: "close", 5: "volume"})

        df = df.drop(df.columns[[7, 8, 9, 10, 11]], axis = 1)

        df['date'] = df['date'] / 1000

        return df
from django.core.management.base import BaseCommand

from trading_bot.trading.enums.intervals import Intervals
from trading_bot.trading.helpers.try_timeout import try_timeout
from trading_bot.trading.models import Candlestick, OrderBook
from typing import List
from django.core.management import call_command
import pandas as pd
import importlib
import humps
import time
from gate_api import ApiClient, SpotApi, Configuration
from trading_bot.service.gate_io_api import api_client
from gate_api.exceptions import ApiException, GateApiException
from datetime import datetime, timezone
from trading_bot.service.binance_api import client

class Command(BaseCommand):
    help = 'Parse order book'

    def add_arguments(self, parser):
        parser.add_argument('pair', type=str, help='Pair')
        parser.add_argument('exchange', type=str, help='Exchange')

        # Named (optional) arguments
        parser.add_argument(
            '--daemon',
            default=False,
            action='store_true',
            help='Run as daemon',
        )

    def handle(self, *args, **options):
        currency_pair = options['pair'].upper()
        exchange = options['exchange'].lower()
        daemon = options['daemon']

        while True:

            if exchange == 'gate_io':
                dt, asks, bids = self.get_gate_io_orderbook(currency_pair)
            else:
                dt, asks, bids = self.get_binance_orderbook(currency_pair)

            self.stdout.write(f"Orderbook data received {currency_pair} {dt} {exchange}")

            bids = round(bids, 6)
            asks = round(asks, 6)

            order = OrderBook(pair=currency_pair, datetime=dt, asks=asks, bids=bids, exchange=exchange)
            order.save()

            if daemon:
                time.sleep(60 - dt.second)
            else:
                return

    def get_gate_io_orderbook(self, currency_pair: str):

        api_instance = SpotApi(api_client)
        interval = '1000000000'
        limit = 1

        api_response = try_timeout(lambda: api_instance.list_order_book(currency_pair, interval=interval, limit=limit), 1000, 5)

        asks = api_response.asks[0][1]
        bids = api_response.bids[0][1]

        update = float(api_response.update) / 1000

        dt = datetime.fromtimestamp(update, tz=timezone.utc)

        return dt, float(asks), float(bids)

    def get_binance_orderbook(self, currency_pair: str):

        currency_pair = currency_pair.replace("_", "")

        result = try_timeout(lambda: client.get_order_book(symbol=currency_pair, limit=1000), 1000, 5)

        bids = 0
        asks = 0

        for i in result['bids']:
            bids += float(i[1])

        for i in result['asks']:
            asks += float(i[1])

        dt = datetime.fromtimestamp(time.time(), tz=timezone.utc)

        return dt, asks, bids
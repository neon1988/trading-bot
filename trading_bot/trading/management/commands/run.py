import time
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from gate_api import ApiClient, SpotApi, Configuration, DeliveryApi, FuturesApi, MarginApi, OptionsApi

from trading_bot.service.binance_api import client
from trading_bot.trading.enums.intervals import Intervals
from trading_bot.trading.exchanges.gate_io_exchange import GateIoExchange
from trading_bot.trading.models import Candlestick
from trading_bot.service.gate_io_api import api_client
from typing import List
import time
from enum import Enum
from datetime import datetime
from gate_api.exceptions import ApiException, GateApiException


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        result = client.get_order_book(symbol='BTCUSDT', limit=1000)

        bids = 0
        asks = 0

        for i in result['bids']:
            bids += float(i[1])

        for i in result['asks']:
            asks += float(i[1])

        print(bids)
        print(asks)

        print(bids / asks)

        #print(result['asks'])


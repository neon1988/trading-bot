import time
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from gate_api import ApiClient, SpotApi, Configuration

from trading_bot.trading.enums.intervals import Intervals
from trading_bot.trading.exchanges.gate_io_exchange import GateIoExchange
from trading_bot.trading.models import Candlestick
from trading_bot.service.gate_io_api import api_client
from typing import List
import time
from enum import Enum
from datetime import datetime


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        text = int(datetime.now().timestamp() * 1000000)



        string = "t-freeCodeCamp"
        print(string[2:])

        #print(exchange.create_trade('AVAX_USDT', 10, 0.1, 'buy', text=text))

        print(exchange.get_trade(150427353834, 'AVAX_USDT').text)


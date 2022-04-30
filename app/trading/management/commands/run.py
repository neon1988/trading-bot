import time
from datetime import datetime, timezone

from django.core.management.base import BaseCommand
from gate_api import ApiClient, SpotApi, Configuration

from app.trading.enums.intervals import Intervals
from app.trading.exchanges.gate_io_exchange import GateIoExchange
from app.trading.models import Candlestick
from app.service.gate_io_api import api_client
from typing import List
import time
from enum import Enum


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):

        exchange = GateIoExchange()
        print(exchange.get_trade(149021356969, 'ATOM_USDT'))


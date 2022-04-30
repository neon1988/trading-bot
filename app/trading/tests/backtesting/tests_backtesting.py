from io import StringIO

from django.core import management
from django.test import TestCase

from app.trading.factories import CandlestickFactory
from app.trading.models import Candlestick
import factory
import pandas_ta as ta

class BacktestingTests(TestCase):

    def test(self):
        args = ['my_strategy', 'BTC_USDT', '30', '5m']

        candlesticks = CandlestickFactory.create_batch(50,
                                                       pair="BTC_USDT",
                                                       interval="5m",
                                                       datetime=factory.Faker('date_time_between', start_date='-1d'))

        out = StringIO()

        management.call_command('backtesting', *args, stdout=out)

        self.assertIn('Testing of the strategy is completed', out.getvalue())

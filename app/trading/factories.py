import factory
from . import models
import random


class CandlestickFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Candlestick

    pair = 'BTC_USDT'
    interval = '5m'
    close = factory.Sequence(lambda n: round(random.uniform(10, 75.5), 2))
    open = factory.Sequence(lambda n: round(random.uniform(10, 75.5), 2))
    high = factory.Sequence(lambda n: round(random.uniform(10, 75.5), 2))
    low = factory.Sequence(lambda n: round(random.uniform(10, 75.5), 2))
    datetime = factory.Faker('date_time_between', start_date='-30d')
    volume = factory.Sequence(lambda n: round(random.uniform(100, 1000), 2))

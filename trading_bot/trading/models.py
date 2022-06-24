from django.db import models
from django.utils.translation import gettext_lazy as _

TIMEFRAMES = [
    (0, '1m'),
    (1, '5m'),
    (2, '15m'),
    (3, '30m'),
    (4, '1h'),
    (5, '4h'),
    (6, '1d'),
    (7, '1w')
]

class Exchanges(models.TextChoices):
    GATE_IO = 0, _('gate_io')
    BINANCE = 1, _('binance')

class Candlestick(models.Model):
    pair = models.CharField(
        max_length=20
    )
    interval = models.CharField(
        max_length=3,
        choices=TIMEFRAMES
    )
    close = models.FloatField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    datetime = models.DateTimeField('datetime')
    volume = models.FloatField()
    exchange = models.CharField(
        max_length=1,
        choices=Exchanges.choices
    )

    class Meta:
        unique_together = ['pair', 'interval', 'datetime', 'exchange']

class OrderBook(models.Model):
    pair = models.CharField(max_length=20)
    interval = models.CharField(
        max_length=3,
        choices=TIMEFRAMES
    )
    exchange = models.CharField(max_length=10, default='gate_io')
    datetime = models.DateTimeField('datetime')
    asks = models.FloatField()
    bids = models.FloatField()

    class Meta:
        unique_together = ['pair', 'datetime']
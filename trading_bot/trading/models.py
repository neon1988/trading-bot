from django.db import models

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

    class Meta:
        unique_together = ['pair', 'interval', 'datetime']

class OrderBook(models.Model):
    pair = models.CharField(max_length=20)
    exchange = models.CharField(max_length=10, default='gate_io')
    datetime = models.DateTimeField('datetime')
    asks = models.FloatField()
    bids = models.FloatField()

    class Meta:
        unique_together = ['pair', 'datetime']
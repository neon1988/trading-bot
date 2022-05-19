from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from django.conf import settings

client = Client(
    settings.EXCHANGES['binance']['key'],
    settings.EXCHANGES['binance']['secret']
)

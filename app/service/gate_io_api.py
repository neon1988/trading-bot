import gate_api
from django.conf import settings
from gate_api import ApiClient, SpotApi, Configuration

configuration = Configuration(
    host=settings.EXCHANGES['gate_io']['host'],
    secret=settings.EXCHANGES['gate_io']['secret'],
    key=settings.EXCHANGES['gate_io']['key']
)

api_client = ApiClient(configuration)

from trading_bot.service.gate_io_api import api_client
from gate_api import ApiClient, SpotApi, Configuration
import gate_api
from gate_api.exceptions import GateApiException
import datetime
from typing import Callable

from trading_bot.trading.exchanges.exchange import Exchange
from trading_bot.trading.exchanges.trade import Trade


class GateIoExchange(Exchange):
    fee = 0.2
    min_create_trade_sum = 1

    def create_trade(self, currency_pair: str, price: float, amount: float, side: str,
                     time: int = None, status: str = 'open', text: str = '') -> int:
        price = price + (
                price * self.fee / 100)  # append small percentage so that the transaction is executed instantly

        if price * amount < self.min_create_trade_sum:
            raise Exception('The minimum is 1')

        spot_api = SpotApi(api_client)

        order = gate_api.Order(account="spot", currency_pair=currency_pair, price=price, amount=amount, side=side,
                               status=status, text=f't-{text}')

        api_response = spot_api.create_order(order)

        return int(api_response.id)

    def get_currency_available_balance(self, currency: str) -> float:
        spot_api = SpotApi(api_client)
        api_response = spot_api.list_spot_accounts(currency=currency.upper())

        for item in iter(api_response):
            if item.currency == currency:
                return float(item.available)

        raise Exception('Currency balance not found')

    def get_trade(self, id: int, currency_pair: str) -> Trade:
        spot_api = SpotApi(api_client)
        api_response = self.try_timeout(lambda: spot_api.get_order(id, currency_pair), 3, 60, GateApiException)
        api_response.text = api_response.text[2:]
        return Trade().from_dict(api_response.to_dict())

    def cancel_trade(self, id: int, currency_pair: str) -> bool:
        spot_api = SpotApi(api_client)
        api_response = spot_api.cancel_order(id, currency_pair)
        return True

    def close_trade(self, id: int, time: int = None) -> bool:
        return True

    def list_candlesticks(self, currency_pair: str, interval: str, _from: int = None, to: int = None, limit: int = 999):
        spot_api = SpotApi(api_client)

        candlesticks = spot_api.list_candlesticks(
            currency_pair=currency_pair,
            interval=interval,
            _from=_from,
            to=to,
            limit=limit
        )

        return candlesticks

    def list_tickers(self, currency_pair: str):
        spot_api = SpotApi(api_client)

        api_response = spot_api.list_tickers(currency_pair=currency_pair)

        return api_response

    def get_latest_price(self, currency_pair: str) -> float:
        spot_api = SpotApi(api_client)

        api_response = spot_api.list_tickers(currency_pair=currency_pair)

        return float(next(iter(api_response)).last)

    def is_trade_closed(self, id: int, currency_pair: str) -> bool:
        trade = self.get_trade(id, currency_pair)

        if trade.status == 'open':
            return False
        if trade.status == 'closed':
            return True

    def list_orders(self, currency_pair: str, status: str = "open", limit: int = 100, _from: datetime = None,
                    to: datetime = None,
                    side: str = None) -> list:
        spot_api = SpotApi(api_client)

        if _from is not None:
            _from = int(_from.timestamp())

        if to is not None:
            to = int(to.timestamp())

        if status == 'closed':
            status = 'finished'

        api_response = spot_api.list_orders(currency_pair, status, limit=limit, account="spot",
                                            _from=_from, to=to, side=side)

        return list(map(lambda x: Trade().from_dict(x.to_dict()), api_response))

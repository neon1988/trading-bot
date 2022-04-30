from app.trading.exchanges.trade import Trade


class ExchangeInterface:

    def create_trade(self, currency_pair: str, price: float, amount: float, side: str,
                          time: int = None, status: str = 'open') -> int:
        """Creating a trade"""
        pass

    def get_currency_available_balance(self, currency: str) -> float:
        """Get the balance of the specified currency"""
        pass

    def cancel_trade(self, id: int, currency_pair: str):
        """Cancel a trade"""
        pass

    def get_trade(self, id: int, currency_pair: str) -> Trade:
        """Get trade info"""
        pass


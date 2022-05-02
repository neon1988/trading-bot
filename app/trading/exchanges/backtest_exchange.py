import time as current_time

from app.trading.exchanges.exchange import Exchange
from app.trading.exchanges.exchange_interface import ExchangeInterface
import pandas as pd
import numpy as np
from pandas import DataFrame
import datetime

from app.trading.exchanges.trade import Trade


class BacktestExchange(Exchange):
    fee = 0.2
    start_balance = 1000
    balance_currency = 'USDT'

    def __init__(self, start_balance=1000, balance_currency='USDT'):
        self.trades = pd.DataFrame(None,
                                   columns=['currency_pair', 'price', 'amount', 'side', 'fee', 'fee_currency',
                                            'create_time', 'update_time', 'fill_price', 'status',
                                            'id', 'text']).astype({
            'currency_pair': str, 'price': np.float32, 'amount': np.float32, 'side': str, 'fee': np.float32,
            'fee_currency': str, 'create_time': 'datetime64[ns]', 'update_time': 'datetime64[ns]', 'fill_price': np.float32,
            'id': np.int32, 'status': str, 'text': str
        })

        self.start_balance = start_balance
        self.balance_currency = balance_currency

        self.balances = pd.DataFrame(None, columns=['currency', 'balance']).astype({
            'currency': str, 'balance': np.float32
        })

        self.set_balance(self.balance_currency, self.start_balance)

    def set_balance(self, currency: str, balance: float):
        currency = currency.upper()

        rows = self.balances[self.balances['currency'] == currency]

        if len(rows) > 0:
            row = rows.iloc[0]
            self.balances.at[row.name, 'balance'] = float(balance)
        else:
            self.balances.loc[self.balances.shape[0]] = {
                'currency': currency,
                'balance': balance
            }

        return True

    def get_balance(self, currency: str) -> float:
        currency = currency.upper()
        rows = self.balances[self.balances['currency'] == currency]

        if len(rows) < 1:
            return 0

        row = rows.iloc[0]

        return row['balance']

    def refresh_balance(self, currency: str) -> bool:
        currency = currency.upper()
        self.set_balance(currency, self.get_currency_available_balance(currency))
        return True

    def refresh_balance_for_pair(self, currency_pair: str) -> bool:
        currency1, currency2 = currency_pair.upper().split("_")
        self.refresh_balance(currency1)
        self.refresh_balance(currency2)
        return True

    def create_trade(self, currency_pair: str, price: float, amount: float, side: str,
                     time: datetime = None, status: str = 'open', text: str = '') -> int:

        currency_pair = currency_pair.upper()

        currency1, currency2 = currency_pair.split("_")

        fee = 0
        fill_price = 0

        if status == 'closed':
            fill_price = price * amount

            if side == 'buy':
                fee = amount * self.fee / 100
            else:
                fee = fill_price * self.fee / 100

        if side == 'buy':
            fee_currency = currency1
        else:
            fee_currency = currency2

        sum = price * amount

        if side == 'buy':
            balance = self.get_currency_available_balance(currency2)

            if balance < sum:
                raise Exception(
                    f'Not enough balance to open a trade. Balance {currency2} {balance}. Trade sum {sum}')
        else:
            balance = self.get_currency_available_balance(currency1)

            if balance < amount:
                raise Exception(
                    f'Not enough balance to open a trade. Balance {currency1} {balance}. Trade sum {sum}')

        id = int(current_time.time_ns())

        row = {
            'id': id,
            'currency_pair': currency_pair,
            'price': price,
            'amount': amount,
            'side': side,
            'fee': fee,
            'fee_currency': fee_currency,
            'create_time': time,
            'update_time': time,
            'fill_price': fill_price,
            'status': status,
            'text': text
        }

        self.trades.loc[self.trades.shape[0]] = row

        self.refresh_balance_for_pair(currency_pair)

        return id

    def get_currency_available_balance(self, currency: str) -> float:

        currency = currency.upper()

        closed_trades = self.get_closed_trades()

        if currency == self.balance_currency:

            buy_trades = closed_trades[closed_trades['side'] == 'buy']
            sell_trades = closed_trades[closed_trades['side'] == 'sell']

            open_trades = self.get_open_trades()

            open_trades = open_trades[open_trades['side'] == 'buy']

            return self.start_balance + sell_trades['fill_price'].sum() - buy_trades['fill_price'].sum() - \
                   closed_trades[closed_trades['fee_currency'] == self.balance_currency]['fee'].sum() - \
                   (open_trades['amount'] * open_trades['price']).sum()
        else:

            trades = closed_trades

            buy_trades = trades[
                (trades['currency_pair'] == f'{currency}_{self.balance_currency}') & (trades['side'] == 'buy')]
            sell_trades = trades[
                (trades['currency_pair'] == f'{currency}_{self.balance_currency}') & (trades['side'] == 'sell')]

            open_trades = self.get_open_trades()

            open_trades = open_trades[open_trades['side'] == 'sell']

            return buy_trades['amount'].sum() - buy_trades['fee'].sum() - \
                   sell_trades['amount'].sum() - open_trades['amount'].sum()

    def get_trade(self, id: int, currency_pair: str):
        row = self.trades[self.trades['id'] == id].to_dict('records')
        dict = next(iter(row))
        return Trade().from_dict(dict)

    def cancel_trade(self, id: int, currency_pair: str) -> bool:

        id = int(id)

        if self.is_trade_closed(id, currency_pair):
            return False

        trade = self.get_trade(id, currency_pair)

        self.trades.drop(self.trades.index[self.trades['id'] == id], inplace=True)

        self.refresh_balance_for_pair(currency_pair)

        return True

    def close_trade(self, id: int, currency_pair: str, time: datetime = None) -> bool:
        trade = self.get_trade(id, currency_pair)

        fill_price = trade.price * trade.amount

        if trade.side == 'buy':
            fee = trade.amount * self.fee / 100
        else:
            fee = fill_price * self.fee / 100

        row = self.trades[self.trades['id'] == id].iloc[0]

        self.trades.at[row.name, 'fee'] = float(fee)
        self.trades.at[row.name, 'fill_price'] = float(fill_price)
        self.trades.at[row.name, 'status'] = 'closed'
        self.trades.at[row.name, 'update_time'] = time

        self.refresh_balance_for_pair(currency_pair)

        return True

    def is_trade_closed(self, id: int, currency_pair: str) -> bool:
        trade = self.get_trade(id, currency_pair)

        if trade.is_closed():
            return True
        else:
            return False

    def get_closed_trades(self) -> DataFrame:
        return self.trades[self.trades['status'] == 'closed']

    def get_open_trades(self) -> DataFrame:
        return self.trades[self.trades['status'] == 'open']

    def get_closed_trades_count(self) -> int:
        return len(self.get_closed_trades())

    def get_open_trades_count(self) -> int:
        return len(self.get_open_trades())

    def get_pairs(self):

        df_pairs = self.get_closed_trades()['currency_pair'].drop_duplicates()

        pairs = []

        for pair in df_pairs:
            pair = pair.upper()

            currency1, currency2 = pair.split("_")

            pairs.append(currency1)
            pairs.append(currency2)

        pairs = list(set(pairs))

        return pairs

    def list_orders(self, currency_pair: str, status: str = "open", limit: int = 100, _from: datetime = None, to: datetime = None,
                    side: str = None) -> list:

        df = self.trades[(self.trades['currency_pair'] == currency_pair) &
                         (self.trades['status'] == status)]

        if side is not None:
            df = df[df['side'] == side]

        if _from is not None:
            df = df[df['create_time'] >= _from]

        if to is not None:
            df = df[df['create_time'] <= to]

        df = df.tail(limit)

        return list(map(lambda x: Trade().from_dict(x), df.to_dict('records')))



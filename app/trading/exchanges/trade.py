import numpy as np


class Trade:

    def __init__(self):
        self.update_time = None
        self.create_time = None
        self.fill_price = None
        self.fee_currency = None
        self.fee = None
        self.currency_pair = None
        self.side = None
        self.status = None
        self.price = None
        self.amount = None
        self.id = None

    def from_dict(self, item: dict):

        self.id = int(item['id'])
        self.amount = float(item['amount'])
        self.price = float(item['price'])
        self.status = str(item['status'])
        self.side = str(item['side'])
        self.currency_pair = str(item['currency_pair'])
        self.fee = float(item['fee'])
        self.fee_currency = str(item['fee_currency'])
        self.fill_price = float(item['fill_price'])
        self.create_time = item['create_time']
        self.update_time = item['update_time']

        return self

    def is_closed(self) -> bool:
        if self.status == 'open':
            return False
        if self.status == 'closed':
            return True

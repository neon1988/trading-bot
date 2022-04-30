import unittest

from app.trading.exchanges.exchange import Exchange
import datetime


class GateIoExchangeTest(unittest.TestCase):

    def test_try_timeout(self):
        exchange = Exchange()

        with self.assertRaises(ZeroDivisionError):
            exchange.try_timeout(closure=self.broken_function, max_try_count=3, timeout_seconds=0)

        result = exchange.try_timeout(closure=self.dont_throw_exception_function, max_try_count=3, timeout_seconds=0)

        self.assertEquals(1, result)

    def broken_function(self):
        return (1 / 0)

    def dont_throw_exception_function(self):
        return 1
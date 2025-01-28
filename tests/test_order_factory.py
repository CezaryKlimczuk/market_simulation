import unittest
from unittest.mock import MagicMock
from datetime import datetime
from order_factory import OrderFactory
from order import Order, OrderSide, OrderType
from instrument import Instrument
from orderbook import OrderBook

class TestOrderFactory(unittest.TestCase):

    def setUp(self):
        self.instrument = Instrument("TestInstrument", 0.01)
        self.orderbook = OrderBook(self.instrument)
        self.arrivals_rate = 1.0
        self.hazard_rate = 1.0
        self.buy_ratio = 0.5
        self.limit_order_ratio = 0.5
        self.min_consideration = 1
        self.max_amount = 100
        self.max_halfspread = 0.05
        self.static_order_type = None
        self.static_midprice = None

        self.order_factory = OrderFactory(
            instrument=self.instrument,
            orderbook=self.orderbook,
            arrivals_rate=self.arrivals_rate,
            hazard_rate=self.hazard_rate,
            buy_ratio=self.buy_ratio,
            limit_order_ratio=self.limit_order_ratio,
            min_consideration=self.min_consideration,
            max_amount=self.max_amount,
            max_halfspread=self.max_halfspread,
            static_order_type=self.static_order_type,
            static_midprice=self.static_midprice
        )

    def test_generate_counterpart_id(self):
        counterpart_id = self.order_factory._generate_counterpart_id()
        self.assertTrue(1000 <= counterpart_id <= 1010)

    def test_generate_interval_time(self):
        interval_time = self.order_factory._generate_interval_time()
        self.assertGreater(interval_time, 0)

    def test_generate_order_lifetime(self):
        order_lifetime = self.order_factory._generate_order_lifetime()
        self.assertGreater(order_lifetime, 0)

    def test_generate_order_side(self):
        order_side = self.order_factory._generate_order_side()
        self.assertIn(order_side, [OrderSide.BUY, OrderSide.SELL])

    def test_generate_order_type(self):
        order_type = self.order_factory._genereate_order_type()
        self.assertIn(order_type, [OrderType.LIMIT, OrderType.MARKET])

    def test_generate_order_amount(self):
        order_amount = self.order_factory._generate_order_amount()
        self.assertTrue(1 <= order_amount <= self.max_amount)

    def test_generate_order_price(self):
        self.orderbook.get_midprice = MagicMock(return_value=100.0)
        order_price = self.order_factory._generate_order_price(50, OrderSide.BUY)
        self.assertGreater(order_price, 0)

    def test_generate_order(self):
        previous_order_ts = datetime.now()
        new_order = self.order_factory.generate_order(previous_order_ts)
        self.assertIsInstance(new_order, Order)
        self.assertGreater(new_order.amount, 0)
        self.assertIn(new_order.side, [OrderSide.BUY, OrderSide.SELL])
        self.assertIn(new_order.order_type, [OrderType.LIMIT, OrderType.MARKET])
        self.assertLess(new_order.timestamp, new_order.cancellation_timestamp)

    def test_generate_orders(self):
        start_time = datetime.now()
        n_orders = 5
        orders = self.order_factory.generate_orders(start_time, n_orders)
        self.assertEqual(len(orders), n_orders)
        for order in orders:
            self.assertIsInstance(order, Order)
            self.assertGreater(order.amount, 0)
            self.assertIn(order.side, [OrderSide.BUY, OrderSide.SELL])
            self.assertIn(order.order_type, [OrderType.LIMIT, OrderType.MARKET])
            self.assertLess(order.timestamp, order.cancellation_timestamp)

    def test_static_order_type(self):
        self.order_factory.static_order_type = OrderType.MARKET
        new_order = self.order_factory.generate_order(datetime.now())
        self.assertEqual(new_order.order_type, OrderType.MARKET)

    def test_static_midprice(self):
        self.order_factory.static_midprice = 100.0
        order_price = self.order_factory._generate_order_price(50, OrderSide.BUY)
        self.assertEqual(order_price, 100.0 - self.order_factory.max_halfspread * 50 / self.order_factory.max_amount)

    def test_generate_order_amount(self):
        order_amount = self.order_factory._generate_order_amount()
        self.assertTrue(1 <= order_amount <= self.max_amount)

if __name__ == '__main__':
    unittest.main()
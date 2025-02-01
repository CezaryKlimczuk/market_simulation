import math
from datetime import datetime, timedelta
from random import expovariate, random, uniform, randint

from orderbook import OrderBook
from instrument import Instrument
from order import Order, OrderSide, OrderType


def _round_up(value: float, precision: float):
    """
    Rounds up the `value` to the nearest multiple of `precision`
    """
    return float(round(value / precision) * precision)


class OrderFactory:
    """
    Generates orders for a given instrument at Poisson-distributed intervals.
    """

    def __init__(
        self,
        instrument: Instrument,
        orderbook: OrderBook, # The Orderbook object of associated Instrument
        arrivals_rate: float,  # Orders per second
        hazard_rate: float, # Cancellation rate per second
        buy_ratio: float,
        limit_order_ratio: float,
        min_consideration: int,
        max_amount: int,
        max_halfspread: float,
        static_midprice: float | None = None
    ) -> None:
        self.instrument = instrument
        self.orderbook = orderbook
        self.arrivals_rate = arrivals_rate
        self.hazard_rate = hazard_rate
        self.buy_ratio = buy_ratio
        self.limit_order_ratio = limit_order_ratio
        self.min_consideration = min_consideration
        self.max_amount = max_amount
        self.max_halfspread = max_halfspread
        self.static_order_type = static_order_type
        self.static_midprice = static_midprice

    def _generate_counterpart_id(self) -> int:
        """
        Draws a random counterpart id for a given order.
        """
        return randint(1000, 1010)

    def _generate_interval_time(self) -> float:
        """
        Draws interarrival time of the order.
        
        Currently drawn from an exponential distribution.
        """
        return expovariate(lambd=self.arrivals_rate)

    def _generate_order_lifetime(self) -> float:
        """
        Draws lifetime of the order.
        
        Currently drawn from an exponential distribution.
        """
        return expovariate(lambd=self.hazard_rate)

    def _generate_order_side(self) -> float:
        """
        Draws randomly a BUY or a SELL side based on the `buy_ratio` attribute.
        """
        return OrderSide.BUY if random() < self.buy_ratio else OrderSide.SELL

    def _genereate_order_type(self) -> OrderType:
        """
        Draws randomly a LIMIT or a MARKET type based on the `limit_order_ratio` attribute.
        """
        return OrderType.LIMIT if random() < self.limit_order_ratio else OrderType.MARKET

    def _generate_order_amount(self) -> int:
        """
        Draws the order amount.

        Currently drawn from the exponential distribution and
        bounded by the `max_amount` attribute.
        """
        return min(math.ceil(expovariate(5 / self.max_amount)), self.max_amount)

    def _generate_order_price(self, amount: int, side: OrderSide) -> float:
        """
        Draws the order price for a LIMIT order.
        """
        # Fetching the midprice and generating the limit price
        midprice = self.static_midprice if self.static_midprice else self.orderbook.get_midprice()

        # The amount of an order influences how far from the mid the price can be
        max_offset = self.max_halfspread * amount / self.max_amount
        midprice_offset = uniform(0, max_offset)

        # Ensuring the limit order adds liquidity to the book 
        midprice_offset = midprice_offset if side == OrderSide.SELL else -midprice_offset

        # Rounding the midprice to the nearest tick size
        limit_price = _round_up(midprice + midprice_offset, self.instrument.min_tick_size)
        return limit_price

    def generate_order(self, previous_order_ts: datetime) -> Order:
        """
        Generates a single instance of Order class
        """
        order_counterpart_id = self._generate_counterpart_id()
        order_side = self._generate_order_side()
        order_type = self._genereate_order_type()

        # Generating the price if the order type is LIMIT
        if order_type == OrderType.LIMIT:
            order_price = self._generate_order_price(order_amount, order_side)
        else:
            order_price = None

        # Generating the order timestamp based on previous order and a random interarrival time
        order_interarrival_time = self._generate_interval_time()
        order_timestamp = previous_order_ts + timedelta(seconds=order_interarrival_time)

        # Generating the order cancellation timestamp based on the order lifetime
        order_lifetime = self._generate_order_lifetime()
        order_cancellation_timestamp = order_timestamp + timedelta(seconds=order_lifetime)

        new_order = Order(
            timestamp=order_timestamp,
            cancellation_timestamp=order_cancellation_timestamp,
            counterpart_id=order_counterpart_id,
            instrument=self.instrument,
            order_type=order_type,
            side=order_side,
            amount=order_amount,
            price=order_price
        )

        return new_order

    def generate_orders(self, start_time: datetime, n_orders: int) -> list[Order]:
        """
        Generates a list of Order instances with assigned timestamps and ids.
        """
        previous_order_time = start_time
        order_list: list[Order] = []

        for _ in range(n_orders):
            new_order = self.generate_order(previous_order_ts=previous_order_time)
            order_list.append(new_order)
            previous_order_time = new_order.timestamp

        return order_list
import numpy as np

import math
from datetime import datetime, timedelta
from random import expovariate, random, uniform, randint

from orderbook import OrderBook
from instrument import Instrument
from order import Order, OrderSide, OrderType


def _round_up(x, a):
    # Rounds x up to the nearest multiple of a
    return float(np.ceil(x / a) * a)


class OrderFactory:
    """
    Generates orders for a given instrument at Poisson-distributed intervals.
    """

    def __init__(
        self,
        instrument: Instrument,
        orderbook: OrderBook,
        arrivals_rate: float,  # Orders per second
        buy_ratio: float,
        limit_order_ratio: float,
        min_consideration: int,
        max_amount: int,
        max_halfspread: float,
        static_order_type: OrderType | None = None,
        static_midprice: float | None = None
    ) -> None:
        self.instrument = instrument
        self.orderbook = orderbook
        self.arrivals_rate = arrivals_rate
        self.buy_ratio = buy_ratio
        self.limit_order_ratio = limit_order_ratio
        self.min_consideration = min_consideration
        self.max_amount = max_amount
        self.max_halfspread = max_halfspread
        self.static_order_type = static_order_type
        self.static_midprice = static_midprice

    def _generate_counterpart_id(self) -> int:
        # Draws a random counterpart id
        return randint(1000, 1010)

    def _generate_interval_time(self) -> float:
        # Draws interarrival time from an exponential distribution
        return expovariate(lambd=self.arrivals_rate)

    def _generate_order_side(self) -> float:
        # Randomly chooses BUY or SELL
        return OrderSide.BUY if random() < self.buy_ratio else OrderSide.SELL

    def _genereate_order_type(self) -> OrderType:
        # Randomly chooses LIMIT or MARKET
        return OrderType.LIMIT if random() < self.limit_order_ratio else OrderType.MARKET

    def _generate_order_amount(self) -> int:
        # Generates an amount bounded by max_amount
        return min(math.ceil(expovariate(5 / self.max_amount)), self.max_amount)

    def _generate_order_price(self, amount: int, side: OrderSide) -> float:
        # Creates a limit price offset scaled by order size
        midprice_offset = uniform(0, self.max_halfspread * amount / self.max_amount)
        midprice_offset = midprice_offset if side == OrderSide.SELL else -midprice_offset
        midprice = self.static_midprice if self.static_midprice else self.orderbook.get_midprice()
        limit_price = _round_up(midprice + midprice_offset, self.instrument.min_tick_size)
        return limit_price

    def generate_order(self) -> tuple[Order, float]:
        # Creates a single order and its interarrival time
        order_counterpart_id = self._generate_counterpart_id()
        order_interarrival_time = self._generate_interval_time()
        order_side = self._generate_order_side()
        order_amount = self._generate_order_amount()

        # Assigining static order type, or drawing a random one if None is given
        if self.static_order_type:
            order_type = self.static_order_type
        else:
            order_type = self._genereate_order_type()

        if order_type == OrderType.LIMIT:
            order_price = self._generate_order_price(order_amount, order_side)
        else:
            order_price = None

        new_order = Order(
            counterpart_id=order_counterpart_id,
            instrument=self.instrument,
            order_type=order_type,
            side=order_side,
            amount=order_amount,
            price=order_price
        )

        return (new_order, order_interarrival_time)

    def generate_orders(self, start_time: datetime, n_orders: int) -> list[Order]:
        # Produces a list of orders, each timestamped based on Poisson intervals
        current_time = start_time
        order_list: list[Order] = []

        for _ in range(n_orders):
            new_order, interarrival_time = self.generate_order()
            new_order.add_timestamp(current_time)
            new_order.generate_id()
            order_list.append(new_order)
            current_time += timedelta(seconds=interarrival_time)

        return order_list
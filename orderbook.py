from typing import Deque
from datetime import datetime
from collections import deque

from trade import Trade
from instrument import Instrument
from order import Order, OrderType, OrderSide


# Introduced to account for floating-point inaccuracy
ERROR_TOLERANCE = 1e-9


class OrderBook:
    """
    Maintains bids (buy orders) and asks (sell orders) for a specific instrument.
    Enforces price-time priority. Generates Trades upon successful matches.
    """

    def __init__(self, instrument: Instrument) -> None:
        self.instrument: Instrument = instrument
        # Storing Order objects within bids and asks queues
        self.bids: Deque[Order] = deque()
        self.asks: Deque[Order] = deque()
        self.trades: list[Trade] = []

    def _validate_limit_price(self, incoming_order: Order) -> None:
        """
        Returns if 'price' is not a multiple of 'tick_size' within a
        small epsilon tolerance to avoid floating-point rounding issues.
        """
        limit_price = incoming_order.price
        tick_size = self.instrument.min_tick_size
        error = abs(round(limit_price / tick_size) * tick_size - limit_price)
        if error > ERROR_TOLERANCE:
            raise ValueError(f"Limit price {limit_price} breaches the minimum tick size of {tick_size}")


    def add_order(self, incoming_order: Order) -> list[Trade]:
        """
        Main entry point: match incoming_order against the order book.
        Returns a list of Trades generated by this matching operation.
        """
        if incoming_order.instrument != self.instrument:
            raise ValueError("Incoming order instrument does not match this OrderBook.")

        if incoming_order.order_type == OrderType.LIMIT:
            self._validate_limit_price(incoming_order)

        if incoming_order.side == OrderSide.BUY:
            return self._match_buy_order(incoming_order)
        elif incoming_order.side == OrderSide.SELL:
            return self._match_sell_order(incoming_order)

    def _match_buy_order(self, buy_order: Order) -> list[Trade]:
        trades: list[Trade] = []
        # MARKET buy => check liquidity first
        if buy_order.order_type == OrderType.MARKET:
            if not self._has_sufficient_liquidity(buy_order, side=OrderSide.BUY):
                return trades  # insufficient volume => reject

        trades = self._execute_buy_matches(buy_order)

        # Insert leftover LIMIT buy
        if (buy_order.amount > 0) and (buy_order.order_type == OrderType.LIMIT):
            self._insert_bid(buy_order)

        return trades

    def _match_sell_order(self, sell_order: Order) -> list[Trade]:
        trades: list[Trade] = []
        # MARKET sell => check liquidity
        if sell_order.order_type == OrderType.MARKET:
            if not self._has_sufficient_liquidity(sell_order, side=OrderSide.SELL):
                return trades # insufficient volume => reject

        trades = self._execute_sell_matches(sell_order)

        # Insert leftover LIMIT sell
        if (sell_order.amount > 0) and (sell_order.order_type == OrderType.LIMIT):
            self._insert_ask(sell_order)

        return trades

    def _execute_buy_matches(self, buy_order: Order) -> list[Trade]:
        trades: list[Trade] = []
        while buy_order.amount > 0 and self.asks:
            best_ask = self.asks[0]

            # For LIMIT order to proceed, limit price must be >= best ask
            if (buy_order.order_type == OrderType.LIMIT) and (best_ask.price - ERROR_TOLERANCE > buy_order.price):
                break

            matched_amount = min(buy_order.amount, best_ask.amount)
            execution_price = best_ask.price

            new_trade = Trade(
                buy_order_id=buy_order.id,
                sell_order_id=best_ask.id,
                instrument=self.instrument,
                price=execution_price,
                amount=matched_amount,
                timestamp=datetime.now()
            )
            
            # Recording the trades in the global scope 
            self.trades.append(new_trade)
            trades.append(new_trade)

            buy_order.amount -= matched_amount
            best_ask.amount -= matched_amount

            # If the best ask is fully filled, pop it. Otherwise update its remaining amount in place.
            if best_ask.amount == 0:
                self.asks.popleft()
            else:
                self.asks[0] = best_ask

            if buy_order.amount == 0:
                break

        return trades

    def _execute_sell_matches(self, sell_order: Order) -> list[Trade]:
        trades: list[Trade] = []
        while sell_order.amount > 0 and self.bids:
            best_bid = self.bids[0]

            # For LIMIT order to proceed, limit price must be <= best bid
            if (sell_order.order_type == OrderType.LIMIT) and (best_bid.price + ERROR_TOLERANCE < sell_order.price):
                break

            matched_amount = min(sell_order.amount, best_bid.amount)
            execution_price = best_bid.price

            new_trade = Trade(
                buy_order_id=best_bid.id,
                sell_order_id=sell_order.id,
                instrument=self.instrument,
                price=execution_price,
                amount=matched_amount,
                timestamp=datetime.now()
            )

            # Recording the trades in the global scope 
            self.trades.append(new_trade)
            trades.append(new_trade)

            sell_order.amount -= matched_amount
            best_bid.amount -= matched_amount

            if best_bid.amount == 0:
                self.bids.popleft()
            else:
                self.bids[0] = best_bid

            if sell_order.amount == 0:
                break

        return trades

    def _insert_bid(self, order: Order) -> None:
        # Higher price => earlier in the list, tie -> FIFO
        inserted = False
        for i, existing_order in enumerate(self.bids):
            if existing_order.price < (order.price or 0.0):
                self.bids.insert(i, order)
                inserted = True
                break
        if not inserted:
            self.bids.append(order)

    def _insert_ask(self, order: Order) -> None:
        # Lower price => earlier in the list, tie -> FIFO
        inserted = False
        for i, existing_order in enumerate(self.asks):
            if existing_order.price > (order.price or 0.0):
                self.asks.insert(i, order)
                inserted = True
                break
        if not inserted:
            self.asks.append(order)

    def _has_sufficient_liquidity(self, incoming_order: Order, side: str) -> bool:
        total_liquidity = 0
        needed = incoming_order.amount

        if side == OrderSide.BUY:
            for ask_order in self.asks:
                total_liquidity += ask_order.amount
                if total_liquidity >= needed:
                    return True
        elif side == OrderSide.SELL:
            for bid_order in self.bids:
                total_liquidity += bid_order.amount
                if total_liquidity >= needed:
                    return True

        return False
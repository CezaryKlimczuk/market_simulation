from datetime import datetime
from dataclasses import dataclass

from instrument import Instrument


@dataclass
class Trade:
    # Links matched orders
    buy_order_id: int
    sell_order_id: int
    instrument: Instrument
    price: float
    amount: int
    timestamp: datetime
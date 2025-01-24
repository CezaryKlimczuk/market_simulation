from datetime import datetime
from dataclasses import dataclass

from instrument import Instrument


@dataclass
class Trade:
    """
    Represents an executed match between one buy order and one sell order.
    """
    buy_order_id: int
    sell_order_id: int
    instrument: Instrument
    price: float
    amount: int
    timestamp: datetime
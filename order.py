from enum import Enum
from datetime import datetime
from dataclasses import dataclass

from instrument import Instrument


class OrderSide(Enum):
    BUY = 1
    SELL = 2

class OrderType(Enum):
    LIMIT = 1
    MARKET = 2

@dataclass
class Order:
    timestamp: datetime
    counterpart_id: int
    instrument: Instrument
    order_type: OrderType
    side: OrderSide
    amount: int
    price: float | None

    def __post_init__(self):
        self.id = hash(self.__str__())

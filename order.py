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
    counterpart_id: int
    instrument: Instrument
    order_type: OrderType
    side: OrderSide
    amount: int
    price: float | None


    def add_timestamp(self, timestamp: datetime) -> None:
        # Allows adding a timestamp after instantiation
        self.timestamp = timestamp

    def generate_id(self) -> None:
        self.id = hash(self.__str__())

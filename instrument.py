from dataclasses import dataclass

@dataclass
class Instrument:
    code: str
    name: str
    is_active: bool
    min_tick_size: float = 0.01
from dataclasses import dataclass


@dataclass(frozen=True)
class Constants:
    POW_PREFIX: str = "0000"
    REWARD_AMOUNT: float = 50.0
    STANDART_FEE: float = 0.0001
    EMPTY_FEE: float = 0.0
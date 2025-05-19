import random
import time


class TimeService:
    MIN_DELAY: int = 500
    MAX_DELAY: int = 1000
    DIVIDER: float = 1000.0

    @staticmethod
    def random_delay():
        delay_ms = random.randint(TimeService.MIN_DELAY, TimeService.MAX_DELAY)
        time.sleep(delay_ms / TimeService.DIVIDER)
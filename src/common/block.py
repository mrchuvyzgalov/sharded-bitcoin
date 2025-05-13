import hashlib
from collections import namedtuple
from typing import Optional
from uuid import UUID

from src.common.transaction import Transaction

BlockData = namedtuple("BlockData", ["transactions", "previous_hash"])

class Block:
    def __init__(self) -> None:
        self._nonce: int = 0
        self._transactions: list[Transaction] = []
        self._previous_hash: Optional[UUID] = None

    def __str__(self) -> str:
        return str(self.get_data())

    def get_data(self) -> BlockData:
        return BlockData(transactions=self._transactions,
                         previous_hash=self._previous_hash)

    def inc_nonce(self) -> None:
        self._nonce += 1

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)

    def calculate_hash(self) -> str:
        tx_hash = self._calculate_tx_hash()
        hash_line = f"{self._nonce}-{self._previous_hash}-{tx_hash}"
        return hashlib.sha256(hash_line.encode()).hexdigest()

    def set_previous_hash(self, previous_hash: str) -> None:
        self._previous_hash = previous_hash

    def _calculate_tx_hash(self) -> str:
        hash_line = ""

        for transaction in self._transactions:
            hash_line += f"{transaction.calculate_hash()}"

        return hashlib.sha256(hash_line.encode()).hexdigest()
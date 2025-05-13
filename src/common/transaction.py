import datetime
import hashlib
import time
from collections import namedtuple
from uuid import UUID, uuid4

from src.common.input import Input
from src.common.output import Output

TransactionData = namedtuple("TransactionData", ["id", "inputs", "outputs", "fee", "hash"])

class Transaction:
    def __init__(self,
                 inputs: list[Input],
                 outputs: list[Output],
                 fee: float = 0.0) -> None:
        self._id: UUID = uuid4()
        self._inputs: list[Input] = inputs
        self._outputs: list[Output] = outputs
        self._timestamp: datetime = time.time()
        self._fee: float = fee
        self._hash: str = self.calculate_hash()

    def __str__(self) -> str:
        return str(self.get_data())

    def get_data(self) -> TransactionData:
        return TransactionData(id=self._id,
                               inputs=self._inputs,
                               outputs=self._outputs,
                               fee=self._fee,
                               hash=self._hash)

    def calculate_hash(self) -> str:
        hash_line = f"{self._id}-{self._inputs}-{self._outputs}-{self._timestamp}-{self._fee}"
        return hashlib.sha256(hash_line.encode()).hexdigest()
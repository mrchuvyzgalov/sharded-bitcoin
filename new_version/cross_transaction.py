import hashlib
from collections import namedtuple

from common.transaction import Transaction

CrossTransactionData = namedtuple("CrossTransactionData",
                                  ["id", "shard_from", "shard_to", "tx", "hash"])

class CrossTransaction:
    def __init__(self,
                 shard_from: int,
                 shard_to: int,
                 tx: Transaction):
        self._shard_from: int = shard_from
        self._shard_to: int = shard_to
        self._tx: Transaction = tx
        self._hash = self._calculate_hash()

    def __str__(self) -> str:
        return str(self.get_data())

    def get_data(self) -> CrossTransactionData:
        return CrossTransactionData(id=self._tx.get_data().id,
                                    shard_from=self._shard_from,
                                    shard_to=self._shard_to,
                                    tx=self._tx,
                                    hash=self._hash)

    def _calculate_hash(self) -> str:
        hash_line = f"{self._shard_from}-{self._shard_to}-{self._tx.calculate_hash()}"
        return hashlib.sha256(hash_line.encode()).hexdigest()
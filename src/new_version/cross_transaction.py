import hashlib
from collections import namedtuple
from uuid import UUID

CrossTransactionData = namedtuple("CrossTransactionData",
                                  ["shard_from", "shard_to", "tx_id", "hash"])

class CrossTransaction:
    def __init__(self,
                 shard_from: int,
                 shard_to: int,
                 tx_id: UUID):
        self._shard_from: int = shard_from
        self._shard_to: int = shard_to
        self._tx_id: UUID = tx_id
        self._hash = self._calculate_hash()

    def __str__(self) -> str:
        return str(self.get_data())

    def get_data(self) -> CrossTransactionData:
        return CrossTransactionData(shard_from=self._shard_from,
                                    shard_to=self._shard_to,
                                    tx_id=self._tx_id,
                                    hash=self._hash)

    def _calculate_hash(self) -> str:
        hash_line = f"{self._shard_from}-{self._shard_to}-{self._tx_id}"
        return hashlib.sha256(hash_line.encode()).hexdigest()
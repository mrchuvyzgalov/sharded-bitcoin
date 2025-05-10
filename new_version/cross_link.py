import hashlib
from datetime import datetime
from collections import namedtuple

from new_version.cross_transaction import CrossTransaction

CrossLinkData = namedtuple("CrossLinkData", ["hash_block", "shard_id", "cross_txs", "timestamp"])

class CrossLink:
    def __init__(self,
                 hash_block: str,
                 shard_id: int,
                 cross_txs: list[CrossTransaction]):
        self._hash_block: str = hash_block
        self._shard_id: int = shard_id
        self._cross_txs: list[CrossTransaction] = cross_txs
        self._timestamp: datetime = datetime.now()

    def __str__(self) -> str:
        return str(self.get_data())

    def get_data(self) -> CrossLinkData:
        return CrossLinkData(hash_block=self._hash_block,
                             shard_id=self._shard_id,
                             cross_txs=self._cross_txs,
                             timestamp=self._timestamp)

    def calculate_hash(self) -> str:
        ctx_hash = self._calculate_ctx_hash()
        hash_line = f"{self._hash_block}-{self._shard_id}-{ctx_hash}-{self._timestamp}"
        return hashlib.sha256(hash_line.encode()).hexdigest()

    def _calculate_ctx_hash(self) -> str:
        hash_line = ""

        for clx in self._cross_txs:
            hash_line += f"{clx.get_data().hash}"

        return hashlib.sha256(hash_line.encode()).hexdigest()
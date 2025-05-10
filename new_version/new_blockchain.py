from typing import Optional

from common.block import Block
from common.blockchain import Blockchain
from common.user import User
from new_version.cross_link import CrossLink
from new_version.cross_transaction import CrossTransaction


class NewBlockchain(Blockchain):
    def __init__(self,
                 owner: User,
                 block_capacity: int) -> None:
        super().__init__(owner=owner, block_capacity=block_capacity)

        self._mem_pool_cross_tx: list[CrossTransaction] = []
        self._new_block: Optional[Block] = None

    def add_cross_transaction(self, cross_transaction: CrossTransaction) -> None:
        self._mem_pool_cross_tx.append(cross_transaction)

    def add_block(self, block: Block) -> None:
        super().add_block(block=block)

        self._mem_pool_cross_tx.clear()
        self._new_block = None

    def create_cross_link(self, shard_id: int) -> CrossLink:
        return CrossLink(shard_id=shard_id,
                         hash_block=self._new_block.calculate_hash(),
                         cross_txs=self._mem_pool_cross_tx)

    def prove_of_work(self) -> Block:
        block: Block = super().prove_of_work()
        self._new_block = block
        return block

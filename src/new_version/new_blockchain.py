import copy
from typing import Optional

from src.common.block import Block
from src.common.blockchain import Blockchain
from src.common.user import User
from src.new_version.cross_link import CrossLink
from src.new_version.cross_transaction import CrossTransaction


class NewBlockchain(Blockchain):
    def __init__(self,
                 owner: User,
                 block_capacity: int) -> None:
        super().__init__(owner=owner, block_capacity=block_capacity)

        self._mem_pool_cross_tx: list[CrossTransaction] = []

    def add_cross_transaction(self, cross_transaction: CrossTransaction) -> None:
        self._mem_pool_cross_tx.append(cross_transaction)

    def add_block(self, block: Block) -> None:
        super().add_block(block=block)
        self._mem_pool_cross_tx.clear()

    def create_cross_link(self, shard_id: int, new_block: Block) -> CrossLink:
        return CrossLink(shard_id=shard_id,
                         hash_block=new_block.calculate_hash(),
                         cross_txs=copy.deepcopy(self._mem_pool_cross_tx))


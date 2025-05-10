from collections import namedtuple

from common.block import Block
from common.transaction import Transaction
from common.user import User
from config.constance import Constants
from service.time_service import TimeService

BlockchainData = namedtuple("BlockchainData", ["owner", "blocks", "mem_pool"])

class Blockchain:
    def __init__(self,
                 owner: User,
                 block_capacity: int) -> None:
        self._owner = owner
        self._blocks: list[Block] = []
        self._users: list[User] = []
        self._block_capacity = block_capacity
        self._mem_pool: list[Transaction] = []

        self._create_init_block()

    def get_data(self) -> BlockchainData:
        return BlockchainData(owner=self._owner, blocks=self._blocks, mem_pool=self._mem_pool)

    def add_transaction(self, transaction: Transaction) -> None:
        self._mem_pool.append(transaction)

    def add_block(self, block: Block) -> None:
        self._blocks.append(block)
        self._mem_pool.clear()

    def need_to_create_block(self) -> bool:
        return len(self._mem_pool) >= self._block_capacity

    def set_owner(self, owner: User) -> None:
        self._owner = owner

    def add_user(self, user: User) -> None:
        self._users.append(user)

    def prove_of_work(self) -> Block:
        TimeService.random_delay()

        block: Block = self._form_block()
        while not block.calculate_hash().startswith(Constants.POW_PREFIX):
            block.inc_nonce()

        return block

    def _form_block(self) -> Block:
        block: Block = Block()

        for tx in self._mem_pool:
            block.add_transaction(tx)
        block.set_previous_hash(self._blocks[-1].calculate_hash())

        return block

    def _create_init_block(self) -> None:
        block = Block()

        while not block.calculate_hash().startswith(Constants.POW_PREFIX):
            block.inc_nonce()

        self._blocks.append(block)
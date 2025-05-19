from typing import Optional

from src.common.user import User
from src.config.constance import Constants
from src.new_version.beacon_block import BeaconBlock
from src.new_version.cross_link import CrossLink
from src.service.time_service import TimeService


class BeaconBlockchain:
    def __init__(self,
                 owner: User,
                 block_capacity: int):
        self._owner = owner
        self._blocks: list[BeaconBlock] = []
        self._users: list[User] = []
        self._block_capacity = block_capacity

        self._mem_pool: list[CrossLink] = []
        self._new_block: Optional[BeaconBlock] = None

        self._create_init_block()

    def get_blocks(self) -> list[BeaconBlock]:
        return self._blocks

    def add_user(self, user: User) -> None:
        self._users.append(user)

    def add_cross_link(self, cross_link: CrossLink) -> None:
        self._mem_pool.append(cross_link)

    def set_owner(self, owner: User) -> None:
        self._owner = owner

    def prove_of_work(self) -> BeaconBlock:
        TimeService.random_delay()

        block: BeaconBlock = self._form_block()
        while not block.calculate_hash().startswith(Constants.POW_PREFIX):
            block.inc_nonce()

        self._new_block = block
        return self._new_block

    def need_to_create_block(self) -> bool:
        return len(self._mem_pool) == self._block_capacity

    def add_block(self, block: BeaconBlock) -> None:
        self._blocks.append(block)

        self._mem_pool.clear()
        self._new_block = None

    def _form_block(self) -> BeaconBlock:
        block: BeaconBlock = BeaconBlock()

        for cl in self._mem_pool:
            block.add_cross_link(cl)
        block.set_previous_hash(self._blocks[-1].calculate_hash())

        return block

    def _create_init_block(self) -> None:
        block = BeaconBlock()

        while not block.calculate_hash().startswith(Constants.POW_PREFIX):
            block.inc_nonce()

        self._blocks.append(block)
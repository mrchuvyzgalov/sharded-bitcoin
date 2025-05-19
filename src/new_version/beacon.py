import copy
import random

from src.common.user import User
from src.config.config import Basic
from src.config.constance import Constants
from src.new_version.beacon_block import BeaconBlock
from src.new_version.beacon_blockchain import BeaconBlockchain
from src.new_version.cross_link import CrossLink


class Beacon:
    def __init__(self, block_capacity: int) -> None:
        self._validators: list[User] = []
        self._blockchains: list[BeaconBlockchain] = [BeaconBlockchain(owner=Basic.FIRST_USER, block_capacity=block_capacity)]

    def get_blocks(self) -> list[BeaconBlock]:
        return self._blockchains[0].get_blocks()

    def set_validators(self, validators: list[User]) -> None:
        blockchain_copy = self._blockchains[-1]
        self._blockchains.clear()

        for validator in validators:
            new_blockchain = copy.deepcopy(blockchain_copy)
            new_blockchain.set_owner(validator)
            self._blockchains.append(new_blockchain)

        self._validators = validators

    def add_user(self, user: User) -> None:
        for blockchain in self._blockchains:
            blockchain.add_user(user)

    def handle_block(self, cross_links: dict[int, CrossLink]) -> None:
        for blockchain in self._blockchains:
            for cl in cross_links.values():
                blockchain.add_cross_link(cross_link=cl)

        self._create_new_block()

    def _create_new_block(self) -> None:
        validator_num: int = random.randint(0, len(self._validators) - 1)
        new_block: BeaconBlock = self._blockchains[validator_num].prove_of_work()

        self._check_block_by_validators(block=new_block)

        for blockchain in self._blockchains:
            blockchain.add_block(new_block)

    def _check_block_by_validators(self, block: BeaconBlock) -> bool:
        for _ in self._validators:
            if not block.calculate_hash().startswith(Constants.POW_PREFIX):
                return False
        return True
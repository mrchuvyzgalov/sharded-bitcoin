import copy
import random
from collections import namedtuple
from typing import Optional
from uuid import UUID

from src.common.block import Block
from src.common.input import Input
from src.common.output import Output
from src.common.transaction import Transaction
from src.common.user import User
from src.config.config import Basic
from src.config.constance import Constants
from src.new_version.cross_link import CrossLink
from src.new_version.cross_transaction import CrossTransaction
from src.new_version.new_blockchain import NewBlockchain
from src.service.balance_service import BalanceService
from src.service.input_service import InputService
from src.service.output_service import OutputService
from src.service.shard_service import ShardService
from src.service.transaction_service import FreeTransactionData, TransactionService

ShardData = namedtuple("ShardData", ["validators"])

class Shard:
    def __init__(self,
                 shard_id: int,
                 amount_of_shards: int,
                 block_capacity: int) -> None:
        self._shard_id: int = shard_id
        self._validators: list[User] = []
        self._blockchains: list[NewBlockchain] = [NewBlockchain(owner=Basic.FIRST_USER, block_capacity=block_capacity)]
        self._users: list[User] = []
        self._amount_of_shards: int = amount_of_shards
        self._block_capacity: int = block_capacity

    def get_mempool(self) -> list[Transaction]:
        return self._blockchains[0].get_data().mem_pool

    def get_blocks(self) -> list[Block]:
        return self._blockchains[0].get_data().blocks

    def get_balances(self) -> dict[User, float]:
        result: dict[User, float] = {}

        for user in self._users:
            if ShardService.get_shard_number_by_user(user.get_data().id, self._amount_of_shards) == self._shard_id:
                result[user] = BalanceService.get_balance_by_user(blockchain=self._blockchains[0], user=user)

        return result

    def add_reward_to_all_users(self) -> None:
        for user in self._users:
            if self._shard_id == ShardService.get_shard_number_by_user(user.get_data().id, amount_of_shards=self._amount_of_shards):
                self.add_reward_for_user(user=user, fees=0.0)

    def add_cross_tx(self, cross_tx: Transaction) -> None:
        for blockchain in self._blockchains:
            blockchain.add_transaction(cross_tx)

    def add_reward_for_user(self, user: User, fees: float) -> None:
        inputs: list[Input] = []
        outputs: list[Output] = [Output(money=Constants.REWARD_AMOUNT + fees, receiver_id=user.get_data().id)]
        self._add_tx(tx=Transaction(inputs=inputs, outputs=outputs))

    def get_data(self) -> ShardData:
        return ShardData(validators=self._validators)

    def add_user(self, user: User) -> None:
        self._users.append(user)
        for blockchain in self._blockchains:
            blockchain.add_user(user)

    def is_user_in_shard(self, user_id: UUID) -> bool:
        for user in self._users:
            if user_id == user.get_data().id:
                return True
        return False

    def set_validators(self, validators: list[User]) -> None:
        blockchain_copy = self._blockchains[-1]

        self._blockchains.clear()

        for validator in validators:
            new_blockchain = copy.deepcopy(blockchain_copy)
            new_blockchain.set_owner(validator)
            self._blockchains.append(new_blockchain)

        self._validators = validators

    def need_to_handle_shard(self) -> bool:
        for blockchain in self._blockchains:
            if blockchain.need_to_create_block():
                return True
        return False

    def create_new_block(self) -> tuple[Block, User, CrossLink]:
        validator_num: int = random.randint(0, len(self._validators) - 1)
        new_block: Block = self._blockchains[validator_num].prove_of_work()

        self._check_block_by_validators(block=new_block)

        miner: User = self._users[validator_num]
        cross_link: CrossLink = self._blockchains[validator_num].create_cross_link(shard_id=self._shard_id, new_block=new_block)

        return new_block, miner, cross_link

    def add_block(self, new_block: Block) -> None:
        for blockchain in self._blockchains:
            blockchain.add_block(new_block)

    def send_money(self,
                   from_user: UUID,
                   to_user: UUID,
                   money: float,
                   fee: float) -> bool:
        shard_from: int = ShardService.get_shard_number_by_user(user_id=from_user, amount_of_shards=self._amount_of_shards)
        shard_to: int = ShardService.get_shard_number_by_user(user_id=to_user,  amount_of_shards=self._amount_of_shards)

        new_tx: Optional[Transaction] = self._create_tx(from_user=from_user, to_user=to_user, money=money, fee=fee)

        if new_tx is None:
            return False

        self._add_tx(tx=new_tx)

        if shard_from != shard_to:
            cross_tx: CrossTransaction = CrossTransaction(shard_from=shard_from, shard_to=shard_to, tx=new_tx)

            for blockchain in self._blockchains:
                blockchain.add_cross_transaction(cross_transaction=cross_tx)

        return True

    def _add_tx(self, tx: Transaction) -> None:
        for blockchain in self._blockchains:
            blockchain.add_transaction(transaction=tx)

    def _check_block_by_validators(self, block: Block) -> bool:
        for _ in self._validators:
            if not block.calculate_hash().startswith(Constants.POW_PREFIX):
                return False
        return True

    def _find_user_and_blockchain(self, user_id: UUID) -> tuple[Optional[User], Optional[NewBlockchain]]:
        for user in self._users:
            if user_id == user.get_data().id:
                return user, self._blockchains[0]
        return None, None

    def _create_tx(self,
                   from_user: UUID,
                   to_user: UUID,
                   money: float,
                   fee: float) -> Optional[Transaction]:
        user, blockchain = self._find_user_and_blockchain(user_id=from_user)

        free_outputs: list[FreeTransactionData] = TransactionService.find_free_outputs_by_user(blockchain=blockchain, user=user)
        new_inputs: Optional[list[Input]] = InputService.create_new_inputs(free_outputs=free_outputs,
                                                                           from_user=user,
                                                                           money=money,
                                                                           fee=fee)

        if new_inputs is None:
            return None

        new_outputs: list[Output] = OutputService.create_new_outputs(free_outputs=free_outputs,
                                                                     from_user=from_user,
                                                                     to_user=to_user,
                                                                     money=money,
                                                                     fee=fee)
        return Transaction(inputs=new_inputs,outputs=new_outputs, fee=fee)

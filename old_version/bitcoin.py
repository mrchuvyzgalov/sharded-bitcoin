import copy
import random
from typing import Optional
from uuid import UUID

from common.block import Block
from common.blockchain import Blockchain
from common.input import Input
from common.output import Output
from common.transaction import Transaction
from common.user import User
from config.config import Basic
from config.constance import Constants
from service.balance_service import BalanceService
from service.block_service import BlockService
from service.input_service import InputService
from service.output_service import OutputService
from service.transaction_service import FreeTransactionData, TransactionService
from service.user_service import UserService


class Bitcoin:
    def __init__(self, block_capacity: int) -> None:
        self._users: list[User] = []
        self._blockchains: list[Blockchain] = [Blockchain(owner=Basic.FIRST_USER, block_capacity=block_capacity)]
        self._block_capacity: int = block_capacity

        self._miner: Optional[User] = None

    def set_validators(self) -> None:
        blockchain_copy = self._blockchains[-1]

        self._blockchains.clear()

        for validator in self._users:
            new_blockchain = copy.deepcopy(blockchain_copy)
            new_blockchain.set_owner(validator)
            self._blockchains.append(new_blockchain)

    def create_user(self) -> User:
        user: User = User()

        for blockchain in self._blockchains:
            blockchain.add_user(user)
        self._users.append(user)

        return user

    def get_balances(self) -> dict[User, float]:
        result: dict[User, float] = {}

        for i in range(len(self._users)):
            user: User = self._users[i]
            blockchain: Blockchain = self._blockchains[i]

            result[user] = BalanceService.get_balance_by_user(blockchain=blockchain, user=user)

        return result

    def try_to_create_new_block(self) -> bool:
        for blockchain in self._blockchains:
            if blockchain.need_to_create_block():
                self.create_new_block()
                return True

        return False

    def send_money(self,
                   from_user: UUID,
                   to_user: UUID,
                   money: float,
                   fee: float) -> bool:
        is_valid: bool = self._validate_request(from_user=from_user,
                                                to_user=to_user,
                                                money=money,
                                                fee=fee)
        if not is_valid:
            return False

        new_tx: Optional[Transaction] = self._create_tx(from_user=from_user, to_user=to_user, money=money, fee=fee)

        if new_tx is None:
            return False

        self._add_tx(tx=new_tx)

        return True

    def add_reward_for_all_users(self) -> None:
        for user in self._users:
            self._add_reward_for_user(user=user)

    def _add_reward_for_user(self, user: User) -> None:
        inputs: list[Input] = []
        outputs: list[Output] = [Output(money=Constants.REWARD_AMOUNT, receiver_id=user.get_data().id)]
        self._add_tx(tx=Transaction(inputs=inputs, outputs=outputs))

    def _add_tx(self, tx: Transaction) -> None:
        for blockchain in self._blockchains:
            blockchain.add_transaction(transaction=tx)

    def _find_user_and_blockchain(self, user_id: UUID) -> tuple[Optional[User], Optional[Blockchain]]:
        for i in range(len(self._users)):
            user: User = self._users[i]
            blockchain: Blockchain = self._blockchains[i]

            if user_id == user.get_data().id:
                return user, blockchain

        return None, None

    def create_new_block(self) -> None:
        validator_num: int = random.randint(0, len(self._users) - 1)
        new_block: Block = self._blockchains[validator_num].prove_of_work()

        for _ in self._users:
            BlockService.check_block_validity(block=new_block)

        for blockchain in self._blockchains:
            blockchain.add_block(new_block)

        self._add_reward_for_miner(new_block=new_block, miner=self._users[validator_num])

    def _add_reward_for_miner(self, new_block: Block, miner: User) -> None:
        fees: float = BlockService.get_block_fees(block=new_block)
        _reward_for_miner: float = fees + Constants.REWARD_AMOUNT

        self._add_reward_for_user(user=miner)

    def _create_tx(self,
                   from_user: UUID,
                   to_user: UUID,
                   money: float,
                   fee: float) -> Optional[Transaction]:
        user, blockchain = self._find_user_and_blockchain(user_id=from_user)

        free_outputs: list[FreeTransactionData] = TransactionService.find_free_outputs_by_user(blockchain=blockchain,
                                                                                               user=user)
        from_user_model: User = UserService.find_user_by_id(user_id=from_user, users=self._users)
        new_inputs: Optional[list[Input]] = InputService.create_new_inputs(free_outputs=free_outputs,
                                                                           from_user=from_user_model,
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

    def _validate_request(self,
                          from_user: UUID,
                          to_user: UUID,
                          money: float,
                          fee: float) -> bool:
        if money < 0 or fee < 0:
            return False
        return self._check_user_existence(from_user=from_user, to_user=to_user)

    def _check_user_existence(self,
                              from_user: UUID,
                              to_user: UUID) -> bool:
        return UserService.check_user_existence(user_id=from_user, users=self._users) and \
            UserService.check_user_existence(user_id=to_user, users=self._users)

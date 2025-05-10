from concurrent.futures import ProcessPoolExecutor
from uuid import UUID

from common.block import Block
from common.transaction import Transaction
from common.user import User
from new_version.beacon import Beacon
from new_version.cross_link import CrossLink
from new_version.shard import Shard
from service.block_service import BlockService
from service.random_service import RandomService
from service.shard_service import ShardService


class Bitcoin:
    def __init__(self,
                 amount_of_shards: int,
                 block_capacity: int) -> None:
        self._shards: list[Shard] = [Shard(shard_id=i,
                                           amount_of_shards=amount_of_shards,
                                           block_capacity=block_capacity) for i in range(amount_of_shards)]
        self._beacon = Beacon(block_capacity=block_capacity)
        self._users: list[User] = []
        self._block_capacity: int = block_capacity
        self._amount_of_shards: int = amount_of_shards
        self._executor = ProcessPoolExecutor(max_workers=amount_of_shards)

    def create_user(self) -> User:
        user: User = User()

        for shard in self._shards:
            shard.add_user(user)
        self._beacon.add_user(user)
        self._users.append(user)

        return user

    def set_validators(self) -> None:
        groups: list[list[User]] = RandomService.split_users(self._users, self._amount_of_shards)

        for i in range(len(self._shards)):
            self._shards[i].set_validators(groups[i])

        self._beacon.set_validators(self._users)

    def add_reward_to_all_users(self) -> None:
        for shard in self._shards:
            shard.add_reward_to_all_users()

    def get_balances(self) -> dict[User, float]:
        result: dict[User, float] = {}

        for shard in self._shards:
            result.update(shard.get_balances())

        return result

    def send_money(self,
                   from_user: UUID,
                   to_user: UUID,
                   money: float,
                   fee: float) -> bool:
        self._check_user_existence(from_user=from_user,
                                   to_user=to_user)

        shard_num_from: int = ShardService.get_shard_number_by_user(user_id=from_user, amount_of_shards=self._amount_of_shards)
        return self._shards[shard_num_from].send_money(from_user=from_user,
                                                       to_user=to_user,
                                                       money=money,
                                                       fee=fee)

    def try_to_handle_new_blocks(self) -> bool:
        for shard in self._shards:
            if shard.need_to_handle_shard():
                self.handle_shards()
                return True
        return False

    def handle_shards(self) -> None:
        new_blocks: list[Block] = []
        miners: list[User] = []
        cross_links: list[CrossLink] = []

        futures = []

        for shard in self._shards:
            futures.append(self._executor.submit(shard.create_new_block))

        for future in futures:
            new_block, miner, cross_link = future.result()

            new_blocks.append(new_block)
            miners.append(miner)
            cross_links.append(cross_link)

        self._add_new_blocks(new_blocks)
        self._beacon.handle_block(cross_links)
        self._add_rewards(miners, new_blocks)
        self._add_cross_transactions(cross_links)

    def __del__(self):
        self._executor.shutdown(wait=True)

    def _add_new_blocks(self, new_blocks: list[Block]) -> None:
        for shard_numb in range(self._amount_of_shards):
            self._shards[shard_numb].add_block(new_blocks[shard_numb])

    def _add_rewards(self, miners: list[User], new_blocks: list[Block]) -> None:
        for i in range(len(miners)):
            miner: User = miners[i]
            fees: float = BlockService.get_block_fees(block=new_blocks[i])

            shard_num: int = ShardService.get_shard_number_by_user(user_id=miner.get_data().id, amount_of_shards=self._amount_of_shards)
            self._shards[shard_num].add_reward_for_user(miner, fees)

    def _add_cross_transactions(self, cross_links: list[CrossLink]) -> None:
        for cross_link in cross_links:
            for cross_tx in cross_link.get_data().cross_txs:
                tx: Transaction = cross_tx.get_data().tx
                self._shards[cross_tx.get_data().shard_to].add_cross_tx(tx)

    def _check_user_existence(self,
                              from_user: UUID,
                              to_user: UUID) -> bool:
        shard_num_from: int = ShardService.get_shard_number_by_user(user_id=from_user, amount_of_shards=self._amount_of_shards)
        shard_num_to: int = ShardService.get_shard_number_by_user(user_id=to_user, amount_of_shards=self._amount_of_shards)

        if not self._is_user_in_shard(user_id=from_user, shard_num=shard_num_from):
            return False
        return self._is_user_in_shard(user_id=to_user, shard_num=shard_num_to)

    def _is_user_in_shard(self, user_id: UUID, shard_num: int) -> bool:
        if self._shards[shard_num] is not None:
            return False
        return self._shards[shard_num].is_user_in_shard(user_id=user_id)
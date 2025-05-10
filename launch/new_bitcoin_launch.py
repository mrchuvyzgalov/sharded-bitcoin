import random
import time
from collections import namedtuple

from common.user import User
from config.constance import Constants
from new_version.bitcoin import Bitcoin
from service.user_service import UserService

LaunchNewBitcoinData = namedtuple("LaunchNewBitcoinData", ["time", "amount_of_transactions"])

def launch_best_new_bitcoin(amount_of_blocks: int,
                            amount_of_users: int,
                            block_capacity: int,
                            amount_of_shards: int) -> LaunchNewBitcoinData:
    bitcoin = Bitcoin(amount_of_shards=amount_of_shards, block_capacity=block_capacity)
    users: list[User] = [bitcoin.create_user() for _ in range(amount_of_users)]
    groups: list[list[User]] = UserService.group_users_by_shards(users=users, amount_of_shards=amount_of_shards)

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_to_all_users()
        bitcoin.handle_shards()

    start = time.time()
    amount_of_transactions: int = 0

    for _ in range(amount_of_blocks):
        for shard_id in range(amount_of_shards):
            for _ in range(1, block_capacity):
                user_num: int = random.randint(0, len(groups[shard_id]) - 1)
                bitcoin.send_money(from_user=groups[shard_id][user_num].get_data().id,
                                   to_user=groups[shard_id][(user_num + 1) % len(groups[shard_id])].get_data().id,
                                   money=1.0,
                                   fee=Constants.STANDART_FEE)
                amount_of_transactions += 1

        bitcoin.handle_shards()

    return LaunchNewBitcoinData(time=time.time() - start, amount_of_transactions=amount_of_transactions)

def launch_random_new_bitcoin(amount_of_blocks: int,
                              amount_of_users: int,
                              block_capacity: int,
                              amount_of_shards: int) -> LaunchNewBitcoinData:
    bitcoin = Bitcoin(amount_of_shards=amount_of_shards, block_capacity=block_capacity)
    users: list[User] = [bitcoin.create_user() for _ in range(amount_of_users)]

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_to_all_users()
        bitcoin.handle_shards()

    start = time.time()
    amount_of_transactions: int = 0

    for _ in range(amount_of_blocks):
        is_block_created: bool = False

        while not is_block_created:
            user_num: int = random.randint(0, len(users) - 1)
            is_sent: bool = bitcoin.send_money(from_user=users[user_num].get_data().id,
                                               to_user=users[(user_num + 1) % len(users)].get_data().id,
                                               money=1.0,
                                               fee=Constants.STANDART_FEE)

            if is_sent:
                amount_of_transactions += 1

            if bitcoin.try_to_handle_new_blocks():
                is_block_created = True

    return LaunchNewBitcoinData(time=time.time() - start, amount_of_transactions=amount_of_transactions)

def launch_worst_new_bitcoin(amount_of_blocks: int,
                             amount_of_users: int,
                             block_capacity: int,
                             amount_of_shards: int) -> LaunchNewBitcoinData:
    bitcoin = Bitcoin(amount_of_shards=amount_of_shards, block_capacity=block_capacity)
    users: list[User] = [bitcoin.create_user() for _ in range(amount_of_users)]
    groups: list[list[User]] = UserService.group_users_by_shards(users=users, amount_of_shards=amount_of_shards)

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_to_all_users()
        bitcoin.handle_shards()

    start = time.time()
    amount_of_transactions: int = 0

    for _ in range(amount_of_blocks):
        is_block_created: bool = False

        while not is_block_created:
            group_num: int = random.randint(0, len(groups) - 1)

            user_from: User = random.choice(groups[group_num])
            user_to: User = random.choice(groups[(group_num + 1) % len(groups)])

            is_sent: bool = bitcoin.send_money(from_user=user_from.get_data().id,
                                               to_user=user_to.get_data().id,
                                               money=1.0,
                                               fee=Constants.STANDART_FEE)

            if is_sent:
                amount_of_transactions += 1

            if bitcoin.try_to_handle_new_blocks():
                is_block_created = True

    return LaunchNewBitcoinData(time=time.time() - start, amount_of_transactions=amount_of_transactions)
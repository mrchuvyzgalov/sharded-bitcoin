import random
import time
from collections import namedtuple

from src.common.user import User
from src.config.constance import Constants
from src.old_version.bitcoin import Bitcoin

LaunchOldBitcoinData = namedtuple("LaunchOldBitcoinData", ["time", "amount_of_transactions"])

def launch_bitcoin(amount_of_blocks: int,
                   amount_of_users: int,
                   block_capacity: int) -> LaunchOldBitcoinData:
    bitcoin = Bitcoin(block_capacity=block_capacity)
    users: list[User] = [bitcoin.create_user() for _ in range(amount_of_users)]

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_for_all_users()
        bitcoin.create_new_block()

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

            if bitcoin.try_to_create_new_block():
                is_block_created = True

    return LaunchOldBitcoinData(time=time.time() - start, amount_of_transactions=amount_of_transactions)
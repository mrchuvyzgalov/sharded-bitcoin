import random
import time

from common.user import User
from old_version.bitcoin import Bitcoin


def simple_test() -> None:
    amount_of_attempts = 10
    amount_of_users = 100
    users: list[User] = []
    bitcoin = Bitcoin(block_capacity=100)

    for _ in range(amount_of_users):
        users.append(bitcoin.create_user())

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_for_all_users()
        bitcoin.create_new_block()

    start = time.time()
    amount_of_transactions: int = 0

    for _ in range(amount_of_attempts):
        is_block_created: bool = False

        while not is_block_created:
            user_num: int = random.randint(0, len(users) - 1)
            is_sent: bool = bitcoin.send_money(from_user=users[user_num].get_data().id,
                                               to_user=users[(user_num + 1) % len(users)].get_data().id,
                                               money=5.0,
                                               fee=0.001)

            if is_sent:
                amount_of_transactions += 1

            if bitcoin.try_to_create_new_block():
                is_block_created = True

    end = time.time()

    duration_minutes = (end - start) / 60
    print(f"Time execution: {duration_minutes:.2f} minutes")
    print(f"Amount of transactions: {amount_of_transactions}")
    print(f"Amount of transactions per second: {amount_of_transactions / (duration_minutes * 60):.2f}")

    print(bitcoin.get_balances())
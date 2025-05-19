import random

from src.common.user import User


class RandomService:
    @staticmethod
    def split_users(users: list[User], amount_of_shards: int) -> list[list[User]]:
        random.shuffle(users)
        k, m = divmod(len(users), amount_of_shards)
        return [users[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(amount_of_shards)]
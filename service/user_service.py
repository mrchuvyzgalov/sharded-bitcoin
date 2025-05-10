from typing import Optional
from uuid import UUID

from common.user import User
from service.shard_service import ShardService


class UserService:
    @staticmethod
    def check_user_existence(user_id: UUID, users: list[User]) -> bool:
        for user in users:
            if user_id == user.get_data().id:
                return True
        return False

    @staticmethod
    def find_user_by_id(user_id: UUID, users: list[User]) -> Optional[User]:
        for user in users:
            if user_id == user.get_data().id:
                return user
        return None

    @staticmethod
    def group_users_by_shards(users: list[User], amount_of_shards: int) -> list[list[User]]:
        groups: list[list[User]] = [[] for _ in range(amount_of_shards)]

        for user in users:
            shard_id: int = ShardService.get_shard_number_by_user(user.get_data().id, amount_of_shards)
            groups[shard_id].append(user)

        return groups
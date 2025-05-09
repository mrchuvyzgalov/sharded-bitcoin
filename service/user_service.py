from typing import Optional
from uuid import UUID

from common.user import User


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
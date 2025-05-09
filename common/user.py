from collections import namedtuple
from typing import Optional
from uuid import UUID, uuid4

UserData = namedtuple("UserData", ["id"])

class User:
    def __init__(self,
                 user_id: Optional[UUID] = None) -> None:
        self._id: UUID = user_id or uuid4()

    def sign(self) -> str:
        return f"User {self._id} is signing transaction"

    def get_data(self) -> UserData:
        return UserData(id=self._id)

    def __str__(self) -> str:
        return str(self.get_data())

    def __repr__(self) -> str:
        return f"<User {self._id}>"
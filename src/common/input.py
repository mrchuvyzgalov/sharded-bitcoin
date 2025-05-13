from collections import namedtuple
from typing import Optional
from uuid import UUID, uuid4

from src.common.user import User

InputData = namedtuple("InputData", ["id", "previous_tx", "output_id", "signature"])

class Input:
    def __init__(self,
                 signature: str,
                 previous_tx: Optional[UUID] = None,
                 output_id: Optional[UUID] = None) -> None:
        self._id: UUID = uuid4()
        self._previous_tx: Optional[UUID] = previous_tx
        self._output_id: Optional[UUID] = output_id
        self._signature: str = signature

    def get_data(self) -> InputData:
        return InputData(id=self._id,
                         previous_tx=self._previous_tx,
                         output_id=self._output_id,
                         signature=self._signature)

    def is_user_owner(self, user: User) -> bool:
        return user.sign() == self._signature

    def __str__(self) -> str:
        return str(self.get_data())

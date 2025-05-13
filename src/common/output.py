from collections import namedtuple
from uuid import UUID, uuid4

OutputData = namedtuple("OutputData", ["id", "money", "receiver_id"])

class Output:
    def __init__(self,
                 money: float,
                 receiver_id: UUID) -> None:
        self._id: UUID = uuid4()
        self._money: float = money
        self._receiver_id: UUID = receiver_id

    def get_data(self) -> OutputData:
        return OutputData(id=self._id, money=self._money, receiver_id=self._receiver_id)

    def __str__(self) -> str:
        return str(self.get_data())
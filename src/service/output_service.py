from uuid import UUID

from src.common.output import Output
from src.service.transaction_service import FreeTransactionData


class OutputService:
    @staticmethod
    def create_new_outputs(free_outputs: list[FreeTransactionData],
                           from_user: UUID,
                           to_user: UUID,
                           money: float,
                           fee: float) -> list[Output]:
        curr_sum: float = 0.0
        for free_output in free_outputs:
            curr_sum += free_output.output.get_data().money

        change: float = curr_sum - money - fee

        outputs: list[Output] = [Output(money=money, receiver_id=to_user)]

        if change > 0:
            outputs.append(Output(money=change, receiver_id=from_user))

        return outputs
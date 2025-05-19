from typing import Optional

from src.common.input import Input
from src.common.user import User
from src.service.transaction_service import FreeTransactionData


class InputService:
    @staticmethod
    def create_new_inputs(free_outputs: list[FreeTransactionData],
                          from_user: User,
                          money: float,
                          fee: float) -> Optional[list[Input]]:
        curr_index: int = 0
        curr_sum: float = 0

        req_sum: float = money + fee
        inputs: list[Input] = []

        while curr_index < len(free_outputs) and curr_sum < req_sum:
            free_tx: FreeTransactionData = free_outputs[curr_index]
            curr_sum += free_tx.output.get_data().money

            inputs.append(Input(signature=from_user.sign(),
                                previous_tx=free_tx.tx_id,
                                output_id=free_tx.output.get_data().id))

            curr_index += 1

        if curr_sum < req_sum:
            return None
        return inputs
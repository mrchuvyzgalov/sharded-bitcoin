from common.blockchain import Blockchain
from common.user import User
from service.transaction_service import FreeTransactionData, TransactionService


class BalanceService:
    @staticmethod
    def get_balance_by_user(blockchain: Blockchain,
                            user: User) -> float:
        free_outputs: list[FreeTransactionData] = TransactionService.find_free_outputs_by_user(blockchain, user)

        curr_sum: float = 0.0

        for free_output in free_outputs:
            curr_sum += free_output.output.get_data().money

        return curr_sum
from src.common.block import Block
from src.common.blockchain import Blockchain
from src.common.user import User
from src.new_version.beacon_block import BeaconBlock
from src.new_version.new_blockchain import NewBlockchain
from src.service.transaction_service import FreeTransactionData, TransactionService


class BalanceService:
    @staticmethod
    def get_balance_by_user(blockchain: Blockchain,
                            user: User) -> float:
        free_outputs: list[FreeTransactionData] = TransactionService.find_free_outputs_by_user(blockchain, user)

        curr_sum: float = 0.0

        for free_output in free_outputs:
            curr_sum += free_output.output.get_data().money

        return curr_sum

    @staticmethod
    def get_balance_by_user_new(blockchain: NewBlockchain,
                                shard_blocks: dict[int, list[Block]],
                                beacon_blocks: list[BeaconBlock],
                                user: User) -> float:
        free_outputs: list[FreeTransactionData] = TransactionService.find_free_outputs_by_user_new(blockchain=blockchain,
                                                                                                   shard_blocks=shard_blocks,
                                                                                                   beacon_blocks=beacon_blocks,
                                                                                                   user=user)
        curr_sum: float = 0.0

        for free_output in free_outputs:
            curr_sum += free_output.output.get_data().money

        return curr_sum

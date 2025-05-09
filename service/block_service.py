from common.block import Block
from common.transaction import Transaction
from config.constance import Constants


class BlockService:
    @staticmethod
    def check_block_validity(block: Block) -> bool:
        return block.calculate_hash().startswith(Constants.POW_PREFIX)

    @staticmethod
    def get_block_fees(block: Block) -> float:
        txs: list[Transaction] = block.get_data().transactions

        result: float = 0.0

        for tx in txs:
            result += tx.get_data().fee

        return result
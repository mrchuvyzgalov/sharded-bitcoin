from collections import namedtuple
from typing import Optional
# from typing import Optional
from uuid import UUID

from src.common.block import Block
from src.common.blockchain import Blockchain, BlockchainData
# from src.common.cache import Cache
from src.common.input import InputData
from src.common.output import OutputData
from src.common.transaction import Transaction, TransactionData
from src.common.user import User, UserData
from src.new_version.beacon_block import BeaconBlock
from src.new_version.new_blockchain import NewBlockchain
from src.service.shard_service import ShardService

FreeTransactionData = namedtuple("FreeTransactionData", ["tx_id", "output"])

class TransactionService:
    @staticmethod
    def find_free_outputs_by_user_new(blockchain: NewBlockchain,
                                      user: User,
                                      shard_blocks: dict[int, list[Block]],
                                      beacon_blocks: list[BeaconBlock]) -> list[FreeTransactionData]:
        all_txs: list[Transaction] = TransactionService._find_connected_with_user_txs_new(shard_blocks=shard_blocks,
                                                                                          beacon_blocks=beacon_blocks,
                                                                                          user=user,
                                                                                          blockchain=blockchain)
        free_outputs_set: set[UUID] = TransactionService._find_free_outputs_ids(all_txs=all_txs, user=user)
        return TransactionService._form_free_transaction_data(all_txs=all_txs, free_outputs_set=free_outputs_set)

    @staticmethod
    def find_free_outputs_by_user(blockchain: Blockchain,
                                  user: User) -> list[FreeTransactionData]:
        all_txs: list[Transaction] = TransactionService._find_connected_with_user_txs(blockchain=blockchain, user=user)
        free_outputs_set: set[UUID] = TransactionService._find_free_outputs_ids(all_txs=all_txs, user=user)
        return TransactionService._form_free_transaction_data(all_txs=all_txs, free_outputs_set=free_outputs_set)

    @staticmethod
    def _find_connected_with_user_txs_new(shard_blocks: dict[int, list[Block]],
                                          beacon_blocks: list[BeaconBlock],
                                          user: User,
                                          blockchain: NewBlockchain) -> list[Transaction]:
        shard_id = ShardService.get_shard_number_by_user(user.get_data().id, len(shard_blocks))
        blocks: list[Block] = shard_blocks[shard_id]

        result: list[Transaction] = []

        for i in range(len(beacon_blocks)):
            block_data = blocks[i].get_data()

            for tx in block_data.transactions:
                if TransactionService._tx_suits_for_user(tx=tx, user=user):
                    result.append(tx)

            beacon_block_data = beacon_blocks[i].get_data()

            for cl in beacon_block_data.cross_links:
                for ctx in cl.get_data().cross_txs:
                    if ctx.get_data().shard_to == shard_id:
                        from_shard_id = ctx.get_data().shard_from
                        from_shard_block: Block = shard_blocks[from_shard_id][i]

                        tx: Transaction = TransactionService._get_transaction_by_id(tx_id=ctx.get_data().tx_id,
                                                                                    block=from_shard_block)

                        if TransactionService._tx_suits_for_user(tx=tx, user=user):
                            result.append(tx)

        mem_txs: list[Transaction] = blockchain.get_data().mem_pool
        for tx in mem_txs:
            if TransactionService._tx_suits_for_user(tx=tx, user=user):
                result.append(tx)

        return result

    @staticmethod
    def _get_transaction_by_id(tx_id: UUID, block: Block) -> Optional[Transaction]:
        for tx in block.get_data().transactions:
            if tx.get_data().id == tx_id:
                return tx
        return None

    @staticmethod
    def _delete_used_outputs(blockchain: Blockchain,
                             user: User,
                             free_outputs_set: set[UUID]) -> set[UUID]:
        txs: list[Transaction] = blockchain.get_data().mem_pool
        result: set[UUID] = free_outputs_set.copy()

        for tx in txs:
            for input in tx.get_data().inputs:
                input_data: InputData = input.get_data()

                if input_data.signature == user.sign() and input_data.output_id in free_outputs_set:
                    result.remove(input_data.output_id)

        return result

    @staticmethod
    def _form_free_transaction_data(all_txs: list[Transaction],
                                    free_outputs_set: set[UUID]) -> list[FreeTransactionData]:
        result: list[FreeTransactionData] = []

        for tx in all_txs:
            tx_data: TransactionData = tx.get_data()

            for output in tx_data.outputs:
                output_data: OutputData = output.get_data()

                if output_data.id in free_outputs_set:
                    result.append(FreeTransactionData(tx_id=tx_data.id, output=output))

        return result

    @staticmethod
    def _find_free_outputs_ids(all_txs: list[Transaction],
                               user: User) -> set[UUID]:
        free_outputs_set: set[UUID] = set()

        for tx in all_txs:
            tx_data: TransactionData = tx.get_data()

            for input in tx_data.inputs:
                input_data = input.get_data()

                if input_data.output_id in free_outputs_set:
                    free_outputs_set.remove(input_data.output_id)

            for output in tx_data.outputs:
                output_data = output.get_data()
                if output_data.receiver_id == user.get_data().id:
                    free_outputs_set.add(output_data.id)

        return free_outputs_set

    @staticmethod
    def _find_connected_with_user_txs(blockchain: Blockchain, user: User) -> list[Transaction]:
        blockchain_data: BlockchainData = blockchain.get_data()
        blocks: list[Block] = blockchain_data.blocks

        result: list[Transaction] = []

        for block in blocks:
            block_data = block.get_data()

            for tx in block_data.transactions:
                if TransactionService._tx_suits_for_user(tx=tx, user=user):
                    result.append(tx)

        mem_txs: list[Transaction] = blockchain.get_data().mem_pool
        for tx in mem_txs:
            if TransactionService._tx_suits_for_user(tx=tx, user=user):
                result.append(tx)

        return result

    @staticmethod
    def _tx_suits_for_user(tx: Transaction, user: User) -> bool:
        tx_data: TransactionData = tx.get_data()
        user_data: UserData = user.get_data()

        for input in tx_data.inputs:
            if input.is_user_owner(user=user):
                return True

        for output in tx_data.outputs:
            output_data: OutputData = output.get_data()
            if output_data.receiver_id == user_data.id:
                return True

        return False
from uuid import UUID

from src.new_version.bitcoin import Bitcoin
from src.service.user_service import UserService


# Reject duplicate UTXO usage (double spend)
def test_reject_double_spending():
    amount_of_users, amount_of_shards, block_capacity = 10, 2, 100

    bitcoin = Bitcoin(amount_of_shards=amount_of_shards, block_capacity=block_capacity)
    users = [bitcoin.create_user() for _ in range(amount_of_users)]
    groups = UserService.group_users_by_shards(users=users, amount_of_shards=amount_of_shards)

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_to_all_users()
        bitcoin.handle_shards()

    users_in_shard, shard_numb = ([groups[0][0], groups[0][1]], 0) if len(groups[0]) >= 2 else (
        [groups[1][0], groups[1][1]], 1)

    for _ in range(block_capacity):
        bitcoin.send_money(from_user=users_in_shard[0].get_data().id,
                           to_user=users_in_shard[1].get_data().id,
                           money=0.1,
                           fee=0.01)

    assert bitcoin.try_to_handle_new_blocks()

    outputs_ids: set[UUID] = set()

    for block in bitcoin.get_blocks_in_shard(shard_num=shard_numb):
        for tx in block.get_data().transactions:
            for input in tx.get_data().inputs:
                id = input.get_data().output_id

                assert id not in outputs_ids

                outputs_ids.add(id)
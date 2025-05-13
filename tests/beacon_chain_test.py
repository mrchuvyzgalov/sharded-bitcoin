from src.new_version.bitcoin import Bitcoin
from src.service.user_service import UserService


# Accept valid snapshot in Beacon Chain
def test_beacon_accepts_valid_snapshot():
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

    last_beacon_block = bitcoin.get_beacon_blocks()[-1]
    last_block_hash = bitcoin.get_blocks_in_shard(shard_num=shard_numb)[-1].calculate_hash()

    cl = last_beacon_block.get_data().cross_links
    assert len(cl) == 2

    has_block = False

    for cl in last_beacon_block.get_data().cross_links:
        if cl.get_data().shard_id == shard_numb:
            has_block = last_block_hash == cl.get_data().hash_block
            print(last_block_hash, cl.get_data().hash_block)
            break

    assert has_block


# Verify cross-shard transaction presence in snapshot
def test_cross_shard_tx_in_snapshot():
    amount_of_users, amount_of_shards, block_capacity = 10, 2, 100

    bitcoin = Bitcoin(amount_of_shards=amount_of_shards, block_capacity=block_capacity)
    users = [bitcoin.create_user() for _ in range(amount_of_users)]
    groups = UserService.group_users_by_shards(users=users, amount_of_shards=amount_of_shards)

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_to_all_users()
        bitcoin.handle_shards()

    user_1, user_2 = groups[0][0], groups[1][0]
    bitcoin.send_money(from_user=user_1.get_data().id,
                       to_user=user_2.get_data().id,
                       money=0.1,
                       fee=0.01)

    bitcoin.handle_shards()

    last_block = bitcoin.get_beacon_blocks()[-1]
    ctx_exists = False

    for cl in last_block.get_data().cross_links:
        if cl.get_data().shard_id == 0:
            ctx = cl.get_data().cross_txs
            ctx_exists = True

            assert len(ctx) == 1
            assert ctx[0].get_data().shard_from == 0
            assert ctx[0].get_data().shard_to == 1

            break

    assert ctx_exists
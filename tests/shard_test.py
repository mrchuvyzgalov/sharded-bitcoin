from src.config.constance import Constants
from src.new_version.bitcoin import Bitcoin
from src.service.user_service import UserService


# Create local block with valid transactions
def test_create_local_block_with_valid_tx():
    amount_of_users, amount_of_shards, block_capacity = 10, 2, 100

    bitcoin = Bitcoin(amount_of_shards=amount_of_shards, block_capacity=block_capacity)
    users = [bitcoin.create_user() for _ in range(amount_of_users)]
    groups = UserService.group_users_by_shards(users=users, amount_of_shards=amount_of_shards)

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_to_all_users()
        bitcoin.handle_shards()

    users_in_shard, shard_numb = ([groups[0][0], groups[0][1]], 0) if len(groups[0]) >= 2 else ([groups[1][0], groups[1][1]], 1)

    assert len(bitcoin.get_blocks_in_shard(shard_num=shard_numb)) == 3

    for _ in range(block_capacity):
        bitcoin.send_money(from_user=users_in_shard[0].get_data().id,
                           to_user=users_in_shard[1].get_data().id,
                           money=0.1,
                           fee=0.01)

    assert bitcoin.try_to_handle_new_blocks()
    assert len(bitcoin.get_blocks_in_shard(shard_num=shard_numb)) == 4


# Update UTXO after local transaction
def test_utxo_update_after_local_transaction():
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

    bitcoin.send_money(from_user=users_in_shard[0].get_data().id,
                       to_user=users_in_shard[1].get_data().id,
                       money=0.1,
                       fee=0.01)

    txs = bitcoin.get_mempool_in_shard(shard_num=shard_numb)

    input_exist: bool = False
    output_exist: bool = False

    for tx in txs:
        for input in tx.get_data().inputs:
            if input.get_data().signature == users_in_shard[0].sign():
                input_exist = True
                break

        for output in tx.get_data().outputs:
            if output.get_data().receiver_id == users_in_shard[1].get_data().id:
                output_exist = True
                break

    assert input_exist and output_exist


# Generate valid block snapshot
def test_generate_valid_block_snapshot():
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

    assert len(bitcoin.get_beacon_blocks()) == 3

    for _ in range(block_capacity):
        bitcoin.send_money(from_user=users_in_shard[0].get_data().id,
                           to_user=users_in_shard[1].get_data().id,
                           money=0.1,
                           fee=0.01)

    assert bitcoin.try_to_handle_new_blocks()

    blocks = bitcoin.get_beacon_blocks()
    assert len(blocks) == 4

    is_the_first_block: bool = False
    is_the_second_block: bool = False

    for cross_link in blocks[-1].get_data().cross_links:
        if cross_link.get_data().shard_id == 0:
            is_the_first_block = True
        if cross_link.get_data().shard_id == 1:
            is_the_second_block = True

    return (is_the_first_block and is_the_second_block
            and len(blocks[-1].get_data().cross_links) == 2)


# Reject invalid transaction
def test_reject_invalid_transaction():
    amount_of_users, amount_of_shards, block_capacity = 10, 2, 100

    bitcoin = Bitcoin(amount_of_shards=amount_of_shards, block_capacity=block_capacity)
    users = [bitcoin.create_user() for _ in range(amount_of_users)]
    groups = UserService.group_users_by_shards(users=users, amount_of_shards=amount_of_shards)

    bitcoin.set_validators()

    for _ in range(2):
        bitcoin.add_reward_to_all_users()
        bitcoin.handle_shards()

    user_1, user_2 = groups[0][0], groups[1][0]
    is_sent = bitcoin.send_money(from_user=user_1.get_data().id,
                                 to_user=user_2.get_data().id,
                                 money=1000000000000,
                                 fee=0.01)

    assert not is_sent

# Validate block hash integrity
def test_block_hash_integrity():
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

    last_block = bitcoin.get_blocks_in_shard(shard_num=shard_numb)[-1]
    assert last_block.calculate_hash().startswith(Constants.POW_PREFIX)
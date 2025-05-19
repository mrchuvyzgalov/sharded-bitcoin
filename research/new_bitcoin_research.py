from research.launch.new_bitcoin_launch import LaunchNewBitcoinData, launch_best_new_bitcoin, launch_random_new_bitcoin, \
    launch_worst_new_bitcoin


def research_best_case(amount_of_shards: int) -> dict[int, float]:
    AMOUNT_OF_USERS = 30
    BLOCK_CAPACITY = 100
    AMOUNT_OF_BLOCKS = 3

    result: dict[int, float] = {}

    for amount_of_blocks in range(1, AMOUNT_OF_BLOCKS + 1):
        data: LaunchNewBitcoinData = launch_best_new_bitcoin(amount_of_blocks=amount_of_blocks,
                                                             amount_of_users=AMOUNT_OF_USERS,
                                                             block_capacity=BLOCK_CAPACITY,
                                                             amount_of_shards=amount_of_shards)

        result[amount_of_blocks] = data.amount_of_transactions / data.time

    return result

def research_random_case(amount_of_shards: int) -> dict[int, float]:
    AMOUNT_OF_USERS = 30
    BLOCK_CAPACITY = 100
    AMOUNT_OF_BLOCKS = 3

    result: dict[int, float] = {}

    for amount_of_blocks in range(1, AMOUNT_OF_BLOCKS + 1):
        data: LaunchNewBitcoinData = launch_random_new_bitcoin(amount_of_blocks=amount_of_blocks,
                                                               amount_of_users=AMOUNT_OF_USERS,
                                                               block_capacity=BLOCK_CAPACITY,
                                                               amount_of_shards=amount_of_shards)

        result[amount_of_blocks] = data.amount_of_transactions / data.time

    return result

def research_worst_case(amount_of_shards: int) -> dict[int, float]:
    AMOUNT_OF_USERS = 30
    BLOCK_CAPACITY = 100
    AMOUNT_OF_BLOCKS = 3

    result: dict[int, float] = {}

    for amount_of_blocks in range(1, AMOUNT_OF_BLOCKS + 1):
        data: LaunchNewBitcoinData = launch_worst_new_bitcoin(amount_of_blocks=amount_of_blocks,
                                                              amount_of_users=AMOUNT_OF_USERS,
                                                              block_capacity=BLOCK_CAPACITY,
                                                              amount_of_shards=amount_of_shards)

        result[amount_of_blocks] = data.amount_of_transactions / data.time

    return result
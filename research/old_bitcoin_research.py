from research.launch.old_bitcoin_launch import launch_bitcoin, LaunchOldBitcoinData


def research() -> dict[int, float]:
    AMOUNT_OF_USERS = 100
    BLOCK_CAPACITY = 100
    AMOUNT_OF_BLOCKS = 5

    result: dict[int, float] = {}

    for amount_of_blocks in range(1, AMOUNT_OF_BLOCKS + 1):
        print(f"Amount of blocks: {amount_of_blocks}")

        data: LaunchOldBitcoinData = launch_bitcoin(amount_of_blocks=amount_of_blocks,
                                                    amount_of_users=AMOUNT_OF_USERS,
                                                    block_capacity=BLOCK_CAPACITY)

        result[amount_of_blocks] = data.amount_of_transactions / data.time

    return result
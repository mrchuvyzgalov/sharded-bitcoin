from uuid import UUID


class ShardService:
    @staticmethod
    def get_shard_number_by_user(user_id: UUID, amount_of_shards: int) -> int:
        return user_id.int % amount_of_shards
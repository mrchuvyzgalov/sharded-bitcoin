from dataclasses import dataclass
from uuid import UUID

from common.blockchain import Blockchain
from common.user import User


@dataclass(frozen=True)
class Basic:
    FIRST_USER = User(UUID(hex="a8098c1af86e11dabd1a00112444be1e"))
    BASIC_BLOCKCHAIN = Blockchain(owner=FIRST_USER)
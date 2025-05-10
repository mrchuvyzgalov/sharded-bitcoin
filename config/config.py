from dataclasses import dataclass
from uuid import UUID

from common.user import User


@dataclass(frozen=True)
class Basic:
    FIRST_USER = User(UUID(hex="a8098c1af86e11dabd1a00112444be1e"))
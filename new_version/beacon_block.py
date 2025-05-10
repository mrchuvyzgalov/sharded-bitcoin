import hashlib
from collections import namedtuple
from typing import Optional

from new_version.cross_link import CrossLink

BeaconBlockData = namedtuple("BeaconBlockData", ["cross_links", "previous_hash"])

class BeaconBlock:
    def __init__(self) -> None:
        self._nonce = 0
        self._cross_links: list[CrossLink] = []
        self._previous_hash: Optional[str] = None

    def __str__(self) -> str:
        return str(self.get_data())

    def get_data(self) -> BeaconBlockData:
        return BeaconBlockData(cross_links=self._cross_links,
                               previous_hash=self._previous_hash)

    def set_previous_hash(self, previous_hash: str) -> None:
        self._previous_hash = previous_hash

    def inc_nonce(self) -> None:
        self._nonce += 1

    def add_cross_link(self, cl: CrossLink) -> None:
        self._cross_links.append(cl)

    def calculate_hash(self) -> str:
        cl_hash = self._calculate_cl_hash()
        hash_line = f"{self._nonce}-{cl_hash}-{self._previous_hash}"
        return hashlib.sha256(hash_line.encode()).hexdigest()

    def _calculate_cl_hash(self) -> str:
        hash_line = ""

        for cl in self._cross_links:
            hash_line += f"{cl.calculate_hash()}"

        return hashlib.sha256(hash_line.encode()).hexdigest()
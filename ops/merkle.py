import hashlib
from typing import List

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def merkle_root(leaves: List[str]) -> str:
    if not leaves:
        return sha256_hex(b"")

    level = [bytes.fromhex(x.removeprefix("0x")) for x in leaves]

    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        level = [
            hashlib.sha256(level[i] + level[i + 1]).digest()
            for i in range(0, len(level), 2)
        ]

    return level[0].hex()

import hashlib
from typing import Any, Union
import json

def calculate_hash(data: Any) -> str:
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    elif not isinstance(data, str):
        data = str(data)
    data_bytes = data.encode("utf-8")
    return hashlib.sha256(data_bytes).hexdigest()

def double_sha256(data: Union[str, bytes]) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    first_hash = hashlib.sha256(data).digest()
    return hashlib.sha256(first_hash).hexdigest()

def merkle_root(items: list) -> str:
    if not items:
        return double_sha256("")
    hashes = [calculate_hash(item) for item in items]
    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        next_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i+1]
            next_hash = calculate_hash(combined)
            next_level.append(next_hash)
        hashes = next_level
    return hashes[0]

def create_block_hash(index: int, timestamp: float, transactions: list, previous_hash: str, nonce: int) -> str:
    tx_root = merkle_root(transactions)
    block_data = {
        "index": index,
        "timestamp": timestamp,
        "transactions_root": tx_root,
        "previous_hash": previous_hash,
        "nonce": nonce
    }
    return calculate_hash(block_data)

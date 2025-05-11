from triadnet.typing import List

def calculate_reward(transactions: List, depth: int) -> float:
    base_reward = 10.0
    tx_volume = len(transactions)
    level_factor = depth + 1
    return base_reward + 0.1 * tx_volume * level_factor

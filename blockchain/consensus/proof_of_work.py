from dataclasses import dataclass
import time
import hashlib
import random
from typing import List, Optional, Dict, Tuple
import logging
from ..core.block import Block
from ..core.transaction import Transaction
from ..core.fractal_coordinate import FractalCoordinate
from ..core.blockchain import Blockchain

BLOCK_REWARD = 50
TARGET_BLOCK_TIME = 60
DIFFICULTY_ADJUSTMENT_INTERVAL = 10
MAX_TRANSACTIONS_PER_BLOCK = 100

@dataclass
class MiningResult:
    success: bool
    hash_val: str = ""
    nonce: int = 0
    duration: float = 0
    block: Optional[Block] = None

class ProofOfFractalWork:
    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty
        self.target = "0" * difficulty
        self.logger = logging.getLogger("triadnet.consensus")
        
    def _calculate_fractal_score(self, coord: FractalCoordinate) -> float:
        base_score = (coord.a + coord.b + coord.c) / 1000.0
        return max(0.1, min(2.0, base_score))
        
    def _adjust_difficulty(self, last_block_time: float, fractal_score: float) -> None:
        time_ratio = TARGET_BLOCK_TIME / max(1, last_block_time)
        difficulty_delta = time_ratio * fractal_score
        if difficulty_delta > 1.2:
            self.difficulty += 1
        elif difficulty_delta < 0.8:
            self.difficulty = max(1, self.difficulty - 1)
        self.target = "0" * self.difficulty
            
    def mine_block(self, block: Block, max_nonce: int = 1000000) -> MiningResult:
        start_time = time.time()
        fractal_score = self._calculate_fractal_score(block.fractal_coord)
        nonce = 0
        while nonce < max_nonce:
            block.nonce = nonce
            block_hash = block.calculate_hash()
            if block_hash.startswith(self.target):
                duration = time.time() - start_time
                block.hash = block_hash  # Set the block hash
                self._adjust_difficulty(duration, fractal_score)
                self.logger.info(
                    f"Block mined! Hash: {block_hash[:10]}... "
                    f"Nonce: {nonce} Time: {duration:.2f}s "
                    f"Difficulty: {self.difficulty}"
                )
                return MiningResult(
                    success=True,
                    hash_val=block_hash,
                    nonce=nonce,
                    duration=duration,
                    block=block
                )
            nonce += 1
        duration = time.time() - start_time
        return MiningResult(success=False, duration=duration)

class ConsensusManager:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain
        self.pofw = ProofOfFractalWork(difficulty=blockchain.difficulty)
        self.logger = logging.getLogger("triadnet.consensus")
        
    def create_block(self, miner_address: str, fractal_coord: FractalCoordinate) -> Block:
        last_block = self.blockchain.last_block
        transactions = self.blockchain.pending_transactions[:MAX_TRANSACTIONS_PER_BLOCK]
        reward_tx = Transaction(
            sender="network",
            receiver=miner_address,
            amount=BLOCK_REWARD,
            data="Mining Reward"
        )
        transactions.append(reward_tx)
        new_block = Block(
            index=last_block.index + 1 if last_block else 0,
            timestamp=time.time(),
            transactions=transactions,
            previous_hash=last_block.hash if last_block else "0" * 64,
            miner=miner_address,
            fractal_coord=fractal_coord
        )
        return new_block
        
    def mine_block(self, block: Block) -> MiningResult:
        result = self.pofw.mine_block(block)
        if result.success:
            if self.blockchain.add_block(result.block):  # Use result.block which has the hash set
                mined_tx_ids = {tx.tx_id for tx in block.transactions}
                self.blockchain.pending_transactions = [
                    tx for tx in self.blockchain.pending_transactions 
                    if tx.tx_id not in mined_tx_ids
                ]
                self.logger.info(f"Block {block.index} added to chain")
            else:
                result.success = False
                self.logger.warning("Block validation failed")
        return result

# triadnet/mine.py

import time
import logging
from typing import List, Optional, Dict
from dataclasses import dataclass, field
from queue import Queue
import threading
from datetime import datetime

from .core.blockchain import Blockchain
from .core.block import Block
from .core.transaction import Transaction
from .core.wallet import Wallet
from .core.fractal_coordinate import FractalCoordinate
from .consensus.proof_of_work import ProofOfFractalWork, ConsensusManager, BLOCK_REWARD
from .crypto.hashing import calculate_hash

@dataclass
class MiningStats:
    blocks_mined: int = 0
    total_time: float = 0
    total_reward: float = 0
    start_time: float = field(default_factory=time.time)
    last_block_time: float = 0
    hash_rate: float = 0
    
    def update_block_mined(self, reward: float):
        self.blocks_mined += 1
        self.total_reward += reward
        current_time = time.time()
        block_time = current_time - self.last_block_time if self.last_block_time else 0
        self.total_time = current_time - self.start_time
        self.last_block_time = current_time
        self.hash_rate = (self.blocks_mined / self.total_time) * 3600 if self.total_time > 0 else 0

class Miner:
    def __init__(self, 
                 wallet: Wallet,
                 blockchain: Blockchain,
                 fractal_coord: FractalCoordinate,
                 auto_adjust_coords: bool = True):
        self.wallet = wallet
        self.blockchain = blockchain
        self.fractal_coord = fractal_coord
        self.auto_adjust_coords = auto_adjust_coords
        
        # Initialize consensus
        self.consensus = ConsensusManager(blockchain)
        
        # Initialize mining state
        self._mining = False
        self._mining_thread: Optional[threading.Thread] = None
        self._pending_transactions: Queue = Queue()
        self.stats = MiningStats()
        
        # Setup logging
        self.logger = logging.getLogger('triadnet.miner')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"Miner initialized with address {wallet.address}")
        self.logger.info(f"Initial fractal coordinates: {fractal_coord}")

    def start(self):
        if not self._mining:
            self._mining = True
            self._mining_thread = threading.Thread(target=self._mine_loop)
            self._mining_thread.daemon = True
            self._mining_thread.start()
            self.logger.info(f"Mining started at coordinates {self.fractal_coord}")
    
    def stop(self):
        if self._mining:
            self._mining = False
            if self._mining_thread:
                self._mining_thread.join()
            self.logger.info("Mining stopped")
    
    def add_transaction(self, transaction: Transaction):
        self._pending_transactions.put(transaction)
        self.blockchain.add_pending_transaction(transaction)
        self.logger.debug(f"Added transaction to pool: {transaction.tx_id}")

    def _mine_loop(self):
        while self._mining:
            try:
                # Create new block
                block = self.consensus.create_block(
                    miner_address=self.wallet.address,
                    fractal_coord=self.fractal_coord
                )
                
                # Try to mine it
                self.logger.info(f"Mining block {block.index} with {len(block.transactions)} transactions...")
                result = self.consensus.mine_block(block)
                
                if result.success:
                    self.stats.update_block_mined(BLOCK_REWARD)
                    self.logger.info(
                        f"Block mined! Hash: {result.hash_val[:10]}... "
                        f"Nonce: {result.nonce} Time: {result.duration:.2f}s "
                        f"Reward: {BLOCK_REWARD} TRIAD"
                    )
                    
                    # Adjust coordinates if needed
                    if self.auto_adjust_coords:
                        self._adjust_fractal_coordinates(result.duration)
                else:
                    self.logger.warning(
                        f"Failed to mine block after {result.duration:.2f}s, "
                        "adjusting parameters and retrying..."
                    )
                    time.sleep(1)  # Brief pause before retrying
                    
            except Exception as e:
                self.logger.error(f"Mining error: {str(e)}")
                time.sleep(5)  # Longer pause on error

    def _adjust_fractal_coordinates(self, last_block_time: float):
        if not self.auto_adjust_coords:
            return
            
        # If mining took too long, try to find an easier spot
        if last_block_time > 120:  # If it took more than 2 minutes
            self.fractal_coord = FractalCoordinate(
                a=self.fractal_coord.a + 50,
                b=self.fractal_coord.b + 50,
                c=self.fractal_coord.c + 50
            )
            self.logger.info(f"Adjusted coordinates to find easier mining spot: {self.fractal_coord}")
            
        # If mining was very fast, try to find a more challenging spot
        elif last_block_time < 10:  # If it took less than 10 seconds
            self.fractal_coord = FractalCoordinate(
                a=max(0, self.fractal_coord.a - 50),
                b=max(0, self.fractal_coord.b - 50),
                c=max(0, self.fractal_coord.c - 50)
            )
            self.logger.info(f"Adjusted coordinates to find more challenging spot: {self.fractal_coord}")

    def get_status(self) -> Dict[str, any]:
        return {
            "active": self._mining,
            "address": self.wallet.address,
            "fractal_coordinates": {
                "a": self.fractal_coord.a,
                "b": self.fractal_coord.b,
                "c": self.fractal_coord.c
            },
            "difficulty": self.consensus.pofw.difficulty,
            "pending_transactions": self._pending_transactions.qsize(),
            "stats": {
                "blocks_mined": self.stats.blocks_mined,
                "total_time": f"{self.stats.total_time:.2f}s",
                "total_reward": f"{self.stats.total_reward:.2f} TRIAD",
                "hash_rate": f"{self.stats.hash_rate:.2f} blocks/hour",
                "mining_start": datetime.fromtimestamp(self.stats.start_time).strftime('%Y-%m-%d %H:%M:%S'),
                "last_block": datetime.fromtimestamp(self.stats.last_block_time).strftime('%Y-%m-%d %H:%M:%S') if self.stats.last_block_time else "Never"
            },
            "chain_height": len(self.blockchain.chain),
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }

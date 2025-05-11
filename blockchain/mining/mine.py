import time
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from queue import Queue
import threading
from datetime import datetime
from threading import Lock

from blockchain.core.blockchain import Blockchain
from blockchain.core.block import Block
from blockchain.core.transaction import Transaction
from blockchain.wallet import Wallet
from blockchain.core.fractal_coordinate import FractalCoordinate
from blockchain.mining.proof_of_work import (
    ProofOfFractalWork, ConsensusManager, BLOCK_REWARD, MiningError
)

# Mining constants
MAX_RETRIES = 5  # Maximum mining retries before aggressive adjustment
INITIAL_BACKOFF = 1  # Initial backoff time in seconds
MAX_BACKOFF = 30  # Maximum backoff time in seconds
COORD_ADJUST_STEP = 50  # Standard coordinate adjustment step
AGGRESSIVE_ADJUST_STEP = 100  # Aggressive coordinate adjustment step
SLOW_BLOCK_TIME = 120  # Time threshold for "too slow" mining (seconds)
FAST_BLOCK_TIME = 10  # Time threshold for "too fast" mining (seconds)

class MinerError(Exception):
    """Base exception for miner-related errors."""
    pass

class MiningStatsError(MinerError):
    """Raised when mining stats operations fail."""
    pass

@dataclass
class MiningStats:
    """
    Statistics for mining operations.
    
    Tracks various metrics about mining performance including:
    - Number of blocks mined
    - Total mining time
    - Total rewards earned
    - Mining start time
    - Last block time
    - Hash rate
    
    Thread-safe for updates.
    """
    
    blocks_mined: int = 0
    total_time: float = 0
    total_reward: float = 0
    start_time: float = field(default_factory=time.time)
    last_block_time: float = 0
    hash_rate: float = 0
    _lock: Lock = field(default_factory=Lock, init=False)
    
    def update_block_mined(self, reward: float) -> None:
        """
        Update statistics after mining a block.
        
        Thread-safe update of all mining statistics.
        
        Args:
            reward (float): Mining reward for the block
            
        Raises:
            MiningStatsError: If update fails
        """
        try:
            with self._lock:
                self.blocks_mined += 1
                self.total_reward += reward
                current_time = time.time()
                self.total_time = current_time - self.start_time
                self.last_block_time = current_time
                self.hash_rate = (self.blocks_mined / self.total_time) * 3600 if self.total_time > 0 else 0
        except Exception as e:
            raise MiningStatsError(f"Failed to update mining stats: {str(e)}")

class Miner:
    """
    Cryptocurrency miner implementation.
    
    Handles the mining process including:
    - Block creation and mining
    - Transaction management
    - Mining statistics
    - Fractal coordinate adjustment
    
    Thread-safe for all operations.
    """
    
    def __init__(
        self, 
        wallet: Wallet,
        blockchain: Blockchain,
        fractal_coord: FractalCoordinate,
        auto_adjust_coords: bool = True
    ):
        """
        Initialize the miner.
        
        Args:
            wallet (Wallet): Miner's wallet for rewards
            blockchain (Blockchain): Blockchain to mine on
            fractal_coord (FractalCoordinate): Initial mining coordinates
            auto_adjust_coords (bool): Whether to auto-adjust coordinates
            
        Raises:
            MinerError: If initialization fails
        """
        if not isinstance(wallet, Wallet):
            raise MinerError("Invalid wallet type")
        if not isinstance(blockchain, Blockchain):
            raise MinerError("Invalid blockchain type")
        if not isinstance(fractal_coord, FractalCoordinate):
            raise MinerError("Invalid fractal coordinates")
            
        self.wallet = wallet
        self.blockchain = blockchain
        self.fractal_coord = fractal_coord
        self.auto_adjust_coords = auto_adjust_coords
        self.consensus = ConsensusManager(blockchain)
        
        self._mining = False
        self._mining_thread: Optional[threading.Thread] = None
        self._pending_transactions: Queue = Queue()
        self._coord_lock = Lock()
        
        self.stats = MiningStats()
        self.logger = logging.getLogger("triadnet.miner")
        
        # Configure logging
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(
            f"Miner initialized with address {wallet.address} "
            f"at coordinates {fractal_coord}"
        )

    def start(self) -> None:
        """
        Start mining operations.
        
        Launches mining in a separate thread if not already running.
        
        Raises:
            MinerError: If mining start fails
        """
        try:
            if not self._mining:
                self._mining = True
                self._mining_thread = threading.Thread(target=self._mine_loop)
                self._mining_thread.daemon = True
                self._mining_thread.start()
                self.logger.info(f"Mining started at coordinates {self.fractal_coord}")
        except Exception as e:
            self._mining = False
            raise MinerError(f"Failed to start mining: {str(e)}")
    
    def stop(self) -> None:
        """
        Stop mining operations.
        
        Gracefully stops the mining thread and waits for completion.
        
        Raises:
            MinerError: If mining stop fails
        """
        try:
            if self._mining:
                self._mining = False
                if self._mining_thread:
                    self._mining_thread.join(timeout=5.0)
                self.logger.info("Mining stopped")
        except Exception as e:
            raise MinerError(f"Failed to stop mining: {str(e)}")
    
    def add_transaction(self, transaction: Transaction) -> None:
        """
        Add a transaction to the mining pool.
        
        Args:
            transaction (Transaction): Transaction to add
            
        Raises:
            MinerError: If transaction addition fails
        """
        try:
            if not isinstance(transaction, Transaction):
                raise MinerError("Invalid transaction type")
                
            self._pending_transactions.put(transaction)
            self.blockchain.add_pending_transaction(transaction)
            self.logger.debug(f"Added transaction to pool: {transaction.tx_id}")
            
        except Exception as e:
            raise MinerError(f"Failed to add transaction: {str(e)}")

    def _mine_loop(self) -> None:
        """
        Main mining loop.
        
        Continuously mines blocks until stopped, handling retries and
        coordinate adjustments as needed.
        """
        retry_count = 0
        backoff_time = INITIAL_BACKOFF
        
        while self._mining:
            try:
                block = self.consensus.create_block(
                    miner_address=self.wallet.address,
                    fractal_coord=self.fractal_coord
                )
                
                self.logger.info(
                    f"Mining block {block.index} with "
                    f"{len(block.transactions)} transactions..."
                )
                
                result = self.consensus.mine_block(block)
                
                if result.success:
                    self.stats.update_block_mined(BLOCK_REWARD)
                    self.logger.info(
                        f"Block {block.index} mined! "
                        f"Hash: {result.hash_val[:10]}... "
                        f"Nonce: {result.nonce} "
                        f"Time: {result.duration:.2f}s "
                        f"Reward: {BLOCK_REWARD} TRIAD"
                    )
                    
                    if self.auto_adjust_coords:
                        self._adjust_fractal_coordinates(result.duration)
                        
                    retry_count = 0
                    backoff_time = INITIAL_BACKOFF
                    
                else:
                    self.logger.warning(
                        f"Failed to mine block after {result.duration:.2f}s, "
                        "adjusting parameters and retrying..."
                    )
                    
                    retry_count += 1
                    if retry_count > MAX_RETRIES:
                        self.logger.info(
                            "Max retries reached, adjusting coordinates aggressively"
                        )
                        with self._coord_lock:
                            self.fractal_coord = FractalCoordinate(
                                a=max(0, self.fractal_coord.a + AGGRESSIVE_ADJUST_STEP),
                                b=max(0, self.fractal_coord.b + AGGRESSIVE_ADJUST_STEP),
                                c=max(0, self.fractal_coord.c + AGGRESSIVE_ADJUST_STEP)
                            )
                        retry_count = 0
                        backoff_time = INITIAL_BACKOFF
                    else:
                        time.sleep(backoff_time)
                        backoff_time = min(backoff_time * 2, MAX_BACKOFF)
                        
            except Exception as e:
                self.logger.error(f"Mining error: {str(e)}")
                time.sleep(5)

    def _adjust_fractal_coordinates(self, last_block_time: float) -> None:
        """
        Adjust mining coordinates based on mining performance.
        
        Args:
            last_block_time (float): Time taken to mine last block
            
        Thread-safe coordinate adjustment.
        """
        if not self.auto_adjust_coords:
            return
            
        try:
            with self._coord_lock:
                if last_block_time > SLOW_BLOCK_TIME:
                    # Mining too slow, move to easier spot
                    self.fractal_coord = FractalCoordinate(
                        a=self.fractal_coord.a + COORD_ADJUST_STEP,
                        b=self.fractal_coord.b + COORD_ADJUST_STEP,
                        c=self.fractal_coord.c + COORD_ADJUST_STEP
                    )
                    self.logger.info(
                        f"Adjusted coordinates for easier mining: {self.fractal_coord}"
                    )
                elif last_block_time < FAST_BLOCK_TIME:
                    # Mining too fast, move to harder spot
                    self.fractal_coord = FractalCoordinate(
                        a=max(0, self.fractal_coord.a - COORD_ADJUST_STEP),
                        b=max(0, self.fractal_coord.b - COORD_ADJUST_STEP),
                        c=max(0, self.fractal_coord.c - COORD_ADJUST_STEP)
                    )
                    self.logger.info(
                        f"Adjusted coordinates for harder mining: {self.fractal_coord}"
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to adjust coordinates: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current miner status and statistics.
        
        Returns:
            Dict[str, Any]: Dictionary containing current miner status
            
        Raises:
            MinerError: If status collection fails
        """
        try:
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
                    "mining_start": datetime.fromtimestamp(
                        self.stats.start_time
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "last_block": (
                        datetime.fromtimestamp(
                            self.stats.last_block_time
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        if self.stats.last_block_time else "Never"
                    )
                },
                "chain_height": len(self.blockchain.chain),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            raise MinerError(f"Failed to get miner status: {str(e)}")

from dataclasses import dataclass, field
import time
import hashlib
import random
from typing import List, Optional, Dict, Tuple, Set
import logging
from ..core.block import Block
from ..core.transaction import Transaction
from ..core.fractal_coordinate import FractalCoordinate
from ..core.blockchain import Blockchain, BlockchainError

# Mining constants
BLOCK_REWARD = 50  # Reward for mining a block
TARGET_BLOCK_TIME = 60  # Target time between blocks in seconds
DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # Number of blocks between difficulty adjustments
MAX_TRANSACTIONS_PER_BLOCK = 100  # Maximum transactions in a block
MIN_DIFFICULTY = 1  # Minimum mining difficulty
MAX_DIFFICULTY = 32  # Maximum mining difficulty
DEFAULT_MAX_NONCE = 1_000_000  # Default maximum nonce value for mining attempts

# Fractal score constants
BASE_WEIGHT_A = 0.4  # Weight for coordinate a in fractal score
BASE_WEIGHT_B = 0.4  # Weight for coordinate b in fractal score
BASE_WEIGHT_C = 0.2  # Weight for coordinate c in fractal score
NOISE_RANGE = 0.1  # Range for random noise in fractal score
MIN_SCORE = 0.1  # Minimum allowed fractal score
MAX_SCORE = 2.0  # Maximum allowed fractal score

class MiningError(Exception):
    """Base exception for mining-related errors."""
    pass

class DifficultyError(MiningError):
    """Raised when difficulty validation fails."""
    pass

class BlockMiningError(MiningError):
    """Raised when block mining fails."""
    pass

@dataclass
class MiningResult:
    """
    Result of a block mining attempt.
    
    Attributes:
        success (bool): Whether mining was successful
        hash_val (str): Hash of the mined block (if successful)
        nonce (int): Nonce that produced the valid hash
        duration (float): Time taken to mine in seconds
        block (Optional[Block]): The mined block (if successful)
    """
    success: bool
    hash_val: str = ""
    nonce: int = 0
    duration: float = 0
    block: Optional[Block] = None

class ProofOfFractalWork:
    """
    Implementation of Proof of Fractal Work consensus algorithm.
    
    This algorithm combines traditional proof of work with fractal coordinates
    to create a unique mining challenge that adapts based on network conditions
    and mining patterns in fractal space.
    """
    
    def __init__(self, difficulty: int = 4):
        """
        Initialize the proof of work system.
        
        Args:
            difficulty (int): Initial mining difficulty (number of leading zeros required)
            
        Raises:
            DifficultyError: If difficulty is invalid
        """
        if not isinstance(difficulty, int):
            raise DifficultyError("Difficulty must be an integer")
        if not MIN_DIFFICULTY <= difficulty <= MAX_DIFFICULTY:
            raise DifficultyError(
                f"Difficulty must be between {MIN_DIFFICULTY} and {MAX_DIFFICULTY}"
            )
            
        self.difficulty = difficulty
        self.target = "0" * difficulty
        self.logger = logging.getLogger("triadnet.consensus")
        self.logger.info(f"Initialized PoFW with difficulty {difficulty}")
        
    def _calculate_fractal_score(self, coord: FractalCoordinate) -> float:
        """
        Calculate a mining score based on fractal coordinates.
        
        The score is calculated using weighted coordinates plus random noise
        to add variability to mining difficulty.
        
        Args:
            coord (FractalCoordinate): The coordinates to evaluate
            
        Returns:
            float: Score between MIN_SCORE and MAX_SCORE
            
        Raises:
            MiningError: If score calculation fails
        """
        try:
            base_score = (
                coord.a * BASE_WEIGHT_A +
                coord.b * BASE_WEIGHT_B +
                coord.c * BASE_WEIGHT_C
            ) / 1000.0
            
            noise = random.uniform(-NOISE_RANGE, NOISE_RANGE)
            score = max(MIN_SCORE, min(MAX_SCORE, base_score + noise))
            
            self.logger.debug(
                f"Fractal score: {score:.3f} "
                f"(base: {base_score:.3f}, noise: {noise:.3f})"
            )
            return score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate fractal score: {str(e)}")
            raise MiningError(f"Fractal score calculation failed: {str(e)}")
        
    def _adjust_difficulty(self, last_block_time: float, fractal_score: float) -> None:
        """
        Adjust mining difficulty based on last block time and fractal score.
        
        Args:
            last_block_time (float): Time taken to mine last block
            fractal_score (float): Score from fractal coordinates
            
        Raises:
            DifficultyError: If adjustment calculation fails
        """
        try:
            if last_block_time <= 0:
                raise DifficultyError("Block time must be positive")
                
            time_ratio = TARGET_BLOCK_TIME / max(1, last_block_time)
            difficulty_delta = time_ratio * fractal_score
            
            old_difficulty = self.difficulty
            
            # Smooth difficulty adjustment
            if difficulty_delta > 1.1:
                self.difficulty = min(MAX_DIFFICULTY, self.difficulty + 1)
            elif difficulty_delta < 0.9:
                self.difficulty = max(MIN_DIFFICULTY, self.difficulty - 1)
                
            self.target = "0" * self.difficulty
            
            if self.difficulty != old_difficulty:
                self.logger.info(
                    f"Difficulty adjusted from {old_difficulty} to {self.difficulty} "
                    f"(time ratio: {time_ratio:.2f}, fractal score: {fractal_score:.2f})"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to adjust difficulty: {str(e)}")
            raise DifficultyError(f"Difficulty adjustment failed: {str(e)}")
            
    def mine_block(self, block: Block, max_nonce: int = DEFAULT_MAX_NONCE) -> MiningResult:
        """
        Mine a block using proof of fractal work.
        
        Args:
            block (Block): The block to mine
            max_nonce (int): Maximum nonce value to try
            
        Returns:
            MiningResult: Result of the mining attempt
            
        Raises:
            BlockMiningError: If mining fails due to invalid input
        """
        if not isinstance(block, Block):
            raise BlockMiningError("Invalid block type")
            
        if max_nonce <= 0:
            raise BlockMiningError("max_nonce must be positive")
            
        try:
            start_time = time.time()
            fractal_score = self._calculate_fractal_score(block.fractal_coord)
            
            self.logger.info(
                f"Starting to mine block {block.index} "
                f"with difficulty {self.difficulty}"
            )
            
            nonce = 0
            while nonce < max_nonce:
                block.nonce = nonce
                block_hash = block.calculate_hash()
                
                if block_hash.startswith(self.target):
                    duration = time.time() - start_time
                    block.hash = block_hash
                    self._adjust_difficulty(duration, fractal_score)
                    
                    self.logger.info(
                        f"Block {block.index} mined! "
                        f"Hash: {block_hash[:10]}... "
                        f"Nonce: {nonce} "
                        f"Time: {duration:.2f}s "
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
            self.logger.warning(
                f"Failed to mine block {block.index} "
                f"after {max_nonce} attempts in {duration:.2f}s"
            )
            return MiningResult(success=False, duration=duration)
            
        except Exception as e:
            self.logger.error(f"Mining error: {str(e)}")
            raise BlockMiningError(f"Mining failed: {str(e)}")

class ConsensusManager:
    """
    Manages blockchain consensus including block creation and mining.
    
    This class coordinates the proof of work system with the blockchain,
    handling block creation, mining, and chain updates.
    """
    
    def __init__(self, blockchain: Blockchain):
        """
        Initialize the consensus manager.
        
        Args:
            blockchain (Blockchain): The blockchain to manage consensus for
        """
        if not isinstance(blockchain, Blockchain):
            raise MiningError("Invalid blockchain type")
            
        self.blockchain = blockchain
        self.pofw = ProofOfFractalWork(difficulty=blockchain.difficulty)
        self.logger = logging.getLogger("triadnet.consensus")
        
    def create_block(self, miner_address: str, fractal_coord: FractalCoordinate) -> Block:
        """
        Create a new block ready for mining.
        
        Args:
            miner_address (str): Address to receive mining reward
            fractal_coord (FractalCoordinate): Mining coordinates
            
        Returns:
            Block: New block ready for mining
            
        Raises:
            MiningError: If block creation fails
        """
        try:
            if not isinstance(miner_address, str) or not miner_address:
                raise MiningError("Invalid miner address")
                
            if not isinstance(fractal_coord, FractalCoordinate):
                raise MiningError("Invalid fractal coordinates")
                
            last_block = self.blockchain.last_block
            transactions = self.blockchain.pending_transactions[:MAX_TRANSACTIONS_PER_BLOCK]
            
            # Create mining reward transaction
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
            
            self.logger.info(
                f"Created block {new_block.index} "
                f"with {len(transactions)} transactions"
            )
            return new_block
            
        except Exception as e:
            self.logger.error(f"Block creation failed: {str(e)}")
            raise MiningError(f"Failed to create block: {str(e)}")
        
    def mine_block(self, block: Block) -> MiningResult:
        """
        Mine a block and add it to the blockchain if successful.
        
        Args:
            block (Block): The block to mine
            
        Returns:
            MiningResult: Result of the mining attempt
            
        Raises:
            MiningError: If mining or block addition fails
        """
        try:
            result = self.pofw.mine_block(block)
            
            if result.success:
                if self.blockchain.add_block(result.block):
                    # Remove mined transactions from pending pool
                    mined_tx_ids = {tx.tx_id for tx in block.transactions}
                    self.blockchain.pending_transactions = [
                        tx for tx in self.blockchain.pending_transactions 
                        if tx.tx_id not in mined_tx_ids
                    ]
                    self.logger.info(
                        f"Block {block.index} added to chain, "
                        f"removed {len(mined_tx_ids)} transactions from pool"
                    )
                else:
                    result.success = False
                    self.logger.warning(
                        f"Block {block.index} mining succeeded but validation failed"
                    )
                    
            return result
            
        except Exception as e:
            self.logger.error(f"Mining operation failed: {str(e)}")
            raise MiningError(f"Mining operation failed: {str(e)}")

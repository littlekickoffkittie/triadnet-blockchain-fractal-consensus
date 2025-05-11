from typing import List, Optional, Dict, Any, Set
from datetime import datetime
import json
import logging
from dataclasses import dataclass, field
from .block import Block
from .transaction import Transaction
from .fractal_coordinate import FractalCoordinate

logger = logging.getLogger(__name__)

# Blockchain constants
MAX_TRANSACTIONS_PER_BLOCK = 100  # Maximum transactions allowed in a block
MAX_PENDING_TRANSACTIONS = 1000   # Maximum size of transaction pool
BLOCK_REWARD = 50                 # Mining reward per block
MIN_DIFFICULTY = 1                # Minimum mining difficulty
MAX_DIFFICULTY = 32               # Maximum mining difficulty

class BlockchainError(Exception):
    """Base exception for blockchain-related errors."""
    pass

class InvalidBlockError(BlockchainError):
    """Raised when a block fails validation."""
    pass

class TransactionError(BlockchainError):
    """Raised when transaction validation or processing fails."""
    pass

@dataclass
class ChainStats:
    """
    Statistics about the blockchain.
    
    Attributes:
        total_blocks (int): Total number of blocks in chain
        total_transactions (int): Total number of processed transactions
        total_rewards (float): Total mining rewards distributed
        average_block_time (float): Average time between blocks
        last_block_time (float): Timestamp of last block
    """
    total_blocks: int = 0
    total_transactions: int = 0
    total_rewards: float = 0.0
    average_block_time: float = 0.0
    last_block_time: float = 0.0
    processed_tx_ids: Set[str] = field(default_factory=set)

class Blockchain:
    """
    A blockchain implementation that manages blocks, transactions, and chain validation.
    
    The blockchain maintains an ordered list of blocks, each containing transactions
    and linked through cryptographic hashes. It also manages pending transactions
    that haven't yet been included in a block.
    
    Attributes:
        chain (List[Block]): The list of blocks forming the blockchain
        pending_transactions (List[Transaction]): Transactions waiting to be included in blocks
        difficulty (int): The mining difficulty (number of leading zeros required in block hash)
        stats (ChainStats): Statistics about the blockchain
    """
    
    def __init__(self, difficulty: int = 4) -> None:
        """
        Initialize a new blockchain with the specified mining difficulty.
        
        Args:
            difficulty (int, optional): Mining difficulty level. Defaults to 4.
                                     Higher values make mining more difficult.
        
        Raises:
            ValueError: If difficulty is negative or zero
        """
        if not MIN_DIFFICULTY <= difficulty <= MAX_DIFFICULTY:
            raise ValueError(
                f"Difficulty must be between {MIN_DIFFICULTY} and {MAX_DIFFICULTY}"
            )
            
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = difficulty
        self.stats = ChainStats()
        
        logger.info(f"Initializing blockchain with difficulty {difficulty}")
        if not self.chain:
            self._create_genesis_block()
            
    def _create_genesis_block(self) -> None:
        """
        Create and add the genesis (first) block to the blockchain.
        
        The genesis block has index 0, no transactions, and a previous hash of 64 zeros.
        Its fractal coordinates are set to (0,0,0).
        """
        try:
            genesis_coord = FractalCoordinate(a=0, b=0, c=0)
            genesis_block = Block(
                index=0,
                timestamp=datetime.utcnow().timestamp(),
                transactions=[],
                previous_hash="0" * 64,
                miner="network",
                fractal_coord=genesis_coord
            )
            genesis_block.hash = genesis_block.calculate_hash()
            self.chain.append(genesis_block)
            
            self.stats.total_blocks = 1
            self.stats.last_block_time = genesis_block.timestamp
            
            logger.info(f"Genesis block created with hash: {genesis_block.hash[:10]}...")
        except Exception as e:
            logger.error(f"Failed to create genesis block: {str(e)}")
            raise BlockchainError(f"Genesis block creation failed: {str(e)}")
        
    @property
    def last_block(self) -> Optional[Block]:
        """
        Get the most recent block in the chain.
        
        Returns:
            Optional[Block]: The last block in the chain, or None if chain is empty
        """
        return self.chain[-1] if self.chain else None
        
    def add_block(self, block: Block) -> bool:
        """
        Add a new block to the chain after validation.
        
        Args:
            block (Block): The block to add to the chain
            
        Returns:
            bool: True if block was successfully added, False otherwise
            
        Raises:
            InvalidBlockError: If the block fails validation checks
        """
        try:
            if not isinstance(block, Block):
                raise InvalidBlockError("Invalid block type")
                
            if not self._is_valid_block(block):
                logger.warning(f"Block {block.index} validation failed")
                return False
                
            # Update chain
            self.chain.append(block)
            
            # Update statistics
            self.stats.total_blocks += 1
            self.stats.total_transactions += len(block.transactions)
            
            # Track processed transactions
            for tx in block.transactions:
                self.stats.processed_tx_ids.add(tx.tx_id)
                if tx.sender == "network":  # Mining reward
                    self.stats.total_rewards += tx.amount
                    
            # Update timing statistics
            current_time = block.timestamp
            if self.stats.last_block_time > 0:
                block_time = current_time - self.stats.last_block_time
                self.stats.average_block_time = (
                    (self.stats.average_block_time * (self.stats.total_blocks - 1) + block_time)
                    / self.stats.total_blocks
                )
            self.stats.last_block_time = current_time
            
            logger.info(
                f"Block {block.index} added to chain with hash: {block.hash[:10]}... "
                f"({len(block.transactions)} transactions)"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error adding block: {str(e)}")
            raise BlockchainError(f"Failed to add block: {str(e)}")
        
    def add_pending_transaction(self, transaction: Transaction) -> None:
        """
        Add a new transaction to the pending transactions pool.
        
        Args:
            transaction (Transaction): The transaction to add to the pool
            
        Raises:
            TransactionError: If transaction is invalid or pool is full
        """
        try:
            if not transaction:
                raise TransactionError("Transaction cannot be None")
                
            if not isinstance(transaction, Transaction):
                raise TransactionError("Invalid transaction type")
                
            if transaction.tx_id in self.stats.processed_tx_ids:
                raise TransactionError("Transaction already processed")
                
            if len(self.pending_transactions) >= MAX_PENDING_TRANSACTIONS:
                raise TransactionError("Transaction pool is full")
                
            self.pending_transactions.append(transaction)
            logger.debug(
                f"Added transaction {transaction.tx_id[:8]}... to pending pool "
                f"(pool size: {len(self.pending_transactions)})"
            )
            
        except Exception as e:
            logger.error(f"Failed to add transaction: {str(e)}")
            raise TransactionError(str(e))
        
    def _is_valid_block(self, block: Block) -> bool:
        """
        Validate a block before adding it to the chain.
        
        Checks:
        1. Block index matches the next expected index
        2. Previous hash matches the hash of the last block
        3. Block hash meets the difficulty requirement
        4. Block hash is valid for its contents
        
        Args:
            block (Block): The block to validate
            
        Returns:
            bool: True if block is valid, False otherwise
            
        Raises:
            InvalidBlockError: If block validation fails with specific reason
        """
        try:
            # Check block index
            if block.index != len(self.chain):
                raise InvalidBlockError(f"Invalid block index. Expected {len(self.chain)}, got {block.index}")
                
            # Check previous hash
            if not self.last_block:
                raise InvalidBlockError("Cannot validate block: no previous block exists")
                
            if block.previous_hash != self.last_block.hash:
                raise InvalidBlockError("Block's previous hash doesn't match last block's hash")
                
            # Check difficulty requirement
            if not block.hash.startswith("0" * self.difficulty):
                raise InvalidBlockError(f"Block hash doesn't meet difficulty requirement of {self.difficulty}")
                
            # Verify block hash
            calculated_hash = block.calculate_hash()
            if calculated_hash != block.hash:
                raise InvalidBlockError("Block hash is invalid")
                
            # Check transaction limit
            if len(block.transactions) > MAX_TRANSACTIONS_PER_BLOCK:
                raise InvalidBlockError(
                    f"Block exceeds maximum transaction limit of {MAX_TRANSACTIONS_PER_BLOCK}"
                )
                
            # Verify mining reward
            reward_tx = None
            for tx in block.transactions:
                if tx.sender == "network":
                    if reward_tx:
                        raise InvalidBlockError("Multiple reward transactions found")
                    if tx.amount != BLOCK_REWARD:
                        raise InvalidBlockError(f"Invalid mining reward amount: {tx.amount}")
                    if tx.receiver != block.miner:
                        raise InvalidBlockError("Mining reward receiver doesn't match block miner")
                    reward_tx = tx
                    
            if not reward_tx:
                raise InvalidBlockError("No mining reward transaction found")
                
            # Check for duplicate transactions
            tx_ids = set()
            for tx in block.transactions:
                if tx.tx_id in tx_ids:
                    raise InvalidBlockError(f"Duplicate transaction found: {tx.tx_id}")
                if tx.tx_id in self.stats.processed_tx_ids:
                    raise InvalidBlockError(f"Transaction already processed: {tx.tx_id}")
                tx_ids.add(tx.tx_id)
                
            return True
            
        except InvalidBlockError:
            raise
        except Exception as e:
            logger.error(f"Error validating block: {str(e)}")
            raise InvalidBlockError(f"Block validation failed: {str(e)}")
        
    def is_valid_chain(self) -> bool:
        """
        Validate the entire blockchain.
        
        Verifies that:
        1. All blocks are properly linked (previous_hash matches)
        2. All blocks meet the difficulty requirement
        3. All block hashes are valid
        4. All mining rewards are correct
        5. No duplicate transactions exist
        
        Returns:
            bool: True if entire chain is valid, False otherwise
        """
        try:
            processed_tx_ids = set()
            total_rewards = 0.0
            
            for i in range(1, len(self.chain)):
                current = self.chain[i]
                previous = self.chain[i-1]
                
                # Check block linkage
                if current.previous_hash != previous.hash:
                    logger.error(f"Invalid chain: Block {i} has incorrect previous hash")
                    return False
                    
                # Check difficulty requirement
                if not current.hash.startswith("0" * self.difficulty):
                    logger.error(f"Invalid chain: Block {i} doesn't meet difficulty requirement")
                    return False
                    
                # Verify block hash
                if current.hash != current.calculate_hash():
                    logger.error(f"Invalid chain: Block {i} has invalid hash")
                    return False
                    
                # Check transactions
                reward_found = False
                for tx in current.transactions:
                    # Check for duplicates
                    if tx.tx_id in processed_tx_ids:
                        logger.error(f"Invalid chain: Duplicate transaction {tx.tx_id} in block {i}")
                        return False
                    processed_tx_ids.add(tx.tx_id)
                    
                    # Verify mining reward
                    if tx.sender == "network":
                        if reward_found:
                            logger.error(f"Invalid chain: Multiple rewards in block {i}")
                            return False
                        if tx.amount != BLOCK_REWARD:
                            logger.error(f"Invalid chain: Incorrect reward in block {i}")
                            return False
                        if tx.receiver != current.miner:
                            logger.error(f"Invalid chain: Reward receiver mismatch in block {i}")
                            return False
                        reward_found = True
                        total_rewards += tx.amount
                        
                if not reward_found:
                    logger.error(f"Invalid chain: No mining reward in block {i}")
                    return False
                    
            logger.info("Chain validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error validating chain: {str(e)}")
            return False
            
    def get_balance(self, address: str) -> float:
        """
        Calculate the balance for a given address.
        
        Args:
            address (str): The address to check balance for
            
        Returns:
            float: Current balance for the address
            
        Raises:
            ValueError: If address is invalid
        """
        if not isinstance(address, str) or not address:
            raise ValueError("Invalid address")
            
        try:
            balance = 0.0
            
            # Process all blocks
            for block in self.chain:
                for tx in block.transactions:
                    if tx.receiver == address:
                        balance += tx.amount
                    if tx.sender == address:
                        balance -= tx.amount
                        
            return balance
            
        except Exception as e:
            logger.error(f"Error calculating balance for {address}: {str(e)}")
            raise BlockchainError(f"Balance calculation failed: {str(e)}")
            
    def get_chain_stats(self) -> Dict[str, Any]:
        """
        Get current blockchain statistics.
        
        Returns:
            Dict[str, Any]: Dictionary containing chain statistics
        """
        return {
            "total_blocks": self.stats.total_blocks,
            "total_transactions": self.stats.total_transactions,
            "total_rewards": self.stats.total_rewards,
            "average_block_time": self.stats.average_block_time,
            "pending_transactions": len(self.pending_transactions),
            "difficulty": self.difficulty,
            "last_block_time": datetime.fromtimestamp(
                self.stats.last_block_time
            ).strftime("%Y-%m-%d %H:%M:%S")
        }

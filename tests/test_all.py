import pytest
import time
from datetime import datetime
from blockchain.core.transaction import Transaction
from blockchain.core.block import Block, BlockValidationError
from blockchain.core.blockchain import (
    Blockchain, BlockchainError, InvalidBlockError, TransactionError,
    BLOCK_REWARD, MAX_TRANSACTIONS_PER_BLOCK, MAX_DIFFICULTY, MAX_PENDING_TRANSACTIONS
)
from blockchain.core.fractal_coordinate import FractalCoordinate
from blockchain.wallet import Wallet

def test_blockchain_initialization():
    """Test blockchain initialization with valid and invalid difficulty."""
    # Test valid initialization
    blockchain = Blockchain(difficulty=4)
    assert blockchain.difficulty == 4
    assert len(blockchain.chain) == 1  # Genesis block
    assert blockchain.stats.total_blocks == 1
    
    # Test invalid difficulty
    with pytest.raises(ValueError):
        Blockchain(difficulty=0)
    with pytest.raises(ValueError):
        Blockchain(difficulty=-1)
    with pytest.raises(ValueError):
        Blockchain(difficulty=MAX_DIFFICULTY + 1)

def test_blockchain_transactions():
    """Test transaction handling and validation."""
    blockchain = Blockchain(difficulty=1)
    
    # Test adding valid transaction
    tx = Transaction("sender", "receiver", 1.0)
    blockchain.add_pending_transaction(tx)
    assert len(blockchain.pending_transactions) == 1
    
    # Test transaction pool limit
    tx2 = Transaction("sender2", "receiver2", 1.0)
    blockchain.add_pending_transaction(tx2)
        
    # Test duplicate transaction rejection
    block = blockchain.last_block
    tx = Transaction("sender", "receiver", 1.0)
    block.transactions.append(tx)
    blockchain.stats.processed_tx_ids.add(tx.tx_id)
    with pytest.raises(TransactionError):
        blockchain.add_pending_transaction(tx)

def test_block_validation():
    """Test block validation rules."""
    blockchain = Blockchain(difficulty=1)
    
    # Create valid block
    block = Block(
        index=len(blockchain.chain),
        timestamp=time.time(),
        transactions=[],
        previous_hash=blockchain.last_block.hash,
        miner="test_miner",
        fractal_coord=FractalCoordinate(100, 100, 100)
    )
    
    # Add mining reward
    reward_tx = Transaction(
        "network",
        "test_miner",
        BLOCK_REWARD,
        timestamp=block.timestamp
    )
    block.transactions.append(reward_tx)
    
    # Mine block
    nonce = 0
    while True:
        block.nonce = nonce
        block.hash = block.calculate_hash()
        if block.hash.startswith("0" * blockchain.difficulty):
            break
        nonce += 1
    
    # Test valid block
    assert blockchain.add_block(block) is True
    assert len(blockchain.chain) == 2
    assert blockchain.stats.total_blocks == 2
    assert blockchain.stats.total_rewards == BLOCK_REWARD
    
    # Test invalid block index
    invalid_block = Block(
        index=5,  # Wrong index (should be 2)
        timestamp=time.time(),
        transactions=[],
        previous_hash=blockchain.last_block.hash,
        miner="test_miner",
        fractal_coord=FractalCoordinate(100, 100, 100)
    )
    
    # Add mining reward
    reward_tx = Transaction(
        "network",
        "test_miner",
        BLOCK_REWARD,
        timestamp=invalid_block.timestamp
    )
    invalid_block.transactions.append(reward_tx)
    
    # Mine block
    nonce = 0
    while True:
        invalid_block.nonce = nonce
        invalid_block.hash = invalid_block.calculate_hash()
        if invalid_block.hash.startswith("0" * blockchain.difficulty):
            break
        nonce += 1
        
    with pytest.raises(BlockchainError):
        blockchain.add_block(invalid_block)

def test_chain_validation():
    """Test chain validation with multiple blocks."""
    blockchain = Blockchain(difficulty=1)
    
    # Add multiple blocks
    for i in range(3):
        block = Block(
            index=len(blockchain.chain),
            timestamp=time.time(),
            transactions=[],
            previous_hash=blockchain.last_block.hash,
            miner="test_miner",
            fractal_coord=FractalCoordinate(100, 100, 100)
        )
        
        # Add mining reward
        reward_tx = Transaction(
            "network",
            "test_miner",
            BLOCK_REWARD,
            timestamp=block.timestamp
        )
        block.transactions.append(reward_tx)
        
        # Mine block
        nonce = 0
        while True:
            block.nonce = nonce
            block.hash = block.calculate_hash()
            if block.hash.startswith("0" * blockchain.difficulty):
                break
            nonce += 1
        
        assert blockchain.add_block(block) is True
    
    # Test valid chain
    assert blockchain.is_valid_chain() is True
    assert len(blockchain.chain) == 4  # Genesis + 3 blocks
    
    # Test invalid chain (tamper with a block)
    blockchain.chain[2].transactions[0].amount = BLOCK_REWARD * 2
    assert blockchain.is_valid_chain() is False

def test_balance_tracking():
    """Test balance calculation and tracking."""
    blockchain = Blockchain(difficulty=1)
    address_a = "miner1"
    address_b = "user1"
    
    # Add block with transactions
    block = Block(
        index=len(blockchain.chain),
        timestamp=time.time(),
        transactions=[],
        previous_hash=blockchain.last_block.hash,
        miner=address_a,
        fractal_coord=FractalCoordinate(100, 100, 100)
    )
    
    # Mining reward
    reward_tx = Transaction(
        "network",
        address_a,
        BLOCK_REWARD,
        timestamp=block.timestamp
    )
    block.transactions.append(reward_tx)
    
    # Transfer
    transfer_tx = Transaction(
        address_a,
        address_b,
        20.0,
        timestamp=block.timestamp
    )
    block.transactions.append(transfer_tx)
    
    # Mine and add block
    nonce = 0
    while True:
        block.nonce = nonce
        block.hash = block.calculate_hash()
        if block.hash.startswith("0" * blockchain.difficulty):
            break
        nonce += 1
    blockchain.add_block(block)
    
    # Test balances
    assert blockchain.get_balance(address_a) == BLOCK_REWARD - 20.0
    assert blockchain.get_balance(address_b) == 20.0
    
    # Test invalid address
    with pytest.raises(ValueError):
        blockchain.get_balance("")
    with pytest.raises(ValueError):
        blockchain.get_balance(None)

def test_chain_statistics():
    """Test blockchain statistics tracking."""
    blockchain = Blockchain(difficulty=1)
    
    # Add multiple blocks
    for i in range(3):
        block = Block(
            index=len(blockchain.chain),
            timestamp=time.time(),
            transactions=[],
            previous_hash=blockchain.last_block.hash,
            miner="test_miner",
            fractal_coord=FractalCoordinate(100, 100, 100)
        )
        
        # Add mining reward
        reward_tx = Transaction(
            "network",
            "test_miner",
            BLOCK_REWARD,
            timestamp=block.timestamp
        )
        block.transactions.append(reward_tx)
        
        # Mine block
        nonce = 0
        while True:
            block.nonce = nonce
            block.hash = block.calculate_hash()
            if block.hash.startswith("0" * blockchain.difficulty):
                break
            nonce += 1
        
        blockchain.add_block(block)
    
    # Test statistics
    stats = blockchain.get_chain_stats()
    assert stats["total_blocks"] == 4  # Genesis + 3 blocks
    assert stats["total_transactions"] == 3  # 3 reward transactions
    assert stats["total_rewards"] == BLOCK_REWARD * 3
    assert stats["average_block_time"] > 0
    assert stats["difficulty"] == 1
    assert isinstance(stats["last_block_time"], str)

def test_genesis_block():
    """Test genesis block creation and validation."""
    blockchain = Blockchain(difficulty=1)
    genesis = blockchain.chain[0]
    
    # Test genesis block properties
    assert genesis.index == 0
    assert genesis.previous_hash == "0" * 64
    assert genesis.miner == "network"
    assert len(genesis.transactions) == 0
    
    # Store original hash
    original_hash = genesis.hash
    
    # Test chain validation with valid genesis block
    assert blockchain.is_valid_chain() is True
    
    # Store the original genesis block hash
    original_genesis_hash = genesis.hash
    
    # Add a valid block that links to the original genesis block
    new_block = Block(
        index=1,
        timestamp=time.time(),
        transactions=[],
        previous_hash=original_genesis_hash,  # Link to original genesis block
        miner="test_miner",
        fractal_coord=FractalCoordinate(1, 1, 1)
    )
    
    # Add mining reward
    reward_tx = Transaction(
        "network",
        "test_miner",
        BLOCK_REWARD,
        timestamp=new_block.timestamp
    )
    new_block.transactions.append(reward_tx)
    
    # Mine new block
    nonce = 0
    while True:
        new_block.nonce = nonce
        new_block.hash = new_block.calculate_hash()
        if new_block.hash.startswith("0" * blockchain.difficulty):
            break
        nonce += 1
    
    # Add the block to the chain
    blockchain.chain.append(new_block)
    
    # Now tamper with genesis block after adding the valid block
    genesis.miner = "attacker"
    genesis.hash = "f" * 64  # Invalid hash that doesn't meet difficulty
    
    # Chain should be invalid because genesis block was tampered
    assert blockchain.is_valid_chain() is False

if __name__ == '__main__':
    pytest.main([__file__])

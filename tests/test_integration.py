# Disabled old tests due to missing functions generate_transactions and mine_block

import pytest
from triadnet.core.transaction import Transaction
from triadnet.core.block import Block
from triadnet.consensus.proof_of_work import ProofOfFractalWork
from triadnet.core.blockchain import Blockchain

def test_transaction_creation():
    tx = Transaction(
        tx_id="tx1",
        sender="addr1",
        receiver="addr2",
        amount=10.0,
        data="Test",
        timestamp=1234567890.0
    )
    assert tx.tx_id == "tx1"
    assert tx.amount == 10.0

def test_mine_block_success():
    blockchain = Blockchain()
    pofw = ProofOfFractalWork(difficulty=1)  # Low difficulty for test
    block = Block(
        index=1,
        timestamp=1234567890.0,
        transactions=[],
        previous_hash="0"*64,
        miner="addr1",
        fractal_coord=blockchain.fractal_coord if hasattr(blockchain, 'fractal_coord') else None
    )
    if block.fractal_coord is None:
        from triadnet.core.fractal_coordinate import FractalCoordinate
        block.fractal_coord = FractalCoordinate.generate()
    result = pofw.mine_block(block, max_nonce=10000)
    assert result.success is True
    assert result.block is not None
    assert result.hash_val.startswith("0")

def test_blockchain_add_block():
    blockchain = Blockchain()
    blockchain.difficulty = 1  # Set difficulty to 1 to match mining difficulty
    last_block = blockchain.last_block
    from triadnet.core.fractal_coordinate import FractalCoordinate
    from triadnet.consensus.proof_of_work import ProofOfFractalWork
    fractal_coord = FractalCoordinate.generate()
    block = Block(
        index=last_block.index + 1,
        timestamp=1234567890.0,
        transactions=[],
        previous_hash=last_block.hash,
        miner="addr1",
        fractal_coord=fractal_coord
    )
    pofw = ProofOfFractalWork(difficulty=1)  # Lower difficulty for test
    result = pofw.mine_block(block, max_nonce=100000)
    assert result.success is True
    print(f"Block hash: {result.block.hash}")
    print(f"Block index: {result.block.index}, Chain length: {len(blockchain.chain)}")
    print(f"Block previous_hash: {result.block.previous_hash}, Last block hash: {blockchain.last_block.hash}")
    added = blockchain.add_block(result.block)
    print(f"Block added: {added}")
    assert added is True

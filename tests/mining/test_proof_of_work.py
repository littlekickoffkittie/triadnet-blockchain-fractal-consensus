import pytest
from triadnet.core.fractal_coordinate import FractalCoordinate
from triadnet.wallet import Wallet
from triadnet.core.transaction import Transaction
from triadnet.mining.proof_of_work import ProofOfFractalWork
from triadnet.core.blockchain import Blockchain
from triadnet.core.block import Block

def test_proof_of_fractal_work_mining():
    blockchain = Blockchain()
    pofw = ProofOfFractalWork(difficulty=1)  # Low difficulty for test
    block = Block(
        index=blockchain.last_block.index + 1,
        timestamp=1234567890.0,
        transactions=[],
        previous_hash=blockchain.last_block.hash,
        miner="miner_address",
        fractal_coord=FractalCoordinate.generate()
    )
    result = pofw.mine_block(block, max_nonce=10000)
    assert result.success is True
    assert result.block is not None
    assert result.hash_val.startswith("0")

def test_enhanced_fractal_score_range():
    pofw = ProofOfFractalWork(difficulty=1)
    for _ in range(100):
        coord = FractalCoordinate.generate()
        score = pofw._calculate_fractal_score(coord)
        assert 0.1 <= score <= 2.0

def test_difficulty_adjustment_behavior():
    pofw = ProofOfFractalWork(difficulty=3)
    # Simulate fast mining time and high fractal score
    pofw._adjust_difficulty(last_block_time=30, fractal_score=1.5)
    assert pofw.difficulty >= 3
    # Simulate slow mining time and low fractal score
    pofw._adjust_difficulty(last_block_time=120, fractal_score=0.5)
    assert pofw.difficulty <= 4

import pytest
from triadnet.core.fractal_coordinate import FractalCoordinate
from triadnet.wallet import Wallet
from triadnet.core.transaction import Transaction
from triadnet.consensus.proof_of_work import ProofOfFractalWork
from triadnet.core.blockchain import Blockchain
from triadnet.core.block import Block

def test_fractal_coordinate_generate():
    fc = FractalCoordinate.generate()
    assert 0 <= fc.a <= 500
    assert 0 <= fc.b <= 500
    assert 0 <= fc.c <= 500

def test_wallet_sign_transaction():
    wallet = Wallet()
    receiver = "receiver_address"
    amount = 10.0
    # Create a transaction manually
    tx = Transaction(
        tx_id="tx1",
        sender=wallet.address,
        receiver=receiver,
        amount=amount,
        data="Test transaction",
        timestamp=1234567890.0
    )
    signed_tx = wallet.sign_transaction(tx)
    assert isinstance(signed_tx, Transaction)
    assert signed_tx.signature is not None

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

def test_blockchain_add_and_validate_block():
    blockchain = Blockchain(difficulty=1)
    pofw = ProofOfFractalWork(difficulty=1)
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
    added = blockchain.add_block(result.block)
    assert added is True
    assert blockchain.is_valid_chain() is True

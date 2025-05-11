from triadnet.core import Wallet, Blockchain, Transaction, FractalCoordinate
from triadnet.core.mining_manager import MiningManager
from triadnet.consensus.proof_of_work import ProofOfFractalWork, ConsensusManager
import time
import random

def main():
    # Create wallet and blockchain
    print("Initializing wallet and blockchain...")
    wallet = Wallet()
    blockchain = Blockchain()
    
    # Create consensus manager
    consensus = ConsensusManager(blockchain)
    
    # Initialize mining manager with fractal coordinates
    print("Setting up mining manager...")
    fractal_coord = FractalCoordinate(
        a=random.randint(0, 1000),
        b=random.randint(0, 1000),
        c=random.randint(0, 1000)
    )
    
    mining_manager = MiningManager(
        wallet=wallet,
        blockchain=blockchain,
        consensus=consensus,
        fractal_coord=fractal_coord
    )
    
    # Start mining
    print(f"\nStarting mining operation at coordinates {fractal_coord}...")
    mining_manager.start_mining()
    
    try:
        while True:
            # Create some random transactions periodically
            tx = Transaction(
                sender=f"wallet_{random.randint(1000,9999)}",
                receiver=f"wallet_{random.randint(1000,9999)}",
                amount=random.uniform(1, 100),
                data=f"Test transaction at {time.time()}"
            )
            mining_manager.add_transaction(tx)
            
            # Print status
            print(f"\nBlockchain Status:")
            print(f"Height: {len(blockchain.chain)}")
            if blockchain.chain:
                last_block = blockchain.chain[-1]
                print(f"Last block hash: {last_block.hash[:10]}...")
                print(f"Current difficulty: {consensus.pofw.difficulty}")
                print(f"Mining at coordinates: {fractal_coord}")
            
            time.sleep(10)  # Status update every 10 seconds
            
    except KeyboardInterrupt:
        print("\nStopping mining...")
        mining_manager.stop_mining()
        
        # Print final statistics
        print("\nMining operation completed!")
        print(f"Final blockchain height: {len(blockchain.chain)}")
        print(f"Final difficulty: {consensus.pofw.difficulty}")
        print(f"Total blocks mined: {len(blockchain.chain)}")

if __name__ == "__main__":
    main()

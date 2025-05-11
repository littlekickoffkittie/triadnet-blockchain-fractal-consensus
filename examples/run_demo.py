from triadnet.core import Wallet, Blockchain, FractalCoordinate, Transaction
from triadnet.mine import Miner
import time
from datetime import datetime, timezone
import random

def print_status_header(user_login: str):
    print("\n" + "="*50)
    print(f"TRIADNET MINING SYSTEM")
    print(f"Current Time (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"User: {user_login}")
    print("="*50 + "\n")

def main():
    user_login = "littlekickoffkittie"
    print_status_header(user_login)
    
    print("1. Initializing wallet and blockchain...")
    wallet = Wallet()
    blockchain = Blockchain(difficulty=4)
    
    fractal_coord = FractalCoordinate(
        a=random.randint(100, 500),
        b=random.randint(100, 500),
        c=random.randint(100, 500)
    )
    
    print(f"\nWallet Address: {wallet.address}")
    print(f"Initial Fractal Coordinates: {fractal_coord}")
    
    print("\n2. Initializing miner...")
    miner = Miner(
        wallet=wallet,
        blockchain=blockchain,
        fractal_coord=fractal_coord,
        auto_adjust_coords=True
    )
    
    print("\n3. Starting mining operations...")
    miner.start()
    
    try:
        while True:
            if random.random() < 0.3:
                tx = Transaction(
                    sender=f"wallet_{random.randint(1000,9999)}",
                    receiver=wallet.address,
                    amount=random.uniform(1, 10),
                    data=f"Test tx at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}"
                )
                miner.add_transaction(tx)
                print("\nNew transaction added to pool!")
            
            status = miner.get_status()
            print("\n" + "-"*50)
            print(f"Mining Status Update at {status['timestamp']}")
            print("-"*50)
            print(f"Active: {status['active']}")
            print(f"Chain Height: {status['chain_height']}")
            print(f"Current Difficulty: {status['difficulty']}")
            print(f"Fractal Coordinates: (a={status['fractal_coordinates']['a']}, "
                  f"b={status['fractal_coordinates']['b']}, "
                  f"c={status['fractal_coordinates']['c']})")
            print(f"Pending Transactions: {status['pending_transactions']}")
            print("\nMining Statistics:")
            print(f"Blocks Mined: {status['stats']['blocks_mined']}")
            print(f"Total Reward: {status['stats']['total_reward']}")
            print(f"Hash Rate: {status['stats']['hash_rate']}")
            print(f"Mining Time: {status['stats']['total_time']}")
            if status['stats']['last_block'] != "Never":
                print(f"Last Block Mined: {status['stats']['last_block']}")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\nStopping mining operations...")
        miner.stop()
        
        final_status = miner.get_status()
        print("\nFinal Mining Statistics:")
        print("="*50)
        print(f"Total Blocks Mined: {final_status['stats']['blocks_mined']}")
        print(f"Final Chain Height: {final_status['chain_height']}")
        print(f"Total Mining Time: {final_status['stats']['total_time']}")
        print(f"Total Rewards Earned: {final_status['stats']['total_reward']}")
        print(f"Final Hash Rate: {final_status['stats']['hash_rate']}")
        print("="*50)

if __name__ == "__main__":
    main()

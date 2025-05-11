from blockchain.core import Wallet
import json

def main():
    # Generate new wallet
    print("Generating new wallet...")
    wallet = Wallet()
    
    # Display wallet information
    print("\nWallet Generated Successfully!")
    print("=" * 50)
    print(f"Address: {wallet.address}")
    print(f"Public Key: {wallet.public_key}")
    print(f"Private Key: {wallet.private_key}")
    print(f"Created At (UTC): {wallet.created_at}")
    print("=" * 50)
    
    # Save wallet info (NEVER store private key in production!)
    wallet_info = wallet.to_dict()
    wallet_info["private_key"] = wallet.private_key  # Only for demo purposes
    
    with open("wallet.json", "w") as f:
        json.dump(wallet_info, f, indent=2)
    print("\nWallet information saved to wallet.json")
    print("WARNING: In production, never store private keys in plain text!")
    
    # Demo signing a transaction
    transaction = f"Send 100 TRIAD tokens to TRIAD1234..."
    signature = wallet.sign_transaction(transaction)
    print("\nTransaction Signing Demo:")
    print(f"Transaction: {transaction}")
    print(f"Signature: {signature}")

if __name__ == "__main__":
    main()

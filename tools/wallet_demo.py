from triadnet.core import Wallet
import json
from datetime import datetime
import os

def main():
    # 1. Generate new wallet
    print("\n1. Generating new wallet...")
    wallet = Wallet()
    
    # Display wallet information
    print("\nWallet Generated Successfully!")
    print("=" * 50)
    print(f"Address: {wallet.address}")
    print(f"Created At (UTC): {wallet.created_at}")
    print("=" * 50)
    
    # 2. Create encrypted backup
    password = "your-secure-password"  # In production, this should be securely provided by the user
    print("\n2. Creating encrypted backup...")
    backup = wallet.create_encrypted_backup(password)
    print(f"Encrypted Backup Created: {backup[:50]}...")
    
    # Save wallet info (excluding private key)
    wallet_info = wallet.to_dict()
    wallet_info["encrypted_backup"] = backup
    
    # Save to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wallet_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(wallet_info, f, indent=2)
    print(f"\nWallet information saved to {filename}")
    
    # 3. Demo transaction signing
    print("\n3. Transaction Signing Demo:")
    transaction = f"Send 100 TRIAD tokens to {wallet.address}"
    signature = wallet.sign_transaction(transaction)
    print(f"Transaction: {transaction}")
    print(f"Signature: {signature[:50]}...")
    
    # 4. Verify signature
    print("\n4. Signature Verification:")
    is_valid = wallet.verify_signature(transaction, signature)
    print(f"Signature Valid: {is_valid}")
    
    # 5. Demonstrate wallet restoration
    print("\n5. Wallet Restoration Demo:")
    restored_wallet = Wallet.restore_from_backup(backup, password)
    print(f"Restored Wallet Address: {restored_wallet.address}")
    print(f"Addresses Match: {wallet.address == restored_wallet.address}")
    
    print("\nWallet Demo Complete!")
    print("\nIMPORTANT SECURITY NOTES:")
    print("1. Always keep your backup and password secure")
    print("2. Never share your private key or backup with anyone")
    print("3. Store your backup in multiple secure locations")
    print("4. Use a strong password for encryption")

if __name__ == "__main__":
    main()

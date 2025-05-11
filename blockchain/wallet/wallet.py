import os
import hashlib
import time
import json
import base64
import logging
from typing import Dict, Tuple, Optional, List, Any
from dataclasses import dataclass, field
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from cryptography.fernet import Fernet
from blockchain.core import FractalCoordinate, Transaction

# Wallet constants
KEY_SIZE = 2048  # RSA key size in bits
PUBLIC_EXPONENT = 65537  # Standard RSA public exponent
ADDRESS_PREFIX = "TX"  # Prefix for wallet addresses
ADDRESS_LENGTH = 32  # Length of wallet address (excluding prefix)
TX_ID_RANDOM_BYTES = 4  # Number of random bytes for transaction IDs

class WalletError(Exception):
    """Base exception for wallet-related errors."""
    pass

class KeyGenerationError(WalletError):
    """Raised when key generation fails."""
    pass

class TransactionError(WalletError):
    """Raised when transaction operations fail."""
    pass

class StorageError(WalletError):
    """Raised when wallet storage/loading fails."""
    pass

@dataclass
class WalletState:
    """
    Represents the current state of a wallet.
    
    Attributes:
        balance (float): Current balance
        transactions (List[Transaction]): Transaction history
        last_update (float): Timestamp of last balance update
    """
    balance: float = 0.0
    transactions: List[Transaction] = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

class Wallet:
    """
    Cryptocurrency wallet implementation.
    
    Handles:
    - Key generation and management
    - Transaction creation and signing
    - Wallet storage and loading
    - Balance tracking
    """
    
    def __init__(self, load_path: Optional[str] = None):
        """
        Initialize a wallet with new or loaded keys.
        
        Args:
            load_path (Optional[str]): Path to load wallet from, if any
            
        Raises:
            StorageError: If wallet loading fails
            KeyGenerationError: If key generation fails
        """
        self.logger = logging.getLogger("triadnet.wallet")
        
        try:
            if load_path and os.path.exists(load_path):
                self._load_wallet(load_path)
                self.logger.info(f"Loaded wallet from {load_path}")
            else:
                self._generate_keypair()
                self.fractal_coord = FractalCoordinate.generate()
                self.address = self._generate_address()
                self.state = WalletState()
                self.logger.info(f"Created new wallet with address {self.address}")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize wallet: {str(e)}")
            raise WalletError(f"Wallet initialization failed: {str(e)}")
            
    def _generate_keypair(self) -> None:
        """
        Generate a new RSA keypair.
        
        Raises:
            KeyGenerationError: If key generation fails
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=PUBLIC_EXPONENT,
                key_size=KEY_SIZE
            )
            
            self.private_key = private_key
            self.public_key = private_key.public_key()
            
            # Store serialized versions
            self._private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            self._public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            self.logger.debug("Generated new keypair")
            
        except Exception as e:
            self.logger.error(f"Key generation failed: {str(e)}")
            raise KeyGenerationError(f"Failed to generate keypair: {str(e)}")

    def _generate_address(self) -> str:
        """
        Generate wallet address from public key and fractal coordinate.
        
        Returns:
            str: Generated wallet address
            
        Raises:
            WalletError: If address generation fails
        """
        try:
            # Combine public key and fractal coordinate
            public_key_bytes = self._public_pem
            fractal_str = str(self.fractal_coord).encode()
            
            # Double-hash for security
            intermediate = hashlib.sha256(public_key_bytes + fractal_str).digest()
            address_bytes = hashlib.sha256(intermediate).digest()
            
            # Format as base32 address with prefix
            address = ADDRESS_PREFIX + base64.b32encode(address_bytes).decode()[:ADDRESS_LENGTH]
            
            self.logger.debug(f"Generated address: {address}")
            return address
            
        except Exception as e:
            self.logger.error(f"Address generation failed: {str(e)}")
            raise WalletError(f"Failed to generate address: {str(e)}")

    def sign_transaction(self, tx: Transaction) -> Transaction:
        """
        Sign a transaction with the wallet's private key.
        
        Args:
            tx (Transaction): Transaction to sign
            
        Returns:
            Transaction: Signed transaction
            
        Raises:
            TransactionError: If signing fails
        """
        try:
            if not isinstance(tx, Transaction):
                raise TransactionError("Invalid transaction type")
                
            # Create message from transaction data
            message = (
                f"{tx.tx_id}{tx.sender}{tx.receiver}{tx.amount}{tx.data}{tx.timestamp}"
            ).encode()
            
            # Sign with RSA-PSS
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Store base64-encoded signature
            tx.signature = base64.b64encode(signature).decode()
            self.logger.debug(f"Signed transaction {tx.tx_id[:8]}...")
            
            return tx
            
        except Exception as e:
            self.logger.error(f"Transaction signing failed: {str(e)}")
            raise TransactionError(f"Failed to sign transaction: {str(e)}")
        
    def create_transaction(
        self, 
        receiver: str, 
        amount: float, 
        data: str = ""
    ) -> Transaction:
        """
        Create and sign a new transaction.
        
        Args:
            receiver (str): Recipient's address
            amount (float): Amount to send
            data (str): Optional transaction data
            
        Returns:
            Transaction: Signed transaction
            
        Raises:
            TransactionError: If transaction creation fails
        """
        try:
            if not isinstance(receiver, str) or not receiver:
                raise TransactionError("Invalid receiver address")
                
            if not isinstance(amount, (int, float)) or amount <= 0:
                raise TransactionError("Amount must be positive")
                
            if self.state.balance < amount:
                raise TransactionError("Insufficient funds")
                
            tx = Transaction(
                tx_id=f"tx-{int(time.time())}-{os.urandom(TX_ID_RANDOM_BYTES).hex()}",
                sender=self.address,
                receiver=receiver,
                amount=amount,
                data=data,
                timestamp=time.time()
            )
            
            self.logger.info(
                f"Creating transaction: {amount} to {receiver[:8]}..."
            )
            return self.sign_transaction(tx)
            
        except Exception as e:
            self.logger.error(f"Transaction creation failed: {str(e)}")
            raise TransactionError(str(e))
    
    def verify_transaction(self, tx: Transaction) -> bool:
        """
        Verify a transaction's signature.
        
        Args:
            tx (Transaction): Transaction to verify
            
        Returns:
            bool: True if signature is valid
            
        Note:
            This is a simplified version that only verifies own transactions.
            A full implementation would need to retrieve the sender's public key.
        """
        try:
            if not isinstance(tx, Transaction):
                return False
                
            if tx.sender != self.address:
                return False
                
            message = (
                f"{tx.tx_id}{tx.sender}{tx.receiver}{tx.amount}{tx.data}{tx.timestamp}"
            ).encode()
            
            signature = base64.b64decode(tx.signature)
            
            self.public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            self.logger.debug(f"Verified transaction {tx.tx_id[:8]}...")
            return True
            
        except (InvalidSignature, Exception):
            self.logger.warning(f"Failed to verify transaction {tx.tx_id[:8]}...")
            return False
    
    def save(self, path: str) -> None:
        """
        Save wallet to encrypted file.
        
        Args:
            path (str): Path to save wallet to
            
        Raises:
            StorageError: If saving fails
        """
        try:
            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            
            wallet_data = {
                "address": self.address,
                "private_key": cipher_suite.encrypt(self._private_pem).decode(),
                "public_key": self._public_pem.decode(),
                "fractal_coord": self.fractal_coord.to_dict(),
                "balance": self.state.balance,
                "transactions": [
                    json.loads(tx.serialize()) 
                    for tx in self.state.transactions
                ],
                "encryption_key": key.decode()
            }
            
            with open(path, 'w') as f:
                json.dump(wallet_data, f, indent=2)
                
            self.logger.info(f"Saved wallet to {path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save wallet: {str(e)}")
            raise StorageError(f"Failed to save wallet: {str(e)}")

    def _load_wallet(self, path: str) -> None:
        """
        Load wallet from encrypted file.
        
        Args:
            path (str): Path to load wallet from
            
        Raises:
            StorageError: If loading fails
        """
        try:
            with open(path, 'r') as f:
                wallet_data = json.load(f)
                
            key = wallet_data.get("encryption_key")
            if not key:
                raise StorageError("Missing encryption key")
                
            cipher_suite = Fernet(key.encode())
            
            # Load and decrypt keys
            self._private_pem = cipher_suite.decrypt(
                wallet_data["private_key"].encode()
            )
            self._public_pem = wallet_data["public_key"].encode()
            
            # Load key objects
            self.private_key = serialization.load_pem_private_key(
                self._private_pem,
                password=None
            )
            self.public_key = serialization.load_pem_public_key(
                self._public_pem
            )
            
            # Load wallet data
            self.address = wallet_data["address"]
            self.fractal_coord = FractalCoordinate.from_dict(
                wallet_data["fractal_coord"]
            )
            
            # Load state
            self.state = WalletState(
                balance=wallet_data["balance"],
                transactions=[
                    Transaction.deserialize(json.dumps(tx_data))
                    for tx_data in wallet_data.get("transactions", [])
                ]
            )
            
            self.logger.info(
                f"Loaded wallet {self.address} with "
                f"{len(self.state.transactions)} transactions"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to load wallet: {str(e)}")
            raise StorageError(f"Failed to load wallet: {str(e)}")
    
    def update_balance(self, blockchain: Any) -> float:
        """
        Update wallet balance from blockchain.
        
        Args:
            blockchain: Blockchain instance to get balance from
            
        Returns:
            float: Updated balance
            
        Raises:
            WalletError: If balance update fails
        """
        try:
            self.state.balance = blockchain.get_balance(self.address)
            self.state.last_update = time.time()
            
            self.logger.info(
                f"Updated balance: {self.state.balance:.2f} "
                f"at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return self.state.balance
            
        except Exception as e:
            self.logger.error(f"Failed to update balance: {str(e)}")
            raise WalletError(f"Failed to update balance: {str(e)}")
    
    def get_public_key_str(self) -> str:
        """
        Get public key in PEM format.
        
        Returns:
            str: Public key in PEM format
        """
        return self._public_pem.decode()
    
    @classmethod
    def generate(cls) -> 'Wallet':
        """
        Generate a new wallet.
        
        Returns:
            Wallet: New wallet instance
            
        Raises:
            WalletError: If wallet generation fails
        """
        try:
            return cls()
        except Exception as e:
            raise WalletError(f"Failed to generate wallet: {str(e)}")

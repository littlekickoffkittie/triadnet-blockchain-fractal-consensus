import hashlib
import time
import json
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class TransactionError(Exception):
    """Base exception for transaction-related errors."""
    pass

class TransactionValidationError(TransactionError):
    """Raised when transaction validation fails."""
    pass

class SignatureError(TransactionError):
    """Raised when transaction signature is invalid."""
    pass

@dataclass
class Transaction:
    """
    A transaction in the blockchain representing a transfer between addresses.
    
    Each transaction includes:
    - Sender's address
    - Receiver's address
    - Amount being transferred
    - Optional data payload
    - Timestamp of creation
    - Transaction ID (hash)
    - Optional digital signature
    
    Attributes:
        sender (str): Address of the sender
        receiver (str): Address of the receiver
        amount (float): Amount being transferred
        data (str): Optional data payload
        timestamp (float): Unix timestamp of creation
        tx_id (Optional[str]): Transaction ID (hash)
        signature (Optional[str]): Digital signature
    """
    
    sender: str
    receiver: str
    amount: float
    data: str = ""
    timestamp: float = field(default_factory=time.time)
    tx_id: Optional[str] = None
    signature: Optional[str] = None

    def __post_init__(self):
        """
        Validate transaction attributes and generate tx_id if not provided.
        
        Raises:
            TransactionValidationError: If any attribute is invalid
        """
        try:
            self._validate_attributes()
            if self.tx_id is None:
                self.tx_id = self.calculate_hash()
                logger.debug(f"Generated transaction ID: {self.tx_id[:8]}...")
        except Exception as e:
            logger.error(f"Transaction initialization failed: {str(e)}")
            raise TransactionValidationError(f"Transaction initialization failed: {str(e)}")

    def _validate_attributes(self) -> None:
        """
        Validate all transaction attributes.
        
        Raises:
            TransactionValidationError: If any attribute is invalid
        """
        if not isinstance(self.sender, str) or not self.sender:
            raise TransactionValidationError("Sender address must be a non-empty string")
            
        if not isinstance(self.receiver, str) or not self.receiver:
            raise TransactionValidationError("Receiver address must be a non-empty string")
            
        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            raise TransactionValidationError("Amount must be a positive number")
            
        if not isinstance(self.data, str):
            raise TransactionValidationError("Data must be a string")
            
        if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
            raise TransactionValidationError("Timestamp must be a positive number")
            
        if self.tx_id is not None and (not isinstance(self.tx_id, str) or len(self.tx_id) != 64):
            raise TransactionValidationError("Transaction ID must be a 64-character hex string")
            
        if self.signature is not None and not isinstance(self.signature, str):
            raise TransactionValidationError("Signature must be a string")

    def calculate_hash(self) -> str:
        """
        Calculate the SHA-256 hash of the transaction.
        
        The hash is calculated from a string containing sender, receiver,
        amount, data, and timestamp.
        
        Returns:
            str: The hexadecimal representation of the transaction's hash
            
        Raises:
            TransactionError: If hash calculation fails
        """
        try:
            tx_string = f"{self.sender}{self.receiver}{self.amount}{self.data}{self.timestamp}"
            return hashlib.sha256(tx_string.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed: {str(e)}")
            raise TransactionError(f"Failed to calculate transaction hash: {str(e)}")

    def sign(self, signature: str) -> None:
        """
        Add a digital signature to the transaction.
        
        Args:
            signature (str): The digital signature to add
            
        Raises:
            SignatureError: If signature is invalid or already exists
        """
        if self.signature is not None:
            raise SignatureError("Transaction is already signed")
            
        if not isinstance(signature, str) or not signature:
            raise SignatureError("Invalid signature format")
            
        self.signature = signature
        logger.debug(f"Transaction {self.tx_id[:8]}... signed")

    def verify_signature(self) -> bool:
        """
        Verify the transaction's digital signature.
        
        Returns:
            bool: True if signature is valid, False otherwise
            
        Note:
            This is a placeholder method. In a real implementation,
            this would verify the signature using public key cryptography.
        """
        return self.signature is not None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transaction to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all transaction attributes
        """
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "data": self.data,
            "timestamp": self.timestamp,
            "tx_id": self.tx_id,
            "signature": self.signature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """
        Create a Transaction instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing transaction data
            
        Returns:
            Transaction: A new Transaction instance
            
        Raises:
            TransactionValidationError: If the dictionary is missing required fields
            or contains invalid data
        """
        try:
            required_fields = {"sender", "receiver", "amount"}
            if not all(field in data for field in required_fields):
                missing = required_fields - set(data.keys())
                raise TransactionValidationError(f"Missing required fields: {missing}")
                
            return cls(
                sender=data["sender"],
                receiver=data["receiver"],
                amount=data["amount"],
                data=data.get("data", ""),
                timestamp=data.get("timestamp", time.time()),
                tx_id=data.get("tx_id"),
                signature=data.get("signature")
            )
            
        except Exception as e:
            raise TransactionValidationError(f"Failed to create transaction from dictionary: {str(e)}")

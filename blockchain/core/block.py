from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import time
from datetime import datetime
import hashlib
import json
import logging
from .transaction import Transaction
from .fractal_coordinate import FractalCoordinate

logger = logging.getLogger(__name__)

class BlockError(Exception):
    """Base exception for block-related errors."""
    pass

class BlockValidationError(BlockError):
    """Raised when block validation fails."""
    pass

@dataclass
class Block:
    """
    A block in the blockchain that contains transactions and links to the previous block.
    
    Each block includes:
    - A unique index
    - Timestamp of creation
    - List of transactions
    - Miner's address
    - Fractal coordinates used in mining
    - Hash of the previous block
    - Its own hash (calculated)
    - Nonce used in mining
    
    Attributes:
        index (int): Block's position in the chain
        timestamp (float): Unix timestamp of block creation
        transactions (List[Transaction]): List of transactions in this block
        miner (str): Address of the miner who created this block
        fractal_coord (FractalCoordinate): Fractal coordinates used in mining
        previous_hash (str): Hash of the previous block
        hash (str): This block's hash (calculated)
        nonce (int): Nonce used to find valid hash
    """
    
    index: int
    timestamp: float
    transactions: List[Transaction]
    miner: str
    fractal_coord: FractalCoordinate
    previous_hash: str = field(default="0" * 64)
    hash: str = field(default="", init=False)
    nonce: int = field(default=0, init=False)
    
    def __post_init__(self):
        """Validate block attributes after initialization."""
        self._validate_attributes()
    
    def _validate_attributes(self) -> None:
        """
        Validate all block attributes.
        
        Raises:
            BlockValidationError: If any attribute is invalid
        """
        try:
            if not isinstance(self.index, int) or self.index < 0:
                raise BlockValidationError("Block index must be a non-negative integer")
            
            if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
                raise BlockValidationError("Block timestamp must be a positive number")
            
            if not isinstance(self.transactions, list):
                raise BlockValidationError("Transactions must be a list")
            
            for tx in self.transactions:
                if not isinstance(tx, Transaction):
                    raise BlockValidationError("All transactions must be Transaction objects")
            
            if not isinstance(self.miner, str) or not self.miner:
                raise BlockValidationError("Miner address must be a non-empty string")
            
            if not isinstance(self.fractal_coord, FractalCoordinate):
                raise BlockValidationError("Fractal coordinate must be a FractalCoordinate object")
            
            if not isinstance(self.previous_hash, str) or len(self.previous_hash) != 64:
                raise BlockValidationError("Previous hash must be a 64-character string")
            
        except Exception as e:
            logger.error(f"Block validation failed: {str(e)}")
            raise BlockValidationError(f"Block validation failed: {str(e)}")
    
    def calculate_hash(self) -> str:
        """
        Calculate the SHA-256 hash of the block.
        
        The hash is calculated from a JSON string containing all block attributes
        except the hash itself.
        
        Returns:
            str: The hexadecimal representation of the block's hash
            
        Raises:
            BlockError: If hash calculation fails
        """
        try:
            block_dict = {
                "index": self.index,
                "timestamp": self.timestamp,
                "transactions": [tx.__dict__ for tx in self.transactions],
                "previous_hash": self.previous_hash,
                "miner": self.miner,
                "fractal_coord": {
                    "a": self.fractal_coord.a,
                    "b": self.fractal_coord.b,
                    "c": self.fractal_coord.c
                },
                "nonce": self.nonce
            }
            block_string = json.dumps(block_dict, sort_keys=True)
            return hashlib.sha256(block_string.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Hash calculation failed: {str(e)}")
            raise BlockError(f"Failed to calculate block hash: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the block to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing all block attributes
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.__dict__ for tx in self.transactions],
            "miner": self.miner,
            "fractal_coord": {
                "a": self.fractal_coord.a,
                "b": self.fractal_coord.b,
                "c": self.fractal_coord.c
            },
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create a Block instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing block data
            
        Returns:
            Block: A new Block instance
            
        Raises:
            BlockValidationError: If the dictionary is missing required fields
            or contains invalid data
        """
        try:
            # Create FractalCoordinate instance
            fractal_data = data.get("fractal_coord", {})
            fractal_coord = FractalCoordinate(
                a=fractal_data.get("a", 0),
                b=fractal_data.get("b", 0),
                c=fractal_data.get("c", 0)
            )
            
            # Create Transaction instances
            transactions = [
                Transaction(**tx) for tx in data.get("transactions", [])
            ]
            
            # Create Block instance
            block = cls(
                index=data["index"],
                timestamp=data["timestamp"],
                transactions=transactions,
                miner=data["miner"],
                fractal_coord=fractal_coord,
                previous_hash=data.get("previous_hash", "0" * 64)
            )
            
            # Set hash and nonce if present
            block.hash = data.get("hash", "")
            block.nonce = data.get("nonce", 0)
            
            return block
            
        except KeyError as e:
            raise BlockValidationError(f"Missing required field: {str(e)}")
        except Exception as e:
            raise BlockValidationError(f"Failed to create block from dictionary: {str(e)}")

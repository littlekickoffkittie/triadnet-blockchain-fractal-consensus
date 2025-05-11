from dataclasses import dataclass
import random
import math
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Constants for coordinate ranges
MIN_COORDINATE = 0
MAX_COORDINATE = 500

class FractalCoordinateError(Exception):
    """Base exception for fractal coordinate-related errors."""
    pass

class CoordinateValidationError(FractalCoordinateError):
    """Raised when coordinate validation fails."""
    pass

@dataclass
class FractalCoordinate:
    """
    A three-dimensional fractal coordinate used in mining.
    
    Each coordinate represents a point in fractal space where mining operations
    can occur. The coordinates are used to adjust mining difficulty and find
    optimal mining spots.
    
    Attributes:
        a (int): First dimension coordinate
        b (int): Second dimension coordinate
        c (int): Third dimension coordinate
        
    Note:
        All coordinates must be integers between MIN_COORDINATE and MAX_COORDINATE.
    """
    
    a: int
    b: int
    c: int

    def __post_init__(self) -> None:
        """
        Validate coordinates after initialization.
        
        Raises:
            CoordinateValidationError: If any coordinate is invalid
        """
        self._validate_coordinates()
        logger.debug(f"Created fractal coordinate at ({self.a}, {self.b}, {self.c})")

    def _validate_coordinates(self) -> None:
        """
        Validate all coordinates are within allowed ranges.
        
        Raises:
            CoordinateValidationError: If any coordinate is invalid
        """
        for coord_name, value in [('a', self.a), ('b', self.b), ('c', self.c)]:
            if not isinstance(value, int):
                raise CoordinateValidationError(
                    f"Coordinate {coord_name} must be an integer, got {type(value)}"
                )
            
            if not MIN_COORDINATE <= value <= MAX_COORDINATE:
                raise CoordinateValidationError(
                    f"Coordinate {coord_name} must be between {MIN_COORDINATE} and {MAX_COORDINATE}, got {value}"
                )

    @classmethod
    def generate(cls) -> 'FractalCoordinate':
        """
        Generate random coordinates within valid ranges.
        
        Returns:
            FractalCoordinate: A new instance with random coordinates
        """
        try:
            coords = cls(
                a=random.randint(MIN_COORDINATE, MAX_COORDINATE),
                b=random.randint(MIN_COORDINATE, MAX_COORDINATE),
                c=random.randint(MIN_COORDINATE, MAX_COORDINATE)
            )
            logger.debug(f"Generated random coordinates: {coords}")
            return coords
        except Exception as e:
            logger.error(f"Failed to generate random coordinates: {str(e)}")
            raise FractalCoordinateError(f"Coordinate generation failed: {str(e)}")

    def distance_to(self, other: 'FractalCoordinate') -> float:
        """
        Calculate Euclidean distance to another coordinate.
        
        Args:
            other (FractalCoordinate): The coordinate to measure distance to
            
        Returns:
            float: The Euclidean distance between the coordinates
            
        Raises:
            CoordinateValidationError: If other coordinate is invalid
        """
        if not isinstance(other, FractalCoordinate):
            raise CoordinateValidationError("Distance calculation requires a FractalCoordinate")
            
        return math.sqrt(
            (self.a - other.a) ** 2 +
            (self.b - other.b) ** 2 +
            (self.c - other.c) ** 2
        )

    def adjust(self, delta_a: int, delta_b: int, delta_c: int) -> 'FractalCoordinate':
        """
        Create a new coordinate adjusted by the given deltas.
        
        Args:
            delta_a (int): Change in a coordinate
            delta_b (int): Change in b coordinate
            delta_c (int): Change in c coordinate
            
        Returns:
            FractalCoordinate: A new coordinate with adjusted values
            
        Raises:
            CoordinateValidationError: If resulting coordinates would be invalid
        """
        try:
            new_coords = FractalCoordinate(
                a=max(MIN_COORDINATE, min(MAX_COORDINATE, self.a + delta_a)),
                b=max(MIN_COORDINATE, min(MAX_COORDINATE, self.b + delta_b)),
                c=max(MIN_COORDINATE, min(MAX_COORDINATE, self.c + delta_c))
            )
            logger.debug(f"Adjusted coordinates from {self} to {new_coords}")
            return new_coords
        except Exception as e:
            logger.error(f"Failed to adjust coordinates: {str(e)}")
            raise FractalCoordinateError(f"Coordinate adjustment failed: {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the coordinate to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing the coordinates
        """
        return {
            "a": self.a,
            "b": self.b,
            "c": self.c
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FractalCoordinate':
        """
        Create a FractalCoordinate instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing coordinate values
            
        Returns:
            FractalCoordinate: A new FractalCoordinate instance
            
        Raises:
            CoordinateValidationError: If the dictionary is missing required fields
            or contains invalid data
        """
        try:
            required_fields = {"a", "b", "c"}
            if not all(field in data for field in required_fields):
                missing = required_fields - set(data.keys())
                raise CoordinateValidationError(f"Missing required fields: {missing}")
                
            return cls(
                a=int(data["a"]),
                b=int(data["b"]),
                c=int(data["c"])
            )
        except Exception as e:
            raise CoordinateValidationError(f"Failed to create coordinate from dictionary: {str(e)}")

    def get_neighbors(self, distance: int = 1) -> list['FractalCoordinate']:
        """
        Get neighboring coordinates at the specified distance.
        
        Args:
            distance (int): Distance to neighbors (default: 1)
            
        Returns:
            list[FractalCoordinate]: List of valid neighboring coordinates
            
        Raises:
            CoordinateValidationError: If distance is invalid
        """
        if not isinstance(distance, int) or distance < 1:
            raise CoordinateValidationError("Distance must be a positive integer")
            
        neighbors = []
        for da in [-distance, 0, distance]:
            for db in [-distance, 0, distance]:
                for dc in [-distance, 0, distance]:
                    if da == db == dc == 0:
                        continue
                    try:
                        neighbor = self.adjust(da, db, dc)
                        neighbors.append(neighbor)
                    except FractalCoordinateError:
                        continue
        return neighbors

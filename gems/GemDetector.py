import random
from gems.GemGenerator import GemGenerator

class GemDetector:
    """
    Detects gemstone artifacts during mining based on fractal coordinate events and entropy patterns.
    """

    def __init__(self):
        self.gem_generator = GemGenerator()

    def check_for_gem(self, block_hash: str, fractal_coord: dict) -> dict:
        """
        Check if a gem is discovered based on mining conditions.

        Args:
            block_hash (str): The hash of the mined block.
            fractal_coord (dict): Dictionary with keys 'a', 'b', 'c' representing fractal coordinates.

        Returns:
            dict or None: Gem metadata if discovered, else None.
        """
        # Example discovery condition: hash ends with "888" and fractalDepth % 7 == 0
        # Assuming fractalDepth is sum of coordinates for simplicity
        fractal_depth = fractal_coord['a'] + fractal_coord['b'] + fractal_coord['c']

        if block_hash.endswith("888") and fractal_depth % 7 == 0:
            gem_metadata = self.gem_generator.generate_gem(block_hash, fractal_coord)
            return gem_metadata

        # Additional random chance for gem discovery based on rarity odds
        chance = random.randint(1, 100000)
        if chance <= 10:  # 0.01% chance for rare gem discovery
            gem_metadata = self.gem_generator.generate_gem(block_hash, fractal_coord)
            return gem_metadata

        return None

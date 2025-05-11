import random
import hashlib
import json

class GemGenerator:
    """
    Generates unique gemstone artifacts based on block hash and fractal coordinates.
    """

    RARITY_TIERS = [
        {"tier": 0, "name": "Iron Ore", "description": "Basic, common", "odds": 100},
        {"tier": 1, "name": "Quartz Crystal", "description": "Slightly ordered structure", "odds": 500},
        {"tier": 2, "name": "Blood Ruby", "description": "Deep red gem formed in layered entropy", "odds": 2000},
        {"tier": 3, "name": "Obsidian Prism", "description": "Reflects fractal harmonics", "odds": 10000},
        {"tier": 4, "name": "Celestial Sapphire", "description": "Deep-blue, cosmic resonance", "odds": 50000},
        {"tier": 5, "name": "Cosmic Diamond", "description": "Rare AF. Only born in ultra-deep fractal wells", "odds": 250000},
    ]

    LORE_TEXTS = [
        "Forged in the heart of a dying star.",
        "Whispers secrets of the fractal universe.",
        "Holds the power of infinite recursion.",
        "Echoes the harmony of cosmic vibrations.",
        "Born from the chaos of fractal depths.",
        "A relic of ancient fractal civilizations."
    ]

    def __init__(self):
        pass

    def generate_gem(self, block_hash: str, fractal_coord: dict) -> dict:
        """
        Generate a gemstone artifact metadata JSON based on block hash and fractal coordinates.

        Args:
            block_hash (str): The hash of the block where gem is found.
            fractal_coord (dict): Dictionary with keys 'a', 'b', 'c' representing fractal coordinates.

        Returns:
            dict: Gem metadata including name, rarity tier, fractal signature, visual seed, block origin, and lore.
        """
        # Create a seed from block hash and fractal coordinates
        seed_input = f"{block_hash}-{fractal_coord['a']}-{fractal_coord['b']}-{fractal_coord['c']}"
        seed = int(hashlib.sha256(seed_input.encode()).hexdigest(), 16)

        random.seed(seed)

        # Determine rarity tier based on odds
        rarity_roll = random.randint(1, self.RARITY_TIERS[-1]['odds'])
        rarity = None
        for tier in reversed(self.RARITY_TIERS):
            if rarity_roll <= tier['odds']:
                rarity = tier
        if rarity is None:
            rarity = self.RARITY_TIERS[0]

        # Generate fractal signature
        fractal_signature = f"FRACT-{fractal_coord['a']}-{fractal_coord['b']}-{fractal_coord['c']}"

        # Visual seed for rendering (could be used for ASCII or 2D render)
        visual_seed = seed % 1000000

        # Select lore text
        lore = random.choice(self.LORE_TEXTS)

        gem_metadata = {
            "name": rarity['name'],
            "rarity_tier": rarity['tier'],
            "description": rarity['description'],
            "fractal_signature": fractal_signature,
            "visual_seed": visual_seed,
            "block_origin": {
                "hash": block_hash,
                "fractal_coordinates": fractal_coord
            },
            "lore": lore
        }

        return gem_metadata

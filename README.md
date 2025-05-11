Current Version: 0.1 (as of 2025-05-11)

## Overview

TriadNet is an innovative blockchain implementation that uses fractal coordinates for mining difficulty adjustment, creating a unique and mathematically beautiful consensus mechanism called Proof of Fractal Work (PoFW).

## Features

- **Proof of Fractal Work (PoFW)**: Novel consensus mechanism using fractal mathematics
- **Dynamic Difficulty**: Automatic adjustment based on fractal coordinates
- **Fractal Mining**: Unique mining algorithm that explores mathematical space
- **Smart Transaction Management**: Efficient handling of pending transactions
- **Real-time Statistics**: Comprehensive mining and blockchain statistics

## Quick Start

For detailed quick start instructions, please refer to the [QUICKSTART.md](QUICKSTART.md) file.

## Project Structure

triadnet/
├── core/           # Core blockchain components
├── consensus/      # Consensus mechanism implementation
├── crypto/        # Cryptographic utilities
└── mine.py        # Mining implementation

## Development Status

Last Updated: 2025-05-11 01:00:34 UTC

• Initial implementation complete

• Mining system operational

• Basic transaction processing working

• Fractal coordinate system implemented

## Contributors

• @littlekickoffkittie (Project Lead)

## License

MIT License - See LICENSE file for details

Last Updated: 2025-05-11 01:00:34 UTC

Prerequisites

• Python 3.8+

• pip package manager

• Virtual environment (recommended)

Installation
1. Clone the repository:
git clone https://github.com/littlekickoffkittie/triadnet.git
cd triadnet
2. Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install the package:
pip install -e .
Running the Mining Demo
python run_demo.py
You should see output similar to:
==================================================
TRIADNET MINING SYSTEM
Current Time (UTC): 2025-05-11 01:00:34
User: littlekickoffkittie
==================================================

1. Initializing wallet and blockchain...

Key Components

1. Wallet

• Automatically generated on startup

• Address format: TRIAD<40 hex characters>

2. Blockchain

• Initial difficulty: 4

• Genesis block created automatically

3. Mining

• Proof of Fractal Work consensus

• Dynamic difficulty adjustment

• Automatic coordinate optimization

4. Transactions

• Automatic reward transactions

• Support for custom transactions

Monitoring

The system provides real-time statistics:

• Chain height

• Current difficulty

• Mining rewards

• Hash rate

• Transaction pool status

Configuration

Default settings can be modified in run_demo.py:
blockchain = Blockchain(difficulty=4)  # Adjust initial difficulty
miner = Miner(
    wallet=wallet,
    blockchain=blockchain,
    fractal_coord=fractal_coord,
    auto_adjust_coords=True  # Toggle coordinate optimization
)
Troubleshooting

1. No blocks being mined

• Check difficulty setting

• Verify fractal coordinates

• Monitor system resources

2. Slow mining rate

• Reduce initial difficulty

• Adjust fractal coordinates

• Check system performance

3. Import errors

• Verify virtual environment activation

• Reinstall package: pip install -e .

Support

For issues and questions:

• Create an issue on GitHub

• Check existing documentation

• Contact: @littlekickoffkittie’ > QUICKSTART.md && echo ’# TriadNet: A Fractal-Based Blockchain ArchitectureWhite Paper - Version 0.1

Last Updated: 2025-05-11 01:00:34 UTCAuthor: @littlekickoffkittie

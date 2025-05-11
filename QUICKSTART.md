# TriadNet Quick Start Guide

Last Updated: 2025-05-11 01:00:34 UTC

## Prerequisites

- Python 3.8+
- pip package manager
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/littlekickoffkittie/triadnet.git
cd triadnet
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Running the Mining Demo

```bash
python run_demo.py
```

You should see output similar to:

```
==================================================
TRIADNET MINING SYSTEM
Current Time (UTC): 2025-05-11 01:00:34
User: littlekickoffkittie
==================================================

1. Initializing wallet and blockchain...
```

## Key Components

### Wallet

- Automatically generated on startup
- Address format: TRIAD<40 hex characters>

### Blockchain

- Initial difficulty: 4
- Genesis block created automatically

### Mining

- Proof of Fractal Work consensus
- Dynamic difficulty adjustment
- Automatic coordinate optimization

### Transactions

- Automatic reward transactions
- Support for custom transactions

## Monitoring

The system provides real-time statistics:

- Chain height
- Current difficulty
- Mining rewards
- Hash rate
- Transaction pool status

## Configuration

Default settings can be modified in `run_demo.py`:

```python
blockchain = Blockchain(difficulty=4)  # Adjust initial difficulty
miner = Miner(
    wallet=wallet,
    blockchain=blockchain,
    fractal_coord=fractal_coord,
    auto_adjust_coords=True  # Toggle coordinate optimization
)
```

## Troubleshooting

1. No blocks being mined
- Check difficulty setting
- Verify fractal coordinates
- Monitor system resources

2. Slow mining rate
- Reduce initial difficulty
- Adjust fractal coordinates
- Check system performance

3. Import errors
- Verify virtual environment activation
- Reinstall package: `pip install -e .`

## Support

For issues and questions:

- Create an issue on GitHub
- Check existing documentation
- Contact: @littlekickoffkittie

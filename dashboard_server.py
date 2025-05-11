import asyncio
import json
import websockets
import datetime
from pathlib import Path
import sys

# Add the project root to Python path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

class DashboardServer:
    def __init__(self):
        self.active_miners = set()
        self.mining_config = {
            'threads': 4,
            'algorithm': 'mandelbrot'
        }
        # Simulated data for testing
        self.chain_height = 0
        self.difficulty = 1
        self.rewards = 0
        self.hash_rate = 0
        self.connected_nodes = 0
        self.block_time = 0
        self.network_hashrate = 0
        self.active_miner_count = 0
        self.pending_transactions = []
        self.mining_logs = []

    async def handle_websocket(self, websocket):
        try:
            async for message in websocket:
                data = json.loads(message)
                response = await self.process_message(data)
                await websocket.send(json.dumps(response))
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        except Exception as e:
            print(f"Error: {e}")

    async def process_message(self, data):
        action = data.get('action')
        
        if action == 'get_dashboard_data':
            return await self.get_dashboard_data()
        
        elif action == 'start_mining':
            config = data.get('config', {})
            return await self.start_mining(config)
        
        elif action == 'stop_mining':
            return await self.stop_mining()
        
        elif action == 'update_threads':
            threads = data.get('threads')
            return await self.update_threads(threads)
        
        elif action == 'update_algorithm':
            algorithm = data.get('algorithm')
            return await self.update_algorithm(algorithm)
        
        return {'error': 'Invalid action'}

    async def get_dashboard_data(self):
        # Simulate changing data
        self.chain_height += 1
        self.difficulty = max(1, self.difficulty + 0.1)
        self.rewards += 0.5
        self.hash_rate = 1000 + (self.chain_height * 100)
        self.connected_nodes = min(10, self.chain_height // 10)
        self.block_time = 60 - min(30, self.chain_height // 10)
        self.network_hashrate = self.hash_rate * max(1, self.connected_nodes)
        self.active_miner_count = min(5, self.chain_height // 20)

        # Simulate transactions
        if len(self.pending_transactions) < 5 and self.chain_height % 3 == 0:
            tx_hash = f"0x{self.chain_height:064x}"
            self.pending_transactions.append({
                'timestamp': datetime.datetime.now(),
                'hash': tx_hash,
                'amount': round(0.1 * self.chain_height, 2)
            })

        # Simulate mining logs
        if len(self.mining_logs) < 5:
            log_entry = {
                'timestamp': datetime.datetime.now(),
                'hash': f"0x{self.chain_height:064x}",
                'x': self.chain_height * 0.1,
                'y': self.chain_height * 0.2,
                'status': 'Mining...' if self.chain_height % 2 == 0 else 'Found block!'
            }
            self.mining_logs.append(log_entry)
        
        return {
            'mining_stats': {
                'chain_height': self.chain_height,
                'difficulty': round(self.difficulty, 2),
                'rewards': round(self.rewards, 2),
                'hash_rate': f"{self.hash_rate:,}"
            },
            'network_stats': {
                'connected_nodes': self.connected_nodes,
                'avg_block_time': round(self.block_time, 2),
                'network_hashrate': f"{self.network_hashrate:,}",
                'active_miners': self.active_miner_count
            },
            'transactions': [{
                'timestamp': tx['timestamp'].strftime('%H:%M:%S'),
                'hash': tx['hash'][:16] + '...',
                'amount': tx['amount']
            } for tx in self.pending_transactions[-5:]],
            'mining_log': [{
                'timestamp': log['timestamp'].strftime('%H:%M:%S'),
                'hash': log['hash'][:16] + '...',
                'coordinates': f"({log['x']:.2f}, {log['y']:.2f})",
                'status': log['status']
            } for log in self.mining_logs[-5:]]
        }

    async def start_mining(self, config):
        threads = config.get('threads', 4)
        algorithm = config.get('algorithm', 'mandelbrot')
        
        self.mining_config['threads'] = threads
        self.mining_config['algorithm'] = algorithm
        
        print(f"Started mining with {threads} threads using {algorithm} algorithm")
        return {'status': 'Mining started'}

    async def stop_mining(self):
        print("Mining stopped")
        return {'status': 'Mining stopped'}

    async def update_threads(self, threads):
        self.mining_config['threads'] = threads
        print(f"Updated thread count to {threads}")
        return {'status': 'Thread count updated'}

    async def update_algorithm(self, algorithm):
        self.mining_config['algorithm'] = algorithm
        print(f"Updated algorithm to {algorithm}")
        return {'status': 'Algorithm updated'}

async def main():
    dashboard = DashboardServer()
    async with websockets.serve(dashboard.handle_websocket, 'localhost', 8765):
        print("Dashboard WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())

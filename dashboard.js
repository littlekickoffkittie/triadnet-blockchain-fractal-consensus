class DashboardController {
  constructor() {
    this.updateInterval = 3000; // Update every 3 seconds
    this.connectionStatus = 'Disconnected';
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.initializeElements();
    this.initializeWebSocket();
    this.setupEventListeners();
  }

  initializeElements() {
    // Status elements
    this.statusDot = document.querySelector('.status-dot');
    this.statusText = document.getElementById('connection-status');
    
    // Mining stats
    this.chainHeight = document.getElementById('chain-height');
    this.currentDifficulty = document.getElementById('current-difficulty');
    this.miningRewards = document.getElementById('mining-rewards');
    this.hashRate = document.getElementById('hash-rate');
    
    // Network stats
    this.connectedNodes = document.getElementById('connected-nodes');
    this.blockTime = document.getElementById('block-time');
    this.networkHashrate = document.getElementById('network-hashrate');
    this.activeMiners = document.getElementById('active-miners');
    
    // Mining controls
    this.workerThreads = document.getElementById('worker-threads');
    this.miningAlgorithm = document.getElementById('mining-algorithm');
    this.startMiningBtn = document.getElementById('start-mining');
    this.stopMiningBtn = document.getElementById('stop-mining');
    
    // Transaction pool
    this.transactionPool = document.getElementById('transaction-pool');
    
    // Terminal log
    this.terminalLog = document.querySelector('.terminal-table tbody');

    // Enable controls
    if (this.startMiningBtn) this.startMiningBtn.disabled = false;
    if (this.stopMiningBtn) this.stopMiningBtn.disabled = true;
  }

  initializeWebSocket() {
    try {
      this.ws = new WebSocket('ws://localhost:8765');
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.setConnectionStatus('Connected');
        this.reconnectAttempts = 0;
        this.startUpdates();
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.setConnectionStatus('Disconnected');
        this.reconnectAttempts++;
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => this.initializeWebSocket(), 5000);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.updateDashboard(data);
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      };
    } catch (error) {
      console.error('Error initializing WebSocket:', error);
    }
  }

  setConnectionStatus(status) {
    this.connectionStatus = status;
    if (this.statusText) this.statusText.textContent = status;
    if (this.statusDot) {
      this.statusDot.style.backgroundColor = status === 'Connected' ? 'var(--accent-teal)' : 'var(--text-muted)';
    }
  }

  setupEventListeners() {
    if (this.startMiningBtn) {
      this.startMiningBtn.addEventListener('click', () => {
        this.startMining();
      });
    }
    
    if (this.stopMiningBtn) {
      this.stopMiningBtn.addEventListener('click', () => {
        this.stopMining();
      });
    }
    
    if (this.workerThreads) {
      this.workerThreads.addEventListener('input', (e) => {
        this.updateWorkerThreads(e.target.value);
      });
    }
    
    if (this.miningAlgorithm) {
      this.miningAlgorithm.addEventListener('change', (e) => {
        this.updateMiningAlgorithm(e.target.value);
      });
    }
  }

  startMining() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    
    const config = {
      threads: parseInt(this.workerThreads.value),
      algorithm: this.miningAlgorithm.value
    };
    
    this.ws.send(JSON.stringify({
      action: 'start_mining',
      config: config
    }));
    
    this.startMiningBtn.disabled = true;
    this.stopMiningBtn.disabled = false;
  }

  stopMining() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    
    this.ws.send(JSON.stringify({
      action: 'stop_mining'
    }));
    
    this.startMiningBtn.disabled = false;
    this.stopMiningBtn.disabled = true;
  }

  updateWorkerThreads(value) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    
    this.ws.send(JSON.stringify({
      action: 'update_threads',
      threads: parseInt(value)
    }));
  }

  updateMiningAlgorithm(algorithm) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    
    this.ws.send(JSON.stringify({
      action: 'update_algorithm',
      algorithm: algorithm
    }));
  }

  updateDashboard(data) {
    // Update mining stats
    if (data.mining_stats) {
      if (this.chainHeight) this.chainHeight.textContent = data.mining_stats.chain_height;
      if (this.currentDifficulty) this.currentDifficulty.textContent = data.mining_stats.difficulty;
      if (this.miningRewards) this.miningRewards.textContent = `${data.mining_stats.rewards} TND`;
      if (this.hashRate) this.hashRate.textContent = `${data.mining_stats.hash_rate} H/s`;
    }
    
    // Update network stats
    if (data.network_stats) {
      if (this.connectedNodes) this.connectedNodes.textContent = data.network_stats.connected_nodes;
      if (this.blockTime) this.blockTime.textContent = `${data.network_stats.avg_block_time}s`;
      if (this.networkHashrate) this.networkHashrate.textContent = `${data.network_stats.network_hashrate} H/s`;
      if (this.activeMiners) this.activeMiners.textContent = data.network_stats.active_miners;
    }
    
    // Update transaction pool
    if (data.transactions) {
      this.updateTransactionPool(data.transactions);
    }
    
    // Update terminal log
    if (data.mining_log) {
      this.updateTerminalLog(data.mining_log);
    }
  }

  updateTransactionPool(transactions) {
    if (!this.transactionPool) return;
    
    this.transactionPool.innerHTML = '';
    
    if (transactions.length === 0) {
      this.transactionPool.innerHTML = `
        <div class="transaction-item" role="listitem" aria-label="No transactions">
          <span class="text-center w-full text-gray-400 italic select-none">No transactions to display</span>
        </div>
      `;
      return;
    }
    
    transactions.forEach(tx => {
      const txElement = document.createElement('div');
      txElement.className = 'transaction-item';
      txElement.setAttribute('role', 'listitem');
      
      txElement.innerHTML = `
        <div class="transaction-header">
          <span class="transaction-time">${tx.timestamp}</span>
        </div>
        <div class="transaction-hash">${tx.hash}</div>
        <div class="transaction-details">
          <span class="transaction-amount">${tx.amount} TND</span>
        </div>
      `;
      
      this.transactionPool.appendChild(txElement);
    });
  }

  updateTerminalLog(logs) {
    if (!this.terminalLog) return;
    
    this.terminalLog.innerHTML = logs.map(log => `
      <tr>
        <td class="timestamp-cell">${log.timestamp}</td>
        <td class="hash-cell">${log.hash}</td>
        <td class="coord-cell">${log.coordinates}</td>
        <td>${log.status}</td>
      </tr>
    `).join('');
  }

  startUpdates() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    
    // Request initial data
    this.ws.send(JSON.stringify({ action: 'get_dashboard_data' }));
    
    // Set up periodic updates
    this.updateInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'get_dashboard_data' }));
      }
    }, this.updateInterval);
  }
}

// Initialize the dashboard when the document is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dashboardController = new DashboardController();
});

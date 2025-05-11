from flask import Flask, render_template, request, jsonify
import json
from blockchain.network.ssh_connector import establish_ssh_connection, close_ssh_connection, SSHConnectionError

app = Flask(__name__)

# Store SSH connections
ssh_connections = {}

@app.route('/')
def dashboard():
    blocks = []
    try:
        with open('blocks.json', 'r') as f:
            for line in f:
                blocks.append(json.loads(line.strip()))
        blocks = blocks[-10:]
    except FileNotFoundError:
        blocks = [{'hash': 'N/A', 'nonce': 'N/A', 'duration': 0, 'coord': (0, 0, 0), 'block_time': 0, 'transactions': []}]
    return render_template('dashboard.html', blocks=blocks)

@app.route('/connect-ssh', methods=['POST'])
def connect_ssh():
    """Handle SSH connection requests"""
    try:
        data = request.get_json()
        host = data.get('host')
        username = data.get('username')
        password = data.get('password')
        
        # Validate required fields
        if not host or not username:
            return jsonify({
                "status": "error",
                "message": "Host and username are required"
            }), 400
            
        # Attempt to establish SSH connection
        client = establish_ssh_connection(
            host=host,
            username=username,
            password=password
        )
        
        # Store the connection
        connection_id = f"{username}@{host}"
        ssh_connections[connection_id] = client
        
        return jsonify({
            "status": "success",
            "message": f"Successfully connected to {connection_id}",
            "connection_id": connection_id
        })
        
    except SSHConnectionError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500

@app.route('/disconnect-ssh', methods=['POST'])
def disconnect_ssh():
    """Handle SSH disconnection requests"""
    try:
        data = request.get_json()
        connection_id = data.get('connection_id')
        
        if not connection_id or connection_id not in ssh_connections:
            return jsonify({
                "status": "error",
                "message": "Invalid connection ID"
            }), 400
            
        # Close the connection
        client = ssh_connections[connection_id]
        close_ssh_connection(client)
        
        # Remove from connections dict
        del ssh_connections[connection_id]
        
        return jsonify({
            "status": "success",
            "message": f"Successfully disconnected from {connection_id}"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error during disconnection: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

import json
import socket
import threading
from triadnet.wallet import Wallet

class Node:
    def __init__(self, node_id: str, host: str = "127.0.0.1", port: int = 5000):
        self.node_id = node_id
        self.wallet = Wallet()
        self.host = host
        self.port = port
        self.peers = {}
        self.running = True

    def start_server(self):
        threading.Thread(target=self._server_loop, daemon=True).start()

    def _server_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            while self.running:
                client, _ = s.accept()
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()

    def _handle_client(self, client_socket):
        with client_socket:
            data = client_socket.recv(4096)
            if data: print(f"[{self.node_id}] Received: {data.decode()}")

    def broadcast(self, message: dict):
        for peer_id, (host, port) in self.peers.items():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(json.dumps(message).encode())

    def add_peer(self, peer_id: str, host: str, port: int):
        self.peers[peer_id] = (host, port)

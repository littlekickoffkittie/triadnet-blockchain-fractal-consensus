#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import signal
import socket

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill any process running on the specified port using lsof"""
    try:
        # Using lsof to find and kill process
        subprocess.run(f"kill -9 $(lsof -t -i:{port}) 2>/dev/null || true", shell=True)
        time.sleep(1)
    except:
        pass

def main():
    print("\n🚀 Starting TriadNet Mining Dashboard...")
    
    # Kill any existing processes on our ports
    if is_port_in_use(8000):
        print("Cleaning up HTTP server port...")
        kill_process_on_port(8000)
    
    if is_port_in_use(8765):
        print("Cleaning up WebSocket server port...")
        kill_process_on_port(8765)
    
    print("\n1. 🔌 Initializing WebSocket Server...")
    
    # Start WebSocket server
    websocket_server = subprocess.Popen(
        [sys.executable, 'dashboard_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Give the WebSocket server time to start
    
    print("2. 🌐 Starting HTTP Server...")
    # Start HTTP server
    http_server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1)  # Give the HTTP server time to start
    
    # Check if servers are running
    if not is_port_in_use(8765):
        print("❌ Error: WebSocket server failed to start")
        sys.exit(1)
    
    if not is_port_in_use(8000):
        print("❌ Error: HTTP server failed to start")
        sys.exit(1)
    
    url = "http://localhost:8000/index%20(2).html"
    print(f"\n3. ✨ Dashboard is ready!")
    print(f"\nDashboard URL: {url}")
    print("\nPress Ctrl+C to stop all servers and exit\n")
    
    try:
        # Keep the script running and servers alive
        websocket_server.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        websocket_server.terminate()
        http_server.terminate()
        # Final cleanup
        kill_process_on_port(8000)
        kill_process_on_port(8765)
        print("✅ Servers stopped. Goodbye!\n")

if __name__ == "__main__":
    main()

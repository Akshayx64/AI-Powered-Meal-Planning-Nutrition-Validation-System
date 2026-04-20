"""
Script to start the ADK A2A server in the background.
Run this before starting the main meal planning system.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_server_health(host="localhost", port=8080, timeout=30):
    """Check if the A2A server is healthy."""
    url = f"http://{host}:{port}/health"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ A2A Server is healthy: {response.json()}")
                return True
        except requests.RequestException:
            time.sleep(1)
    
    return False

def start_server():
    """Start the A2A server in the background."""
    print("\n" + "="*80)
    print("🚀 Starting ADK A2A Server")
    print("="*80 + "\n")
    
    # Start the server as a subprocess
    server_script = Path(__file__).parent / "src" / "adk_a2a_server.py"
    
    if sys.platform == "win32":
        # Windows
        process = subprocess.Popen(
            ["python", str(server_script)],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        # Unix/Linux/Mac
        process = subprocess.Popen(
            ["python", str(server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    print(f"Server process started with PID: {process.pid}")
    print("Waiting for server to be ready...")
    
    # Wait for server to be healthy
    if check_server_health():
        print("\n✅ A2A Server is ready!")
        print("\nYou can now run: python main.py --profile profiles/keto_profile.json")
        print("\nTo stop the server, close the server window or kill the process.")
    else:
        print("\n❌ Server failed to start or health check timed out")
        process.kill()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(start_server())

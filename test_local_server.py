import requests
import time
import subprocess
import sys

def test_local():
    print("Starting local server test...\n")
    
    # Start server in background
    print("1. Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    print("2. Waiting for server to be ready...")
    time.sleep(3)
    
    try:
        # Test endpoints
        print("3. Testing endpoints...")
        
        # Health check
        response = requests.get("http://localhost:7860/health")
        assert response.status_code == 200
        print("✓ Health check passed")
        
        # Reset
        response = requests.post("http://localhost:7860/reset")
        assert response.status_code == 200
        print("✓ Reset passed")
        
        # Step
        action = {
            "appliance_actions": [
                {"appliance_id": "dishwasher", "command": "ON"}
            ],
            "battery_action": {"command": "IDLE", "power_kw": 0.0}
        }
        response = requests.post("http://localhost:7860/step", json={"action": action})
        assert response.status_code == 200
        print("✓ Step passed")
        
        # State
        response = requests.get("http://localhost:7860/state")
        assert response.status_code == 200
        print("✓ State passed")
        
        print("\n✅ All tests passed! Server works correctly.")
        
    finally:
        # Stop server
        server_process.terminate()
        server_process.wait()
        print("\nServer stopped.")

if __name__ == "__main__":
    test_local()
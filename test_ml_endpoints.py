#!/usr/bin/env python3
"""
Test ML endpoints to verify they return proper error messages
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread

def start_server():
    """Start the Flask server in background"""
    try:
        subprocess.run([sys.executable, "web_server.py"], check=False, capture_output=True)
    except:
        pass

def test_ml_endpoints():
    """Test ML endpoints return proper errors"""
    base_url = "http://localhost:5000"
    
    # Wait for server to start
    print("Starting server...")
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(3)
    
    # Test ML insights endpoint
    try:
        response = requests.get(f"{base_url}/api/ml-insights", timeout=5)
        print(f"ML Insights: HTTP {response.status_code}")
        if response.status_code == 503:
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Error: {data.get('error')}")
            print("  [OK] Returns proper 503 error")
        else:
            print(f"  [FAIL] Expected 503, got {response.status_code}")
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
    
    # Test ML training endpoint
    try:
        response = requests.post(f"{base_url}/api/ml-train", timeout=5)
        print(f"ML Training: HTTP {response.status_code}")
        if response.status_code == 503:
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Error: {data.get('error')}")
            print("  [OK] Returns proper 503 error")
        else:
            print(f"  [FAIL] Expected 503, got {response.status_code}")
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")
    
    # Test ML prediction endpoint
    try:
        test_data = {"bias": "Bullish", "session": "London", "price": 15000}
        response = requests.post(f"{base_url}/api/ml-predict", 
                               json=test_data, timeout=5)
        print(f"ML Prediction: HTTP {response.status_code}")
        if response.status_code == 503:
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Error: {data.get('error')}")
            print("  [OK] Returns proper 503 error")
        else:
            print(f"  [FAIL] Expected 503, got {response.status_code}")
    except Exception as e:
        print(f"  [FAIL] Request failed: {e}")

if __name__ == "__main__":
    print("TESTING ML ENDPOINTS...")
    print("=" * 40)
    test_ml_endpoints()
    print("=" * 40)
    print("TEST COMPLETE")
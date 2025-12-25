#!/usr/bin/env python3
"""Test the stats API endpoint"""

import requests

url = "http://localhost:5000/api/market-data/mnq/ohlcv-1m/stats"

try:
    response = requests.get(url, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to server. Is web_server.py running?")
    print("Start it with: python web_server.py")
except Exception as e:
    print(f"ERROR: {e}")

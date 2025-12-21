import requests
import time

BASE_URL = "https://web-production-f8c3.up.railway.app"

# Test price snapshot endpoint
snapshot = {
    "symbol": "NQH2025",
    "timeframe": "1m",
    "bar_ts": int(time.time() * 1000),
    "open": 16892.25,
    "high": 16894.75,
    "low": 16888.50,
    "close": 16890.25
}

response = requests.post(f"{BASE_URL}/api/price-snapshot", json=snapshot)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

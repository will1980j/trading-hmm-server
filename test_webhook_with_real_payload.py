#!/usr/bin/env python3
"""Test the webhook endpoint with a real payload from the CSV"""
import requests
import json

# Use a real payload from the CSV file
real_payload = {
    "schema_version": "1.0.0",
    "engine_version": "1.0.0",
    "strategy_name": "NQ_FVG_CORE",
    "strategy_id": "NQ_FVG_CORE",
    "strategy_version": "2025.11.20",
    "trade_id": "TEST_20251201_123456_BULLISH",
    "event_type": "ENTRY",
    "event_timestamp": "2025-12-01T00:11:00Z",
    "symbol": "MNQ1!",
    "exchange": "MNQ1!",
    "timeframe": "1",
    "session": "ASIA",
    "direction": "Bullish",
    "entry_price": 25249.75,
    "stop_loss": 25232.25,
    "risk_R": 1,
    "position_size": 4,
    "be_price": None,
    "mfe_R": 0,
    "mae_R": 0,
    "final_mfe_R": None,
    "exit_price": None,
    "exit_timestamp": None,
    "exit_reason": None,
    "targets": {
        "tp1_price": 25267.25,
        "tp2_price": 25284.75,
        "tp3_price": 25302.25,
        "target_Rs": [1, 2, 3]
    },
    "setup": {
        "setup_family": "FVG_CORE",
        "setup_variant": "HTF_ALIGNED",
        "setup_id": "FVG_CORE_HTF_ALIGNED",
        "signal_strength": 75,
        "confidence_components": {
            "trend_alignment": 1,
            "structure_quality": 0.8,
            "volatility_fit": 0.7
        }
    },
    "market_state": {
        "trend_regime": "Bullish",
        "trend_score": 0.8,
        "volatility_regime": "NORMAL"
    }
}

# Test different endpoints
endpoints = [
    'https://web-production-f8c3.up.railway.app/api/automated-signals/webhook',
    'https://web-production-f8c3.up.railway.app/api/automated-signals',
]

for url in endpoints:
    print(f"\n=== Testing: {url} ===")
    try:
        # Send as JSON
        resp = requests.post(url, json=real_payload, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

# Also test with the payload as a string (how TradingView sends it)
print("\n=== Testing with string payload (TradingView format) ===")
url = 'https://web-production-f8c3.up.railway.app/api/automated-signals/webhook'
try:
    # TradingView sends the payload as plain text in the body
    resp = requests.post(url, data=json.dumps(real_payload), 
                        headers={'Content-Type': 'application/json'}, 
                        timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

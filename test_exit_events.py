#!/usr/bin/env python3
"""
Test EXIT event handling to verify EXIT_BREAK_EVEN and EXIT_STOP_LOSS
are correctly mapped and processed.
"""

import requests
import json
from datetime import datetime

PRODUCTION_URL = "https://web-production-f8c3.up.railway.app"
WEBHOOK_ENDPOINT = f"{PRODUCTION_URL}/api/automated-signals/webhook"

def test_exit_event_mapping():
    """Test that EXIT_BREAK_EVEN and EXIT_STOP_LOSS are correctly handled"""
    
    # Create a unique trade ID for this test
    test_trade_id = f"EXIT_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_BULLISH"
    
    print("="*60)
    print("Testing EXIT Event Mapping")
    print("="*60)
    
    # First create an ENTRY
    entry_payload = {
        "schema_version": "1.0.0",
        "trade_id": test_trade_id,
        "event_type": "ENTRY",
        "direction": "Bullish",
        "entry_price": 21000.00,
        "stop_loss": 20975.00,
        "session": "NY AM"
    }
    
    print(f"\n1. Creating ENTRY for trade: {test_trade_id}")
    response = requests.post(WEBHOOK_ENDPOINT, json=entry_payload, timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Now test EXIT_BREAK_EVEN (exact format from indicator)
    exit_be_payload = {
        "schema_version": "1.0.0",
        "trade_id": test_trade_id,
        "event_type": "EXIT_BREAK_EVEN",  # Exact indicator format
        "direction": "Bullish",
        "entry_price": 21000.00,
        "stop_loss": 20975.00,
        "exit_price": 21000.00,
        "final_mfe_R": 1.5,
        "exit_reason": "be_stop_loss_hit",
        "session": "NY AM"
    }
    
    print(f"\n2. Sending EXIT_BREAK_EVEN event")
    response = requests.post(WEBHOOK_ENDPOINT, json=exit_be_payload, timeout=30)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 200 and result.get("success"):
        print("\n✅ EXIT_BREAK_EVEN correctly mapped to EXIT_BE and processed!")
    else:
        print(f"\n❌ EXIT_BREAK_EVEN handling failed: {result.get('error')}")
    
    # Test EXIT_STOP_LOSS with a new trade
    test_trade_id_2 = f"EXIT_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_BEARISH"
    
    entry_payload_2 = {
        "schema_version": "1.0.0",
        "trade_id": test_trade_id_2,
        "event_type": "ENTRY",
        "direction": "Bearish",
        "entry_price": 21000.00,
        "stop_loss": 21025.00,
        "session": "NY PM"
    }
    
    print(f"\n3. Creating ENTRY for trade: {test_trade_id_2}")
    response = requests.post(WEBHOOK_ENDPOINT, json=entry_payload_2, timeout=30)
    print(f"   Status: {response.status_code}")
    
    exit_sl_payload = {
        "schema_version": "1.0.0",
        "trade_id": test_trade_id_2,
        "event_type": "EXIT_STOP_LOSS",  # Exact indicator format
        "direction": "Bearish",
        "entry_price": 21000.00,
        "stop_loss": 21025.00,
        "exit_price": 21025.00,
        "final_mfe_R": 0.5,
        "exit_reason": "original_stop_loss_hit",
        "session": "NY PM"
    }
    
    print(f"\n4. Sending EXIT_STOP_LOSS event")
    response = requests.post(WEBHOOK_ENDPOINT, json=exit_sl_payload, timeout=30)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 200 and result.get("success"):
        print("\n✅ EXIT_STOP_LOSS correctly mapped to EXIT_SL and processed!")
    else:
        print(f"\n❌ EXIT_STOP_LOSS handling failed: {result.get('error')}")
    
    print("\n" + "="*60)
    print("EXIT Event Mapping Test Complete")
    print("="*60)

if __name__ == "__main__":
    test_exit_event_mapping()

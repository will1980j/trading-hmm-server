#!/usr/bin/env python3
"""Diagnose EXIT_BE 500 error on automated signals webhook"""

import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

def test_exit_be():
    """Test EXIT_BE webhook and capture detailed error"""
    
    # First, let's check what trades exist
    print("=" * 60)
    print("STEP 1: Check existing trades in database")
    print("=" * 60)
    
    try:
        resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            active = data.get('active_trades', [])
            completed = data.get('completed_trades', [])
            print(f"Active trades: {len(active)}")
            print(f"Completed trades: {len(completed)}")
            
            if active:
                print("\nActive trade IDs:")
                for t in active[:5]:
                    print(f"  - {t.get('trade_id')}")
        else:
            print(f"Dashboard API returned {resp.status_code}")
    except Exception as e:
        print(f"Error checking dashboard: {e}")
    
    print("\n" + "=" * 60)
    print("STEP 2: Send EXIT_BE for TEST_LIFECYCLE_001")
    print("=" * 60)
    
    # Test payload matching what the test script sends
    payload = {
        "event_type": "EXIT_BE",
        "trade_id": "TEST_LIFECYCLE_001",
        "exit_price": 21050.00,
        "final_be_mfe": 1.5,
        "final_no_be_mfe": 2.0,
        "direction": "Bullish",
        "session": "NY AM"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/automated-signals/webhook",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse Status: {resp.status_code}")
        print(f"Response Headers: {dict(resp.headers)}")
        
        try:
            response_json = resp.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {resp.text[:500]}")
            
    except Exception as e:
        print(f"Request error: {e}")
    
    print("\n" + "=" * 60)
    print("STEP 3: First create an ENTRY, then try EXIT_BE")
    print("=" * 60)
    
    import time
    test_trade_id = f"DIAG_EXIT_TEST_{int(time.time())}"
    
    # Create ENTRY first
    entry_payload = {
        "event_type": "ENTRY",
        "trade_id": test_trade_id,
        "direction": "Bullish",
        "entry_price": 21000.00,
        "stop_loss": 20975.00,
        "risk_distance": 25.0,
        "session": "NY AM",
        "bias": "Bullish"
    }
    
    print(f"\nCreating ENTRY for {test_trade_id}...")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/automated-signals/webhook",
            json=entry_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"ENTRY Response: {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"ENTRY error: {e}")
    
    # Now try EXIT_BE
    exit_payload = {
        "event_type": "EXIT_BE",
        "trade_id": test_trade_id,
        "exit_price": 21050.00,
        "final_be_mfe": 1.5,
        "final_no_be_mfe": 2.0
    }
    
    print(f"\nSending EXIT_BE for {test_trade_id}...")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/automated-signals/webhook",
            json=exit_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"EXIT_BE Response: {resp.status_code}")
        try:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
        except:
            print(f"Response text: {resp.text[:500]}")
    except Exception as e:
        print(f"EXIT_BE error: {e}")

if __name__ == "__main__":
    test_exit_be()

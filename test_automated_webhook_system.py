"""
Test Automated Trading System Webhook Integration
Simulates a complete trade lifecycle to verify the system works
"""

import requests
import json
from datetime import datetime
import time

# Your Railway webhook endpoint
WEBHOOK_URL = "https://web-production-cd33.up.railway.app/api/automated-signals"

def test_entry_signal():
    """Test 1: Entry Signal"""
    print("\n" + "="*60)
    print("TEST 1: ENTRY SIGNAL")
    print("="*60)
    
    payload = {
        "event_type": "ENTRY",
        "trade_id": "TEST_TRADE_001",
        "direction": "LONG",
        "entry_price": 21250.50,
        "stop_loss": 21225.50,
        "session": "NY AM",
        "bias": "Bullish",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "account_size": 100000,
        "risk_percent": 0.25,
        "contracts": 4,
        "risk_amount": 250.00
    }
    
    print(f"\nSending ENTRY webhook...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ ENTRY signal received successfully!")
            return True
        else:
            print(f"❌ ENTRY signal failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending ENTRY signal: {e}")
        return False


def test_mfe_update():
    """Test 2: MFE Update"""
    print("\n" + "="*60)
    print("TEST 2: MFE UPDATE")
    print("="*60)
    
    payload = {
        "event_type": "MFE_UPDATE",
        "trade_id": "TEST_TRADE_001",
        "current_price": 21275.75,
        "mfe": 1.01,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    
    print(f"\nSending MFE UPDATE webhook...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ MFE UPDATE received successfully!")
            return True
        else:
            print(f"❌ MFE UPDATE failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending MFE UPDATE: {e}")
        return False


def test_exit_be():
    """Test 3: Break-Even Exit"""
    print("\n" + "="*60)
    print("TEST 3: BREAK-EVEN EXIT")
    print("="*60)
    
    payload = {
        "event_type": "EXIT_BE",
        "trade_id": "TEST_TRADE_001",
        "exit_price": 21250.50,
        "final_mfe": 1.52,
        "timestamp": int(datetime.now().timestamp() * 1000)
    }
    
    print(f"\nSending EXIT_BE webhook...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ EXIT_BE received successfully!")
            return True
        else:
            print(f"❌ EXIT_BE failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending EXIT_BE: {e}")
        return False


def test_complete_trade_lifecycle():
    """Run complete trade lifecycle test"""
    print("\n" + "="*70)
    print("🚀 AUTOMATED TRADING SYSTEM - COMPLETE LIFECYCLE TEST")
    print("="*70)
    print(f"\nTesting webhook endpoint: {WEBHOOK_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Entry
    results.append(("ENTRY", test_entry_signal()))
    time.sleep(1)
    
    # Test 2: MFE Update
    results.append(("MFE_UPDATE", test_mfe_update()))
    time.sleep(1)
    
    # Test 3: Exit
    results.append(("EXIT_BE", test_exit_be()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your automated system is ready!")
        print("\n📋 Next Steps:")
        print("   1. Check your Railway logs to see the webhook data")
        print("   2. Check your database for the test trade")
        print("   3. Wait for market open to see real signals flow in")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   - Verify Railway is running")
        print("   - Check webhook endpoint is deployed")
        print("   - Review Railway logs for errors")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    test_complete_trade_lifecycle()

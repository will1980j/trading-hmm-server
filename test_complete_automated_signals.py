import requests
import json
import time

print("=== TESTING COMPLETE AUTOMATED SIGNALS SYSTEM ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Waiting for deployment...")
print("Press Enter after pushing changes and waiting 2-3 minutes...")
input()

print("\n1. TESTING STATS ENDPOINT:")
print("-" * 60)

try:
    response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(json.dumps(stats, indent=2))
        print(f"\n✓ Stats endpoint working!")
        print(f"  Total signals: {stats.get('stats', {}).get('total_signals', 0)}")
        print(f"  Active: {stats.get('stats', {}).get('active_count', 0)}")
    else:
        print(f"✗ Error: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n2. TESTING WEBHOOK WITH NEW SIGNAL:")
print("-" * 60)

webhook_url = f'{base_url}/api/automated-signals'

test_signal = {
    "type": "signal_created",
    "signal_id": "20241111_112000_BEARISH",
    "date": "2024-11-11",
    "time": "11:20:00",
    "bias": "Bearish",
    "session": "NY AM",
    "entry_price": 20995.25,
    "sl_price": 21020.50,
    "risk_distance": 25.25,
    "be_price": 20995.25,
    "target_1r": 20970.00,
    "target_2r": 20944.75,
    "target_3r": 20919.50,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": 1731342000000
}

try:
    response = requests.post(webhook_url, json=test_signal, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✓ Webhook accepted signal!")
        
        # Wait and check stats again
        time.sleep(2)
        stats_response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\nUpdated stats:")
            print(f"  Total signals: {stats.get('stats', {}).get('total_signals', 0)}")
            print(f"  Active: {stats.get('stats', {}).get('active_count', 0)}")
            
            if stats.get('stats', {}).get('total_signals', 0) > 0:
                print("\n✓✓✓ SYSTEM FULLY OPERATIONAL! ✓✓✓")
            else:
                print("\n⚠ Signal received but not showing in stats")
    else:
        print(f"\n✗ Webhook failed: {response.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n3. TESTING MFE UPDATE:")
print("-" * 60)

mfe_update = {
    "type": "mfe_update",
    "signal_id": "20241111_112000_BEARISH",
    "current_price": 20990.00,
    "be_mfe": 0.21,
    "no_be_mfe": 0.21,
    "timestamp": 1731342060000
}

try:
    response = requests.post(webhook_url, json=mfe_update, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✓ MFE update accepted!")
    else:
        print(f"\n✗ MFE update failed: {response.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n4. TESTING BREAK-EVEN TRIGGER:")
print("-" * 60)

be_trigger = {
    "type": "be_triggered",
    "signal_id": "20241111_112000_BEARISH",
    "be_price": 20995.25,
    "be_mfe": 1.05,
    "timestamp": 1731342120000
}

try:
    response = requests.post(webhook_url, json=be_trigger, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✓ BE trigger accepted!")
    else:
        print(f"\n✗ BE trigger failed: {response.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n5. TESTING SIGNAL COMPLETION:")
print("-" * 60)

completion = {
    "type": "signal_completed",
    "signal_id": "20241111_112000_BEARISH",
    "completion_reason": "BE_STOP_HIT",
    "exit_price": 20995.25,
    "final_mfe": 1.05,
    "timestamp": 1731342180000
}

try:
    response = requests.post(webhook_url, json=completion, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✓ Completion accepted!")
        
        # Final stats check
        time.sleep(2)
        stats_response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\nFinal stats:")
            print(f"  Total signals: {stats.get('stats', {}).get('total_signals', 0)}")
            print(f"  Active: {stats.get('stats', {}).get('active_count', 0)}")
            print(f"  Completed: {stats.get('stats', {}).get('completed_count', 0)}")
    else:
        print(f"\n✗ Completion failed: {response.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*60)
print("TRADINGVIEW SETUP:")
print("="*60)
print(f"""
Your TradingView alert configuration:

Webhook URL: {webhook_url}

The indicator will automatically send:
1. signal_created - When trade is ready to enter
2. mfe_update - Real-time MFE tracking
3. be_triggered - When break-even is hit
4. signal_completed - When trade exits

Alert Settings:
- Condition: "Complete Automated Trading System"
- Message: Use indicator's default (already formatted correctly)
- Options: "Once Per Bar Close"
- Make sure alert is ACTIVE

Dashboard URL: {base_url}/automated-signals-dashboard
""")

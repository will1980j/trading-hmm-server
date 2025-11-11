import requests
import json
import time

print("=== DEPLOYING SCHEMA FIX AND TESTING ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Step 1: Waiting for deployment to complete...")
print("(Push changes via GitHub Desktop, then wait 2-3 minutes)")
print("\nPress Enter when deployment is complete...")
input()

print("\nStep 2: Fixing database schema...")
fix_url = f'{base_url}/api/automated-signals/fix-schema'

try:
    response = requests.post(fix_url, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("\n✓ Schema fixed successfully!")
    else:
        print(f"\n✗ Schema fix failed: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    exit(1)

print("\nStep 3: Testing webhook with signal...")
webhook_url = f'{base_url}/api/automated-signals'

test_signal = {
    "type": "signal_created",
    "signal_id": "20241111_111500_BULLISH",
    "date": "2024-11-11",
    "time": "11:15:00",
    "bias": "Bullish",
    "session": "NY AM",
    "entry_price": 21005.75,
    "sl_price": 20980.50,
    "risk_distance": 25.25,
    "be_price": 21005.75,
    "target_1r": 21031.00,
    "target_2r": 21056.25,
    "target_3r": 21081.50,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": 1731341700000
}

try:
    response = requests.post(webhook_url, json=test_signal, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✓✓✓ WEBHOOK WORKING! ✓✓✓")
        
        # Check stats
        time.sleep(1)
        stats_response = requests.get(f'{base_url}/api/automated-signals/stats', timeout=10)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\nTotal signals: {stats.get('stats', {}).get('total_signals', 0)}")
            print(f"Active signals: {stats.get('stats', {}).get('active_count', 0)}")
    else:
        print(f"\n✗ Webhook failed: {response.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("""
1. Open TradingView
2. Go to your chart with the Complete Automated Trading System indicator
3. Create an alert:
   - Condition: "Complete Automated Trading System"
   - Webhook URL: https://web-production-cd33.up.railway.app/api/automated-signals
   - Message: Use the indicator's default alert message
   - Options: "Once Per Bar Close"
4. Make sure alert is ACTIVE
5. Wait for next signal confirmation on your chart
6. Check the Automated Signals Dashboard
""")

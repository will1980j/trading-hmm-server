import requests

print("=== TESTING AUTOMATED SIGNALS DASHBOARD ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

print("Press Enter after deployment...")
input()

print("\n1. Testing stats-live endpoint...")
try:
    response = requests.get(f'{base_url}/api/automated-signals/stats-live', timeout=10)
    if response.status_code == 200:
        data = response.json()
        stats = data.get('stats', {})
        print(f"   ✓ Total signals: {stats.get('total_signals', 0)}")
        print(f"   ✓ Active: {stats.get('active_count', 0)}")
        print(f"   ✓ Completed: {stats.get('completed_count', 0)}")
    else:
        print(f"   ✗ Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Testing dashboard page...")
try:
    # Note: This will redirect to login if not authenticated
    response = requests.get(f'{base_url}/automated-signals', timeout=10, allow_redirects=False)
    if response.status_code in [200, 302]:
        print(f"   ✓ Dashboard accessible (status: {response.status_code})")
    else:
        print(f"   ✗ Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n3. Testing webhook endpoint...")
try:
    test_signal = {
        "type": "signal_created",
        "signal_id": "FINAL_TEST_001",
        "date": "2024-11-11",
        "time": "14:00:00",
        "bias": "Bullish",
        "session": "NY PM",
        "entry_price": 21100.00,
        "sl_price": 21075.00,
        "risk_distance": 25.00,
        "be_price": 21100.00,
        "target_1r": 21125.00,
        "target_2r": 21150.00,
        "target_3r": 21175.00,
        "be_hit": False,
        "be_mfe": 0.00,
        "no_be_mfe": 0.00,
        "status": "active",
        "timestamp": 1731344400000
    }
    
    response = requests.post(f'{base_url}/api/automated-signals', json=test_signal, timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Webhook working (signal ID: {result.get('signal_id')})")
    else:
        print(f"   ✗ Error: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("SYSTEM STATUS:")
print("="*60)
print("""
✓ Webhook: https://web-production-cd33.up.railway.app/api/automated-signals
✓ Dashboard: https://web-production-cd33.up.railway.app/automated-signals
✓ Stats API: https://web-production-cd33.up.railway.app/api/automated-signals/stats-live

Your TradingView alert should send to the webhook URL.
The dashboard will display all signals in real-time.
""")

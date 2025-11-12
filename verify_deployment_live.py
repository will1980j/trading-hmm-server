import requests
import time

print("=" * 80)
print("VERIFYING LIVE DEPLOYMENT")
print("=" * 80)

# Test with cache-busting query parameter
url = f"https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data?_={int(time.time() * 1000)}"

print(f"\nFetching: {url}")

response = requests.get(url, headers={
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache'
})

print(f"\nStatus Code: {response.status_code}")
print("\nResponse Headers:")
print(f"  Cache-Control: {response.headers.get('Cache-Control', 'NOT SET')}")
print(f"  Pragma: {response.headers.get('Pragma', 'NOT SET')}")
print(f"  Expires: {response.headers.get('Expires', 'NOT SET')}")

if response.status_code == 200:
    data = response.json()
    
    if data.get('success'):
        active_trades = data.get('active_trades', [])
        stats = data.get('stats', {})
        debug = data.get('debug_info', {})
        
        print(f"\n✅ API Response:")
        print(f"  Total Records (debug): {debug.get('total_records')}")
        print(f"  Active Trades: {len(active_trades)}")
        print(f"  Total Signals (stats): {stats.get('total_signals')}")
        
        if active_trades:
            latest = active_trades[0]
            print(f"\n  Most Recent Active Trade:")
            print(f"    Trade ID: {latest.get('trade_id')}")
            print(f"    Signal Time: {latest.get('signal_time')}")
            print(f"    Entry: {latest.get('entry_price')}")
        
        # Check if we're getting the NEW data (should be 1900+ signals, not 90)
        total_signals = stats.get('total_signals', 0)
        if total_signals < 100:
            print(f"\n❌ STILL GETTING OLD DATA!")
            print(f"   Expected: 1900+ signals")
            print(f"   Got: {total_signals} signals")
            print(f"\n   This means the deployment hasn't taken effect yet.")
        else:
            print(f"\n✅ GETTING NEW DATA!")
            print(f"   Total signals: {total_signals}")
    else:
        print(f"\n❌ API Error: {data.get('error')}")
else:
    print(f"\n❌ HTTP Error: {response.status_code}")
    print(response.text[:500])

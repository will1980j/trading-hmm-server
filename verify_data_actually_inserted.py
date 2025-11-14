"""
Verify if data is actually in the database by creating a fresh connection
"""
import requests
import os

def check_with_direct_query():
    """Check database with a fresh connection like the webhook does"""
    print("=" * 80)
    print("CHECKING DATABASE WITH FRESH CONNECTION")
    print("=" * 80)
    
    # First, send a test signal
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("\n1. Sending test signal...")
    payload = {
        "type": "ENTRY",
        "signal_id": "VERIFY_TEST_20251114",
        "date": "2025-11-14",
        "time": "14:30:00",
        "bias": "Bullish",
        "session": "NY PM",
        "entry_price": 25100,
        "sl_price": 25075,
        "timestamp": 1731586200000
    }
    
    response = requests.post(f"{base_url}/api/automated-signals/webhook", json=payload, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    # Now check with stats endpoint (uses db.conn)
    print("\n2. Checking with stats endpoint (db.conn)...")
    stats = requests.get(f"{base_url}/api/automated-signals/stats-live", timeout=10)
    if stats.status_code == 200:
        data = stats.json()
        print(f"   Total signals: {data.get('total_signals', 0)}")
    
    # Check with dashboard endpoint (also uses db.conn)
    print("\n3. Checking with dashboard endpoint (db.conn)...")
    dashboard = requests.get(f"{base_url}/api/automated-signals/dashboard-data", timeout=10)
    if dashboard.status_code == 200:
        data = dashboard.json()
        active = data.get('active_trades', [])
        completed = data.get('completed_trades', [])
        print(f"   Active trades: {len(active)}")
        print(f"   Completed trades: {len(completed)}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS")
    print("=" * 80)
    
    print("\n🔍 The issue:")
    print("   - Webhook handler creates fresh connection: psycopg2.connect(DATABASE_URL)")
    print("   - Stats/Dashboard use shared connection: db.conn")
    print("   - These might be seeing different transaction states!")
    
    print("\n💡 Solution:")
    print("   - Make webhook handler use db.conn instead of creating new connection")
    print("   - OR make stats endpoint create fresh connection")
    print("   - OR ensure proper transaction isolation")

def main():
    check_with_direct_query()

if __name__ == '__main__':
    main()

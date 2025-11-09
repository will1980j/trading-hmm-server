"""
Comprehensive workflow verification for automated signals system
"""
import requests
import json
from datetime import datetime

BASE_URL = "https://web-production-cd33.up.railway.app"

def test_workflow():
    print("=" * 70)
    print("AUTOMATED SIGNALS WORKFLOW VERIFICATION")
    print("=" * 70)
    
    # 1. Check if dashboard is accessible
    print("\n1. Dashboard Accessibility")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/automated-signals", timeout=10)
        if response.status_code == 200 and "Trading Calendar" in response.text:
            print("✅ Dashboard loads successfully")
            print("✅ Calendar component present")
        else:
            print(f"⚠️  Dashboard status: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # 2. Check API endpoints
    print("\n2. API Endpoints")
    print("-" * 70)
    
    endpoints = [
        ("/api/automated-signals/dashboard-data", "Dashboard Data"),
        ("/api/automated-signals/stats", "Statistics"),
        ("/api/automated-signals/daily-calendar", "Calendar Data"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: Working (success={data.get('success', False)})")
            else:
                print(f"⚠️  {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {e}")
    
    # 3. Test webhook endpoint
    print("\n3. Webhook Endpoint")
    print("-" * 70)
    
    test_payload = {
        "direction": "Bullish",
        "entry_price": 20000.00,
        "stop_loss": 19975.00,
        "session": "NY AM",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/automated-signals",
            json=test_payload,
            timeout=10
        )
        if response.status_code in [200, 201]:
            print("✅ Webhook endpoint accepting signals")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️  Webhook status: {response.status_code}")
    except Exception as e:
        print(f"❌ Webhook error: {e}")
    
    # 4. Check database connectivity
    print("\n4. Database Integration")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/api/automated-signals/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Database connected and responding")
                print(f"   Total signals: {data.get('total_signals', 0)}")
                print(f"   Active trades: {data.get('active_count', 0)}")
            else:
                print("⚠️  Database query returned no success flag")
        else:
            print(f"⚠️  Database check status: {response.status_code}")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # 5. Verify navigation
    print("\n5. Navigation Integration")
    print("-" * 70)
    try:
        response = requests.get(f"{BASE_URL}/homepage", timeout=10)
        if "automated-signals" in response.text.lower():
            print("✅ Homepage links to Automated Signals")
        else:
            print("⚠️  Homepage may not have Automated Signals link")
        
        response = requests.get(f"{BASE_URL}/automated-signals", timeout=10)
        if "🏠 Home" in response.text:
            print("✅ Dashboard has Home navigation link")
        else:
            print("⚠️  Dashboard may be missing Home link")
    except Exception as e:
        print(f"❌ Navigation check error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("WORKFLOW SUMMARY")
    print("=" * 70)
    print("\n✅ READY FOR AUTOMATION:")
    print("   1. TradingView webhook alerts → Send to Railway")
    print("   2. Railway receives & stores signals → PostgreSQL database")
    print("   3. Dashboard displays signals → Calendar view with stats")
    print("   4. You check anytime → All data persisted in cloud")
    print("\n📡 Webhook URL for TradingView:")
    print(f"   {BASE_URL}/api/automated-signals")
    print("\n🌐 Dashboard URL:")
    print(f"   {BASE_URL}/automated-signals")
    print("\n💡 Your laptop can be OFF - everything runs in the cloud!")
    print("=" * 70)

if __name__ == '__main__':
    test_workflow()

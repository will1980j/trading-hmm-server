"""
Check Railway production database via API - NO direct database connection
"""
import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("CHECKING RAILWAY PRODUCTION VIA API")
print("=" * 80)

# Check dashboard-data endpoint
print("\n1. Checking /api/automated-signals/dashboard-data...")
try:
    r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        
        active = data.get('active_trades', [])
        completed = data.get('completed_trades', [])
        
        print(f"Active trades: {len(active)}")
        print(f"Completed trades: {len(completed)}")
        
        if active:
            print("\nFirst active trade:")
            t = active[0]
            print(f"  Trade ID: {t.get('trade_id')}")
            print(f"  Direction: {t.get('direction')}")
            print(f"  Entry: {t.get('entry_price')}")
            print(f"  BE MFE: {t.get('be_mfe')}")
            print(f"  No BE MFE: {t.get('no_be_mfe')}")
            print(f"  Current Price: {t.get('current_price')}")
            
            if t.get('be_mfe', 0) == 0 and t.get('no_be_mfe', 0) == 0:
                print("\n  ❌ MFE VALUES ARE STILL 0.00")
                print("  Either deployment not complete OR no MFE_UPDATE events exist")
            else:
                print("\n  ✅ MFE VALUES ARE NON-ZERO - FIX WORKING!")
    else:
        print(f"Error: {r.status_code}")
        print(r.text[:500])
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)

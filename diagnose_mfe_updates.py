"""
Diagnose MFE update issue - why are MFE values stuck at 0.00?
Using API only to check if MFE updates are being stored
"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("MFE UPDATE DIAGNOSTIC")
print("=" * 80)

# Get active trades and check their MFE values
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=10)
    data = resp.json()
    
    active = data.get('active_trades', [])
    
    print(f"\n✅ Found {len(active)} active trades")
    
    if active:
        print(f"\nChecking MFE values for active trades:")
        
        zero_mfe_count = 0
        nonzero_mfe_count = 0
        
        for trade in active[:10]:
            trade_id = trade['trade_id']
            be_mfe = trade.get('be_mfe', 0)
            no_be_mfe = trade.get('no_be_mfe', 0)
            
            print(f"\n  {trade_id}:")
            print(f"    BE MFE: {be_mfe}R")
            print(f"    No BE MFE: {no_be_mfe}R")
            
            if be_mfe == 0 and no_be_mfe == 0:
                zero_mfe_count += 1
                print(f"    ⚠️  Both MFE values are 0.00")
            else:
                nonzero_mfe_count += 1
                print(f"    ✅ MFE values are updating")
        
        print(f"\n📊 Summary:")
        print(f"  Trades with 0.00 MFE: {zero_mfe_count}")
        print(f"  Trades with non-zero MFE: {nonzero_mfe_count}")
        
        if zero_mfe_count == len(active[:10]):
            print(f"\n🚨 ALL TRADES HAVE 0.00 MFE")
            print(f"   This means MFE_UPDATE webhooks are NOT being stored on ENTRY rows")
            print(f"\n   Possible causes:")
            print(f"   1. handle_mfe_update function not updating ENTRY row")
            print(f"   2. MFE_UPDATE webhooks not being received")
            print(f"   3. Database UPDATE query failing silently")
        elif zero_mfe_count > 0:
            print(f"\n⚠️  SOME trades have 0.00 MFE")
            print(f"   These might be very new trades that haven't received MFE_UPDATE yet")
        else:
            print(f"\n✅ MFE updates are working correctly")
    else:
        print(f"\n⚠️  No active trades to check")
        
except Exception as e:
    print(f"❌ Error: {e}")

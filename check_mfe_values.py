import requests
import json

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

print("=" * 80)
print("ACTIVE TRADES (BE=1:ACTIVE, No-BE:ACTIVE):")
print("=" * 80)
active = data.get('active_trades', [])
for t in active[:10]:
    be_status = t.get('be_status', 'UNKNOWN')
    no_be_status = t.get('no_be_status', 'UNKNOWN')
    be_mfe = t.get('be_mfe', 0)
    no_be_mfe = t.get('no_be_mfe', 0)
    mae = t.get('mae_global_r', 0)
    
    print(f"\n{t['trade_id']}:")
    print(f"  BE=1: {be_status} (MFE: {be_mfe}R)")
    print(f"  No-BE: {no_be_status} (MFE: {no_be_mfe}R)")
    print(f"  MAE: {mae}R")
    
    # Flag issues
    if be_status == 'ACTIVE' and no_be_status == 'ACTIVE' and no_be_mfe == 0:
        print(f"  ⚠️ ISSUE: No-BE MFE stuck at 0.00R")
    if be_status == 'COMPLETE' and no_be_status == 'ACTIVE' and be_mfe == no_be_mfe:
        print(f"  ⚠️ ISSUE: BE=1 COMPLETE but No-BE MFE same as BE MFE")
    if be_mfe < 0 or no_be_mfe < 0:
        print(f"  ⚠️ ISSUE: Negative MFE values (should be MAE)")

print("\n" + "=" * 80)
print("COMPLETED TRADES (BE=1:COMPLETE, No-BE:ACTIVE):")
print("=" * 80)
completed = data.get('completed_trades', [])
for t in completed[:10]:
    be_status = t.get('be_status', 'UNKNOWN')
    no_be_status = t.get('no_be_status', 'UNKNOWN')
    be_mfe = t.get('be_mfe', 0)
    no_be_mfe = t.get('no_be_mfe', 0)
    mae = t.get('mae_global_r', 0)
    
    if be_status == 'COMPLETE' and no_be_status == 'ACTIVE':
        print(f"\n{t['trade_id']}:")
        print(f"  BE=1: {be_status} (MFE: {be_mfe}R)")
        print(f"  No-BE: {no_be_status} (MFE: {no_be_mfe}R)")
        print(f"  MAE: {mae}R")
        
        if be_mfe == no_be_mfe:
            print(f"  ⚠️ ISSUE: No-BE should continue updating after BE=1 completes")

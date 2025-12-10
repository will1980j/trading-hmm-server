import requests

# Get dashboard data
r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

active_trades = data.get('active_trades', [])
completed_trades = data.get('completed_trades', [])

print(f"Active trades: {len(active_trades)}")
print(f"Completed trades: {len(completed_trades)}")
print("=" * 80)

print("\nActive trades (should these be completed?):")
print("=" * 80)

for trade in active_trades[:15]:
    trade_id = trade['trade_id']
    direction = trade['direction']
    be_status = trade.get('be_status', 'UNKNOWN')
    no_be_status = trade.get('no_be_status', 'UNKNOWN')
    be_mfe = trade.get('be_mfe', 0)
    no_be_mfe = trade.get('no_be_mfe', 0)
    
    print(f"\n{trade_id} ({direction})")
    print(f"  BE=1: {be_status} (MFE: {be_mfe}R)")
    print(f"  No-BE: {no_be_status} (MFE: {no_be_mfe}R)")
    
    # Flag suspicious cases
    if be_status == 'COMPLETE' and no_be_status == 'COMPLETE':
        print(f"  ⚠️ BOTH COMPLETE - Should be in completed_trades!")
    if be_mfe < 0 or no_be_mfe < 0:
        print(f"  ⚠️ NEGATIVE MFE - Trade likely stopped out!")

print("\n" + "=" * 80)
print("Recent completed trades:")
print("=" * 80)

for trade in completed_trades[:5]:
    trade_id = trade['trade_id']
    direction = trade['direction']
    be_mfe = trade.get('be_mfe', 0)
    no_be_mfe = trade.get('no_be_mfe', 0)
    final_mfe = trade.get('final_mfe', 0)
    
    print(f"\n{trade_id} ({direction})")
    print(f"  BE MFE: {be_mfe}R, No-BE MFE: {no_be_mfe}R")
    print(f"  Final MFE: {final_mfe}R")

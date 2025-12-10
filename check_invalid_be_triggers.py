import requests

r = requests.get('https://web-production-f8c3.up.railway.app/api/automated-signals/dashboard-data')
data = r.json()

all_trades = data.get('active_trades', []) + data.get('completed_trades', [])

print("Checking for invalid BE triggers (BE triggered but MFE < 1R):")
print("=" * 80)

problem_trades = []
for trade in all_trades:
    be_status = trade.get('be_status', 'UNKNOWN')
    be_mfe = trade.get('be_mfe', 0)
    no_be_mfe = trade.get('no_be_mfe', 0)
    
    # BE should only trigger if MFE >= 1R
    if be_status in ['COMPLETE', 'ACTIVE'] and be_mfe < 1.0:
        problem_trades.append(trade)
        print(f"\n⚠️ {trade['trade_id']} ({trade['direction']})")
        print(f"  BE Status: {be_status}")
        print(f"  BE MFE: {be_mfe}R (should be >= 1.0R)")
        print(f"  No-BE MFE: {no_be_mfe}R")
        print(f"  Entry: {trade.get('entry_price')}, Stop: {trade.get('stop_loss')}")

if len(problem_trades) == 0:
    print("✅ No invalid BE triggers found")
else:
    print(f"\n{'='*80}")
    print(f"Found {len(problem_trades)} trades with invalid BE triggers")

import requests
import json

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("CHECKING DASHBOARD API RESPONSE STRUCTURE")
print("=" * 80)

response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = response.json()

print(f"\nActive Trades: {len(data['active_trades'])}")
print(f"Completed Trades: {len(data['completed_trades'])}")

if data['active_trades']:
    print("\n" + "=" * 80)
    print("FIRST ACTIVE TRADE - ALL FIELDS:")
    print("=" * 80)
    print(json.dumps(data['active_trades'][0], indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("CHECKING MFE VALUES IN ACTIVE TRADES:")
    print("=" * 80)
    
    missing_mfe_count = 0
    for trade in data['active_trades']:
        trade_id = trade.get('trade_id', 'UNKNOWN')
        be_mfe = trade.get('be_mfe')
        no_be_mfe = trade.get('no_be_mfe')
        
        if be_mfe is None and no_be_mfe is None:
            missing_mfe_count += 1
            print(f"{trade_id}: BE_MFE={be_mfe}, NO_BE_MFE={no_be_mfe} ❌ MISSING")
        else:
            print(f"{trade_id}: BE_MFE={be_mfe}, NO_BE_MFE={no_be_mfe} ✓")
    
    print(f"\nMissing MFE: {missing_mfe_count}/{len(data['active_trades'])} ({missing_mfe_count/len(data['active_trades'])*100:.1f}%)")

if data['completed_trades']:
    print("\n" + "=" * 80)
    print("FIRST COMPLETED TRADE - ALL FIELDS:")
    print("=" * 80)
    print(json.dumps(data['completed_trades'][0], indent=2, default=str))
    
    print("\n" + "=" * 80)
    print("CHECKING COMPLETION STATUS:")
    print("=" * 80)
    
    for trade in data['completed_trades'][:10]:
        trade_id = trade.get('trade_id', 'UNKNOWN')
        status = trade.get('status', 'UNKNOWN')
        print(f"{trade_id}: Status={status}")

print("\n" + "=" * 80)

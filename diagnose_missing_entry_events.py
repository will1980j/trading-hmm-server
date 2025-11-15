import requests
import json

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("DIAGNOSING MISSING MFE UPDATES")
print("=" * 80)

response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = response.json()

print(f"\nActive Trades: {len(data['active_trades'])}")
print(f"Completed Trades: {len(data['completed_trades'])}")

print("\n" + "=" * 80)
print("ACTIVE TRADES - CHECKING FOR ENTRY EVENTS")
print("=" * 80)

trades_with_zero_mfe = []
trades_with_mfe = []

for trade in data['active_trades']:
    trade_id = trade['trade_id']
    be_mfe = trade.get('be_mfe', 0)
    no_be_mfe = trade.get('no_be_mfe', 0)
    
    if be_mfe == 0 and no_be_mfe == 0:
        trades_with_zero_mfe.append(trade_id)
        print(f"❌ {trade_id}: MFE=0.0 (NO MFE_UPDATE events)")
    else:
        trades_with_mfe.append(trade_id)
        print(f"✅ {trade_id}: BE_MFE={be_mfe:.2f}R, NO_BE_MFE={no_be_mfe:.2f}R")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Trades with MFE data: {len(trades_with_mfe)}")
print(f"Trades missing MFE data: {len(trades_with_zero_mfe)}")
print(f"Percentage missing: {len(trades_with_zero_mfe)/len(data['active_trades'])*100:.1f}%")

print("\n" + "=" * 80)
print("ROOT CAUSE ANALYSIS")
print("=" * 80)
print("""
The indicator only sends MFE_UPDATE webhooks for trades where:
1. Signal occurred in REAL-TIME (not historical)
2. ENTRY webhook was successfully sent
3. At least 1 bar has passed since entry

If trades show 0.0 MFE, it means:
- Indicator was restarted/reloaded after trade entered
- TradingView was closed and reopened
- Chart was refreshed
- ENTRY webhook failed to send

SOLUTION:
The indicator needs to track ALL active trades, not just those it created.
This requires checking the database for active trades on startup.
""")

print("\n" + "=" * 80)
print("IMMEDIATE WORKAROUND")
print("=" * 80)
print("""
Option 1: Delete trades with 0.0 MFE (they're test/stale trades)
Option 2: Wait for trades to naturally complete (hit BE or SL)
Option 3: Modify indicator to track ALL active trades from database
""")

import requests
import json

base_url = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("CHECKING WHAT WEBHOOK EVENTS ARE IN DATABASE")
print("=" * 80)

# Get dashboard data
response = requests.get(f"{base_url}/api/automated-signals/dashboard-data")
data = response.json()

print(f"\nActive Trades: {len(data.get('active_trades', []))}")
print(f"Completed Trades: {len(data.get('completed_trades', []))}")

if data.get('active_trades'):
    print("\n--- SAMPLE ACTIVE TRADE ---")
    trade = data['active_trades'][0]
    print(json.dumps(trade, indent=2))
    print(f"\nMFE Value: {trade.get('current_mfe')}")
    print(f"Trade Status: {trade.get('trade_status')}")

# Now let's check TradingView alert log to see if webhooks are firing
print("\n" + "=" * 80)
print("NEXT STEPS TO DEBUG:")
print("=" * 80)
print("\n1. Check TradingView Alert Log:")
print("   - Right-click chart → Alert Log")
print("   - Look for recent alerts firing")
print("   - Should see alerts every minute for MFE updates")
print("\n2. Check what types of alerts are firing:")
print("   - signal_created (when trade confirms)")
print("   - mfe_update (every minute)")
print("   - signal_completed (when stop loss hits)")
print("\n3. If NO alerts in log:")
print("   - Strategy might not be running")
print("   - Alert might be paused")
print("   - Strategy might have errors")
print("\n4. If alerts ARE firing but no MFE data:")
print("   - Check Railway logs for webhook errors")
print("   - Webhook URL might be wrong")
print("   - Backend might be rejecting webhooks")

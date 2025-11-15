import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

print("=" * 80)
print("CHECKING IF MFE_UPDATE WEBHOOKS ARE BEING RECEIVED")
print("=" * 80)

# Check webhook stats
response = requests.get(f"{BASE_URL}/api/webhook-stats")
if response.status_code == 200:
    stats = response.json()
    print("\nWebhook Stats:")
    print(f"  Total Webhooks: {stats.get('total_webhooks', 'N/A')}")
    print(f"  Last Webhook: {stats.get('last_webhook_time', 'N/A')}")
else:
    print(f"\nWebhook stats endpoint returned: {response.status_code}")

# Get dashboard data to see MFE values
response = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
data = response.json()

print("\n" + "=" * 80)
print("ACTIVE TRADES MFE STATUS")
print("=" * 80)

for trade in data['active_trades']:
    trade_id = trade['trade_id']
    be_mfe = trade.get('be_mfe', 0)
    no_be_mfe = trade.get('no_be_mfe', 0)
    
    if be_mfe > 0 or no_be_mfe > 0:
        print(f"✓ {trade_id}: BE_MFE={be_mfe:.2f}R, NO_BE_MFE={no_be_mfe:.2f}R")
    else:
        print(f"⏳ {trade_id}: Waiting for MFE updates (just entered)")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
If you see trades with non-zero MFE values, the system is working correctly!

Trades showing 0.0 MFE are either:
1. Just entered (haven't completed 1 bar yet)
2. Not receiving MFE_UPDATE webhooks (indicator issue)

The indicator sends MFE_UPDATE once per bar for active trades.
On a 1-minute chart, you should see updates every minute.
""")

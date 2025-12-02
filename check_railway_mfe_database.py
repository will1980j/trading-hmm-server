"""
Check Railway database for MFE_UPDATE events
"""
import requests

# Use the Railway API endpoint to check database
BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("CHECKING RAILWAY DATABASE FOR MFE_UPDATE EVENTS")
print("=" * 80)

# Create a simple diagnostic endpoint call
print("\n1. Checking for MFE_UPDATE events via API...")

try:
    # We'll use a simple query to check event types
    r = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data")
    data = r.json()
    
    print(f"Response status: {r.status_code}")
    print(f"Active trades: {len(data.get('active_trades', []))}")
    print(f"Completed trades: {len(data.get('completed_trades', []))}")
    
    # Check all active trades
    print("\nActive trades MFE values:")
    for trade in data.get('active_trades', []):
        print(f"  {trade['trade_id'][:30]}...")
        print(f"    BE MFE: {trade.get('be_mfe', 0)}")
        print(f"    No BE MFE: {trade.get('no_be_mfe', 0)}")
        print(f"    Current Price: {trade.get('current_price')}")
        print()
        
except Exception as e:
    print(f"Error: {e}")

# Check webhook stats to see if MFE_UPDATE events are being received
print("\n2. Checking webhook stats...")
try:
    r = requests.get(f"{BASE_URL}/api/webhook-stats")
    if r.status_code == 200:
        stats = r.json()
        print(f"Total webhooks: {stats.get('total_webhooks', 0)}")
        
        # Look for event type breakdown
        if 'event_types' in stats:
            print("\nEvent type breakdown:")
            for event_type, count in stats['event_types'].items():
                print(f"  {event_type}: {count}")
    else:
        print(f"Webhook stats not available (status {r.status_code})")
except Exception as e:
    print(f"Error checking webhook stats: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)
print("If MFE values are 0.00, possible causes:")
print("1. Railway deployment hasn't completed yet (check Railway dashboard)")
print("2. No MFE_UPDATE webhooks have been received (indicator not running)")
print("3. The fix was deployed but there's a query issue")
print("\nNext steps:")
print("- Wait 2-3 minutes for Railway deployment to complete")
print("- Check TradingView indicator is running and sending MFE_UPDATE every 60s")
print("- Verify the indicator webhook URL is correct")
print("=" * 80)

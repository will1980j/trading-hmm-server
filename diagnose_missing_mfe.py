import requests
import json

# Fetch dashboard data from Railway
url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"

print("Fetching dashboard data from Railway...\n")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    active_trades = data.get('active_trades', [])
    completed_trades = data.get('completed_trades', [])
    
    print(f"Total active trades: {len(active_trades)}")
    print(f"Total completed trades: {len(completed_trades)}\n")
    
    print("=" * 80)
    print("ACTIVE TRADES WITH MISSING MFE:")
    print("=" * 80)
    
    missing_mfe_count = 0
    has_mfe_count = 0
    
    for trade in active_trades:
        trade_id = trade.get('trade_id', 'unknown')
        be_mfe = trade.get('be_mfe')
        no_be_mfe = trade.get('no_be_mfe')
        entry_price = trade.get('entry_price')
        signal_time = trade.get('signal_time', 'unknown')
        
        # Check if MFE is missing (None, 0, or not present)
        if be_mfe is None or be_mfe == 0:
            missing_mfe_count += 1
            print(f"\n❌ {trade_id}")
            print(f"   Time: {signal_time}")
            print(f"   Entry: {entry_price}")
            print(f"   BE MFE: {be_mfe}")
            print(f"   No BE MFE: {no_be_mfe}")
            print(f"   Status: {trade.get('status', 'unknown')}")
        else:
            has_mfe_count += 1
    
    print(f"\n" + "=" * 80)
    print(f"SUMMARY:")
    print(f"=" * 80)
    print(f"Active trades WITH MFE: {has_mfe_count}")
    print(f"Active trades WITHOUT MFE: {missing_mfe_count}")
    print(f"Percentage missing: {(missing_mfe_count / len(active_trades) * 100):.1f}%")
    
    # Check if there are MFE_UPDATE events in database
    print(f"\n" + "=" * 80)
    print(f"CHECKING FOR MFE_UPDATE EVENTS:")
    print(f"=" * 80)
    
    # Sample a few trades to see their event history
    print("\nSample trade event history (first 3 active trades):")
    for i, trade in enumerate(active_trades[:3]):
        print(f"\n{i+1}. Trade: {trade.get('trade_id')}")
        print(f"   Entry Price: {trade.get('entry_price')}")
        print(f"   BE MFE: {trade.get('be_mfe')}")
        print(f"   No BE MFE: {trade.get('no_be_mfe')}")
        print(f"   Latest Event Type: {trade.get('event_type', 'unknown')}")
        print(f"   Created At: {trade.get('created_at', 'unknown')}")
        
else:
    print(f"❌ Failed to fetch data: {response.status_code}")
    print(response.text[:500])

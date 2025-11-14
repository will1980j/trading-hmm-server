import requests

url = "https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    active = data.get('active_trades', [])
    
    print(f"Active trades: {len(active)}")
    
    if active:
        trade = active[0]
        print(f"\nFirst trade:")
        print(f"  Trade ID: {trade.get('trade_id')}")
        print(f"  BE MFE: {trade.get('be_mfe')}")
        print(f"  No BE MFE: {trade.get('no_be_mfe')}")
        print(f"  Entry: {trade.get('entry_price')}")
        
        # Check if values are still 0
        if trade.get('be_mfe') == 0.0:
            print("\n❌ MFE still showing 0.0")
            print("This means either:")
            print("1. Deployment hasn't completed yet")
            print("2. No MFE_UPDATE events exist in database")
            print("3. The LATERAL JOIN isn't finding them")
else:
    print(f"Error: {response.status_code}")

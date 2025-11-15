import requests

# First get dashboard data to find a real trade
dashboard_url = 'https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data'
dash_response = requests.get(dashboard_url)
dash_data = dash_response.json()

# Find first bullish trade
bullish_trades = [t for t in dash_data.get('active_trades', []) + dash_data.get('completed_trades', []) 
                  if t.get('direction') == 'Bullish']

if not bullish_trades:
    print("No bullish trades found")
    exit()

trade_id = bullish_trades[0].get('trade_id')
print(f"Testing trade: {trade_id}\n")

# Get specific trade
url = f'https://web-production-cd33.up.railway.app/api/automated-signals/trade-detail/{trade_id}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        trade = data['trade']
        
        print(f"Trade ID: {trade.get('trade_id')}")
        print(f"Direction: {trade.get('direction')}")
        print(f"Entry Price: {trade.get('entry_price')}")
        print(f"Stop Loss: {trade.get('stop_loss')}")
        print(f"Risk Distance: {trade.get('risk_distance')}")
        print(f"No BE MFE: {trade.get('no_be_mfe')}")
        
        entry = trade.get('entry_price') or 0
        stop = trade.get('stop_loss') or 0
        risk = trade.get('risk_distance') or 0
        mfe = trade.get('no_be_mfe') or 0
        
        print(f"\nCalculations:")
        print(f"Risk Distance (should be positive for long): {risk}")
        print(f"Entry - Stop: {entry - stop}")
        print(f"For +{mfe}R, price should be: {entry + mfe * risk}")
        print(f"That's {mfe * risk} points above entry")
        
        # Check if risk distance matches
        if abs(risk - abs(entry - stop)) > 1:
            print(f"\n⚠️ WARNING: Risk distance ({risk}) doesn't match entry-stop ({abs(entry - stop)})")
else:
    print(f"Error: {response.status_code}")

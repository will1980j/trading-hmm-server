import requests

# Get dashboard data
url = 'https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data'
response = requests.get(url)
data = response.json()

# Find any bullish trade
bullish_trades = [t for t in data.get('active_trades', []) + data.get('completed_trades', []) 
                  if t.get('direction') == 'Bullish']

if bullish_trades:
    trade = bullish_trades[0]
    print(f"Testing bullish trade: {trade.get('trade_id')}")
    print(f"Direction: {trade.get('direction')}")
    print(f"No BE MFE: {trade.get('no_be_mfe')}")
    
    # Get detail
    detail_url = f"https://web-production-cd33.up.railway.app/api/automated-signals/trade-detail/{trade.get('trade_id')}"
    detail_response = requests.get(detail_url)
    detail_data = detail_response.json()
    
    if detail_data.get('success'):
        trade_detail = detail_data['trade']
        print(f"\nTrade Detail:")
        print(f"Direction: {trade_detail.get('direction')}")
        print(f"Entry Price: {trade_detail.get('entry_price')}")
        print(f"Stop Loss: {trade_detail.get('stop_loss')}")
        print(f"Risk Distance: {trade_detail.get('risk_distance')}")
        print(f"No BE MFE: {trade_detail.get('no_be_mfe')}")
        
        print(f"\nEvents ({len(trade_detail.get('events', []))}):")
        for i, event in enumerate(trade_detail.get('events', [])[:5]):
            print(f"  {i+1}. {event.get('event_type')} - Direction: {event.get('direction')} - MFE: {event.get('no_be_mfe')} - Time: {event.get('signal_time') or event.get('timestamp')}")
else:
    print("No bullish trades found")
    print(f"Total active: {len(data.get('active_trades', []))}")
    print(f"Total completed: {len(data.get('completed_trades', []))}")
    
    # Show first few trades
    all_trades = data.get('active_trades', []) + data.get('completed_trades', [])
    print(f"\nFirst 5 trades:")
    for t in all_trades[:5]:
        print(f"  {t.get('trade_id')} - {t.get('direction')} - MFE: {t.get('no_be_mfe')}")

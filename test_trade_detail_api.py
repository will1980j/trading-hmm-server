import requests
import json

# Test the trade detail endpoint with a real trade ID
url = 'https://web-production-cd33.up.railway.app/api/automated-signals/dashboard-data'

try:
    response = requests.get(url)
    print(f'Dashboard data status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        
        # Get a real trade ID
        active_trades = data.get('active_trades', [])
        completed_trades = data.get('completed_trades', [])
        
        print(f'\nActive trades: {len(active_trades)}')
        print(f'Completed trades: {len(completed_trades)}')
        
        # Test with first available trade
        test_trade = None
        if active_trades:
            test_trade = active_trades[0]
            print(f'\nTesting with active trade: {test_trade.get("trade_id")}')
        elif completed_trades:
            test_trade = completed_trades[0]
            print(f'\nTesting with completed trade: {test_trade.get("trade_id")}')
        
        if test_trade:
            trade_id = test_trade.get('trade_id')
            detail_url = f'https://web-production-cd33.up.railway.app/api/automated-signals/trade-detail/{trade_id}'
            
            print(f'\nFetching detail from: {detail_url}')
            detail_response = requests.get(detail_url)
            print(f'Detail status: {detail_response.status_code}')
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                print(f'\nTrade detail keys: {list(detail_data.keys())}')
                print(f'Direction: {detail_data.get("direction")}')
                print(f'Entry price: {detail_data.get("entry_price")}')
                print(f'Stop loss: {detail_data.get("stop_loss")}')
                print(f'No BE MFE: {detail_data.get("no_be_mfe")}')
                print(f'BE MFE: {detail_data.get("be_mfe")}')
                print(f'Latest event: {detail_data.get("latest_event_type")}')
                print(f'\nHas events: {"events" in detail_data}')
                if 'events' in detail_data:
                    print(f'Number of events: {len(detail_data.get("events", []))}')
                    for i, event in enumerate(detail_data.get('events', [])[:3]):
                        print(f'  Event {i+1}: {event.get("event_type")} - MFE: {event.get("no_be_mfe")}')
            else:
                print(f'Error: {detail_response.text}')
    else:
        print(f'Error: {response.text}')
        
except Exception as e:
    print(f'Exception: {e}')
    import traceback
    traceback.print_exc()

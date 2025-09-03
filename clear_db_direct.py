import requests

def clear_via_api():
    """Clear via existing API endpoint"""
    try:
        # Use the existing GET endpoint to see current signals
        response = requests.get('https://web-production-cd33.up.railway.app/api/live-signals?timeframe=1m')
        print(f"Current signals status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            print(f"Found {len(signals)} signals in database")
            
            if signals:
                print("Signals found - they need to be cleared from the database directly")
                for signal in signals[:3]:  # Show first 3
                    print(f"- {signal.get('symbol')} {signal.get('signal_type')} at {signal.get('timestamp')}")
            else:
                print("No signals found - database is already clean")
        else:
            print(f"API Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_via_api()
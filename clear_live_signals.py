import requests

def clear_live_signals():
    """Clear all live signals from database"""
    try:
        # Call the clear endpoint
        response = requests.delete('https://web-production-cd33.up.railway.app/api/live-signals/clear-all')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    clear_live_signals()
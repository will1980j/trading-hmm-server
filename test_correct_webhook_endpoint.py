import requests
import json
from datetime import datetime

print("=== TESTING CORRECT AUTOMATED SIGNALS WEBHOOK ===\n")

webhook_url = 'https://web-production-cd33.up.railway.app/api/automated-signals'

# Test payload matching your indicator's format
test_payload = {
    "type": "signal_created",
    "signal_id": "20241111_110645_BULLISH",
    "date": "2024-11-11",
    "time": "11:06:45",
    "bias": "Bullish",
    "session": "NY AM",
    "entry_price": 21000.50,
    "sl_price": 20975.25,
    "risk_distance": 25.25,
    "be_price": 21000.50,
    "target_1r": 21025.75,
    "target_2r": 21051.00,
    "target_3r": 21076.25,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": 1731340005000
}

print("Testing webhook endpoint:")
print(f"URL: {webhook_url}")
print(f"\nPayload:")
print(json.dumps(test_payload, indent=2))

try:
    response = requests.post(webhook_url, json=test_payload, timeout=10)
    print(f"\n✓ Response Status: {response.status_code}")
    print(f"✓ Response Body: {response.text}\n")
    
    if response.status_code == 200:
        print("SUCCESS! Webhook is working!")
        
        # Check if signal was saved
        print("\nChecking if signal was saved to database...")
        stats_url = 'https://web-production-cd33.up.railway.app/api/automated-signals/stats'
        stats_response = requests.get(stats_url, timeout=10)
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"Total signals: {stats.get('stats', {}).get('total_signals', 0)}")
            print(f"Active signals: {stats.get('stats', {}).get('active_count', 0)}")
            
            if stats.get('stats', {}).get('total_signals', 0) > 0:
                print("\n✓✓✓ SIGNAL SUCCESSFULLY SAVED TO DATABASE! ✓✓✓")
            else:
                print("\n✗ Signal not found in database")
    else:
        print(f"\n✗ Webhook failed with status {response.status_code}")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

print("\n" + "="*60)
print("TRADINGVIEW ALERT CONFIGURATION:")
print("="*60)
print(f"""
Your TradingView alert should be configured as:

Webhook URL: {webhook_url}

Alert Message: 
Just use the indicator's built-in alert message (it already sends the correct JSON format)

The indicator automatically sends:
- Signal creation events
- MFE updates
- Break-even triggers  
- Signal completion events

Make sure:
1. Alert is set to "Once Per Bar Close"
2. Alert is ACTIVE (not paused)
3. You're on a live/replay chart (not historical data)
""")

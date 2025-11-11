import requests
import json

print("=== CHECKING DATABASE DIRECTLY ===\n")

base_url = 'https://web-production-cd33.up.railway.app'

# Create a simple endpoint to query the database
print("1. Checking what's actually in the database...")

# Try to get recent signals (requires login)
print("\nNote: The /recent endpoint requires login, so we'll create a debug endpoint")

# Let's check the raw table data via a test query
test_query = """
SELECT 
    id, trade_id, event_type, direction, entry_price, 
    stop_loss, session, bias, timestamp
FROM automated_signals
ORDER BY id DESC
LIMIT 10
"""

print(f"\nQuery we need to run:")
print(test_query)

print("\n2. Testing if signals are actually being saved...")
print("Let's send another test signal and check the response carefully:")

webhook_url = f'{base_url}/api/automated-signals'

test_signal = {
    "type": "signal_created",
    "signal_id": "TEST_DEBUG_001",
    "date": "2024-11-11",
    "time": "11:30:00",
    "bias": "Bullish",
    "session": "NY AM",
    "entry_price": 21010.00,
    "sl_price": 20985.00,
    "risk_distance": 25.00,
    "be_price": 21010.00,
    "target_1r": 21035.00,
    "target_2r": 21060.00,
    "target_3r": 21085.00,
    "be_hit": False,
    "be_mfe": 0.00,
    "no_be_mfe": 0.00,
    "status": "active",
    "timestamp": 1731343800000
}

try:
    response = requests.post(webhook_url, json=test_signal, timeout=10)
    print(f"\nWebhook Response Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # The response shows signal_id which is the database ID
    if response.status_code == 200:
        result = response.json()
        db_id = result.get('signal_id')
        print(f"\n✓ Signal saved with database ID: {db_id}")
        print(f"  Trade ID: {result.get('trade_id')}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n3. The problem:")
print("-" * 60)
print("""
The webhook IS saving signals (we got database IDs back).
But the stats endpoint shows 0 signals.

This means the stats query is looking for the wrong thing.

Let me check the stats query...
""")

# Check what the stats endpoint is actually querying
print("\n4. Stats endpoint query issue:")
print("-" * 60)
print("""
Current stats query:
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN event_type = 'ENTRY' THEN 1 END) as entries,
        COUNT(CASE WHEN event_type LIKE 'EXIT_%' THEN 1 END) as exits
    FROM automated_signals

The problem: event_type is being saved as 'ENTRY' (uppercase)
but the query might be case-sensitive or the data is different.

Let me check what event_type values are actually in the database...
""")

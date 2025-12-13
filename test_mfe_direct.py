"""
Direct MFE_UPDATE Test
"""

import requests
from datetime import datetime

WEBHOOK_URL = "https://web-production-f8c3.up.railway.app/api/automated-signals/webhook"

# Use the trade_id from our successful test
trade_id = "20251213_140113000_BULLISH"

print("=" * 80)
print("DIRECT MFE_UPDATE TEST")
print("=" * 80)
print(f"Trade ID: {trade_id}")
print()

# Send MFE_UPDATE
mfe_payload = {
    "event_type": "MFE_UPDATE",
    "trade_id": trade_id,
    "direction": "LONG",
    "session": "NY AM",
    "entry_price": 25683.50,
    "stop_loss": 25645.00,
    "risk_distance": 38.50,
    "current_price": 25703.00,
    "be_mfe": 0.51,
    "no_be_mfe": 0.51,
    "mae_global_r": -0.05,
    "signal_age_seconds": 300,
    "event_timestamp": datetime.now().isoformat()
}

print("Sending MFE_UPDATE...")
print(f"   Current Price: $25703.00")
print(f"   BE MFE: 0.51R")
print(f"   No-BE MFE: 0.51R")
print()

response = requests.post(WEBHOOK_URL, json=mfe_payload, timeout=10)

print(f"Response Status: {response.status_code}")
print(f"Response Body: {response.text}")
print()

if response.status_code == 200:
    print("✅ MFE_UPDATE ACCEPTED!")
    print()
    print("Verifying in database...")
    
    import psycopg2
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    cur.execute("""
        SELECT COUNT(*) FROM automated_signals
        WHERE trade_id = %s AND event_type = 'MFE_UPDATE'
    """, (trade_id,))
    
    count = cur.fetchone()[0]
    print(f"✅ MFE_UPDATE events in database: {count}")
    
    # Get latest
    cur.execute("""
        SELECT be_mfe, no_be_mfe, current_price, timestamp
        FROM automated_signals
        WHERE trade_id = %s AND event_type = 'MFE_UPDATE'
        ORDER BY timestamp DESC
        LIMIT 1
    """, (trade_id,))
    
    row = cur.fetchone()
    if row:
        print(f"\nLatest MFE_UPDATE:")
        print(f"   BE MFE: {float(row[0]):.2f}R")
        print(f"   No-BE MFE: {float(row[1]):.2f}R")
        print(f"   Price: ${row[2]:.2f}")
        print(f"   Time: {row[3]}")
    
    cur.close()
    conn.close()
    
else:
    print("❌ MFE_UPDATE REJECTED")
    print()
    print("Checking why...")
    
    import psycopg2
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Check what events exist
    cur.execute("""
        SELECT event_type, timestamp
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    events = cur.fetchall()
    print(f"\nEvents in database for {trade_id}:")
    for event in events:
        print(f"   {event[0]} at {event[1]}")
    
    print(f"\nHas ENTRY: {'ENTRY' in [e[0] for e in events]}")
    
    cur.close()
    conn.close()

print()
print("=" * 80)

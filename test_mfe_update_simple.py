"""
Simple MFE_UPDATE Test
Send MFE_UPDATE for an existing ENTRY event
"""

import requests
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

WEBHOOK_URL = "https://web-production-f8c3.up.railway.app/api/automated-signals/webhook"

print("=" * 80)
print("MFE_UPDATE TEST")
print("=" * 80)
print()

# Step 1: Find an existing ENTRY event
print("STEP 1: Finding existing ENTRY event...")
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

cur.execute("""
    SELECT 
        e.trade_id,
        e.entry_price,
        e.stop_loss,
        e.direction,
        e.session
    FROM automated_signals e
    WHERE e.event_type = 'ENTRY'
    AND e.trade_id NOT IN (
        SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%'
    )
    ORDER BY e.timestamp DESC
    LIMIT 1
""")

row = cur.fetchone()

if not row:
    print("❌ No active ENTRY events found")
    cur.close()
    conn.close()
    exit(1)

trade_id = row[0]
entry_price = float(row[1])
stop_loss = float(row[2])
direction = row[3]
session = row[4]

print(f"✅ Found active trade:")
print(f"   Trade ID: {trade_id}")
print(f"   Entry: ${entry_price}")
print(f"   Stop: ${stop_loss}")
print(f"   Direction: {direction}")
print(f"   Session: {session}")

# Check if ENTRY really exists
cur.execute("""
    SELECT event_type FROM automated_signals
    WHERE trade_id = %s
    ORDER BY timestamp ASC
""", (trade_id,))

existing_events = [row[0] for row in cur.fetchall()]
print(f"\n   Existing events: {existing_events}")
print(f"   Has ENTRY: {'ENTRY' in existing_events}")

cur.close()
conn.close()

print()

# Step 2: Send MFE_UPDATE
print("STEP 2: Sending MFE_UPDATE...")
print("-" * 80)

risk_distance = abs(entry_price - stop_loss)
current_price = entry_price + (risk_distance * 0.5)  # +0.5R

if direction == "SHORT":
    current_price = entry_price - (risk_distance * 0.5)

mfe_update = {
    "event_type": "MFE_UPDATE",
    "trade_id": trade_id,
    "direction": direction,
    "session": session,
    "entry_price": entry_price,
    "stop_loss": stop_loss,
    "risk_distance": risk_distance,
    "current_price": current_price,
    "be_mfe": 0.50,
    "no_be_mfe": 0.50,
    "mae_global_r": -0.05,
    "signal_age_seconds": 300,
    "event_timestamp": datetime.now().isoformat()
}

print(f"Payload:")
print(f"   Trade ID: {trade_id}")
print(f"   Current Price: ${current_price:.2f}")
print(f"   BE MFE: 0.50R")
print(f"   No-BE MFE: 0.50R")
print()

try:
    response = requests.post(WEBHOOK_URL, json=mfe_update, timeout=10)
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ MFE_UPDATE accepted!")
        
        # Verify it was stored
        time.sleep(1)
        
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) FROM automated_signals
            WHERE trade_id = %s
            AND event_type = 'MFE_UPDATE'
        """, (trade_id,))
        
        mfe_count = cur.fetchone()[0]
        print(f"✅ MFE_UPDATE events for this trade: {mfe_count}")
        
        # Get latest MFE values
        cur.execute("""
            SELECT be_mfe, no_be_mfe, mae_global_r, current_price
            FROM automated_signals
            WHERE trade_id = %s
            AND event_type = 'MFE_UPDATE'
            ORDER BY timestamp DESC
            LIMIT 1
        """, (trade_id,))
        
        latest = cur.fetchone()
        if latest:
            print(f"\n   Latest MFE values:")
            print(f"      BE MFE: {float(latest[0]):.2f}R")
            print(f"      No-BE MFE: {float(latest[1]):.2f}R")
            print(f"      MAE: {float(latest[2]):.2f}R")
            print(f"      Current Price: ${latest[3]:.2f}")
        
        cur.close()
        conn.close()
        
    else:
        print(f"\n❌ MFE_UPDATE rejected")
        print(f"   This means lifecycle enforcement is blocking it")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)

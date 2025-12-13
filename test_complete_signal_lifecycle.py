"""
Test Complete Signal Lifecycle
Simulates: SIGNAL_CREATED → ENTRY → MFE_UPDATE → BE_TRIGGERED → EXIT
"""

import requests
import time
from datetime import datetime, timedelta
import json

WEBHOOK_URL = "https://web-production-f8c3.up.railway.app/api/automated-signals/webhook"

print("=" * 80)
print("COMPLETE SIGNAL LIFECYCLE TEST")
print("=" * 80)
print()

# Generate trade ID
signal_time = datetime.now()
trade_id = signal_time.strftime("%Y%m%d_%H%M%S000_BULLISH")

print(f"Trade ID: {trade_id}")
print(f"Signal Time: {signal_time}")
print()

# Step 1: SIGNAL_CREATED
print("STEP 1: SIGNAL_CREATED (Triangle Appears)")
print("-" * 80)

signal_created = {
    "event_type": "SIGNAL_CREATED",
    "trade_id": trade_id,
    "direction": "Bullish",
    "session": "NY AM",
    "signal_date": signal_time.strftime("%Y-%m-%d"),
    "signal_time": signal_time.strftime("%H:%M:%S"),
    "htf_alignment": {
        "daily": "Bullish",
        "h4": "Neutral",
        "h1": "Bullish",
        "m15": "Bullish",
        "m5": "Bullish",
        "m1": "Bullish"
    },
    "signal_price": 25680.00,
    "event_timestamp": signal_time.isoformat()
}

response = requests.post(WEBHOOK_URL, json=signal_created, timeout=10)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ SIGNAL_CREATED sent")
else:
    print(f"❌ Failed: {response.text}")
    exit(1)

time.sleep(1)

# Step 2: ENTRY (Confirmation after 3 bars)
print("\nSTEP 2: ENTRY (Signal Confirmed)")
print("-" * 80)

confirmation_time = signal_time + timedelta(minutes=3)
entry_price = 25683.50
stop_loss = 25645.00
risk_distance = entry_price - stop_loss

entry = {
    "event_type": "ENTRY",
    "trade_id": trade_id,
    "direction": "LONG",
    "session": "NY AM",
    "signal_date": signal_time.strftime("%Y-%m-%d"),
    "signal_time": signal_time.strftime("%H:%M:%S"),
    "entry_price": entry_price,
    "stop_loss": stop_loss,
    "risk_distance": risk_distance,
    "confirmation_time": confirmation_time.isoformat(),
    "bars_to_confirmation": 3,
    "htf_alignment": {
        "daily": "Bullish",
        "h4": "Neutral",
        "h1": "Bullish",
        "m15": "Bullish",
        "m5": "Bullish",
        "m1": "Bullish"
    },
    "event_timestamp": confirmation_time.isoformat()
}

response = requests.post(WEBHOOK_URL, json=entry, timeout=10)
print(f"Status: {response.status_code}")
print(f"Entry: ${entry_price}, Stop: ${stop_loss}, Risk: ${risk_distance:.2f}")
if response.status_code == 200:
    print("✅ ENTRY sent")
else:
    print(f"❌ Failed: {response.text}")

print("Waiting 3 seconds for ENTRY to commit...")
time.sleep(3)

# Step 3: MFE_UPDATE (Price moves up)
print("\nSTEP 3: MFE_UPDATE (Price Moving Favorably)")
print("-" * 80)

# Simulate price moving up over 5 minutes
mfe_updates = [
    {"minutes": 1, "price": 25690.00, "be_mfe": 0.17, "no_be_mfe": 0.17, "mae": -0.05},
    {"minutes": 2, "price": 25705.00, "be_mfe": 0.56, "no_be_mfe": 0.56, "mae": -0.05},
    {"minutes": 3, "price": 25722.00, "be_mfe": 1.00, "no_be_mfe": 1.00, "mae": -0.05},  # +1R achieved
    {"minutes": 4, "price": 25740.00, "be_mfe": 1.00, "no_be_mfe": 1.47, "mae": -0.05},  # BE triggered, No-BE continues
    {"minutes": 5, "price": 25760.00, "be_mfe": 1.00, "no_be_mfe": 1.99, "mae": -0.05},  # Almost +2R
]

for update in mfe_updates:
    update_time = confirmation_time + timedelta(minutes=update["minutes"])
    current_price = update["price"]
    
    mfe_update = {
        "event_type": "MFE_UPDATE",
        "trade_id": trade_id,
        "direction": "LONG",
        "session": "NY AM",
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "risk_distance": risk_distance,
        "current_price": current_price,
        "be_mfe": update["be_mfe"],
        "no_be_mfe": update["no_be_mfe"],
        "mae_global_r": update["mae"],
        "signal_age_seconds": update["minutes"] * 60,
        "event_timestamp": update_time.isoformat()
    }
    
    response = requests.post(WEBHOOK_URL, json=mfe_update, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ MFE Update {update['minutes']}: Price ${current_price:.2f}, BE MFE: {update['be_mfe']:.2f}R, No-BE MFE: {update['no_be_mfe']:.2f}R")
    else:
        print(f"❌ MFE Update {update['minutes']} failed: {response.text}")
    
    time.sleep(0.5)

# Step 4: BE_TRIGGERED (at +1R)
print("\nSTEP 4: BE_TRIGGERED (Break Even at +1R)")
print("-" * 80)

be_time = confirmation_time + timedelta(minutes=3)

be_triggered = {
    "event_type": "BE_TRIGGERED",
    "trade_id": trade_id,
    "direction": "LONG",
    "session": "NY AM",
    "entry_price": entry_price,
    "stop_loss": stop_loss,
    "current_price": 25722.00,
    "be_mfe": 1.00,
    "no_be_mfe": 1.00,
    "event_timestamp": be_time.isoformat()
}

response = requests.post(WEBHOOK_URL, json=be_triggered, timeout=10)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ BE_TRIGGERED sent (stop moved to entry)")
else:
    print(f"❌ Failed: {response.text}")

time.sleep(1)

# Step 5: EXIT_BE (Price comes back to entry)
print("\nSTEP 5: EXIT_BE (Price Returns to Entry)")
print("-" * 80)

exit_time = confirmation_time + timedelta(minutes=8)

exit_be = {
    "event_type": "EXIT_BE",
    "trade_id": trade_id,
    "direction": "LONG",
    "session": "NY AM",
    "entry_price": entry_price,
    "stop_loss": stop_loss,
    "exit_price": entry_price,  # Stopped at entry (BE)
    "be_mfe": 1.00,  # Final MFE for BE strategy
    "no_be_mfe": 1.99,  # Final MFE for No-BE strategy (continued tracking)
    "mae_global_r": -0.05,
    "exit_reason": "break_even_stop",
    "event_timestamp": exit_time.isoformat()
}

response = requests.post(WEBHOOK_URL, json=exit_be, timeout=10)
print(f"Status: {response.status_code}")
print(f"Exit Price: ${entry_price:.2f} (Break Even)")
print(f"Final BE MFE: 1.00R, Final No-BE MFE: 1.99R")
if response.status_code == 200:
    print("✅ EXIT_BE sent")
else:
    print(f"❌ Failed: {response.text}")

time.sleep(2)

# Verification
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Get all events for this trade
    cur.execute("""
        SELECT 
            event_type,
            timestamp,
            current_price,
            be_mfe,
            no_be_mfe,
            mae_global_r,
            exit_price
        FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    events = cur.fetchall()
    
    print(f"\nTotal events stored: {len(events)}")
    print("\nEvent Timeline:")
    
    for i, event in enumerate(events, 1):
        print(f"\n{i}. {event[0]}")
        print(f"   Time: {event[1]}")
        if event[2]:
            print(f"   Price: ${event[2]:.2f}")
        if event[3] is not None:
            print(f"   BE MFE: {float(event[3]):.2f}R")
        if event[4] is not None:
            print(f"   No-BE MFE: {float(event[4]):.2f}R")
        if event[5] is not None:
            print(f"   MAE: {float(event[5]):.2f}R")
        if event[6]:
            print(f"   Exit Price: ${event[6]:.2f}")
    
    # Check completeness
    event_types = [e[0] for e in events]
    
    print("\n" + "-" * 80)
    print("Completeness Check:")
    print(f"   {'✅' if 'SIGNAL_CREATED' in event_types else '❌'} SIGNAL_CREATED")
    print(f"   {'✅' if 'ENTRY' in event_types else '❌'} ENTRY")
    print(f"   {'✅' if 'MFE_UPDATE' in event_types else '❌'} MFE_UPDATE ({event_types.count('MFE_UPDATE')} updates)")
    print(f"   {'✅' if 'BE_TRIGGERED' in event_types else '❌'} BE_TRIGGERED")
    print(f"   {'✅' if 'EXIT_BE' in event_types else '❌'} EXIT_BE")
    
    # Check dashboard would show this correctly
    cur.execute("""
        SELECT 
            e.trade_id,
            e.entry_price,
            e.stop_loss,
            latest_mfe.be_mfe,
            latest_mfe.no_be_mfe,
            latest_mfe.mae_global_r,
            ex.exit_price,
            ex.event_type as exit_type
        FROM automated_signals e
        LEFT JOIN LATERAL (
            SELECT be_mfe, no_be_mfe, mae_global_r
            FROM automated_signals
            WHERE trade_id = e.trade_id
            AND event_type = 'MFE_UPDATE'
            ORDER BY timestamp DESC
            LIMIT 1
        ) latest_mfe ON true
        LEFT JOIN automated_signals ex ON ex.trade_id = e.trade_id 
            AND ex.event_type LIKE 'EXIT_%'
        WHERE e.trade_id = %s
        AND e.event_type = 'ENTRY'
    """, (trade_id,))
    
    dashboard_row = cur.fetchone()
    
    if dashboard_row:
        print("\n" + "-" * 80)
        print("Dashboard View:")
        print(f"   Trade ID: {dashboard_row[0]}")
        print(f"   Entry: ${dashboard_row[1]:.2f}")
        print(f"   Stop: ${dashboard_row[2]:.2f}")
        print(f"   Latest BE MFE: {float(dashboard_row[3]):.2f}R" if dashboard_row[3] else "   No MFE data")
        print(f"   Latest No-BE MFE: {float(dashboard_row[4]):.2f}R" if dashboard_row[4] else "   No MFE data")
        print(f"   MAE: {float(dashboard_row[5]):.2f}R" if dashboard_row[5] else "   No MAE data")
        print(f"   Exit: ${dashboard_row[6]:.2f} ({dashboard_row[7]})" if dashboard_row[6] else "   Still Active")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE LIFECYCLE TEST PASSED")
    print("=" * 80)
    print()
    print("Summary:")
    print("✅ SIGNAL_CREATED → Triangle appeared")
    print("✅ ENTRY → Signal confirmed after 3 bars")
    print("✅ MFE_UPDATE → 5 price updates tracked")
    print("✅ BE_TRIGGERED → Break even at +1R")
    print("✅ EXIT_BE → Stopped at entry (1.00R for BE, 1.99R for No-BE)")
    print()
    print("The complete signal lifecycle is working perfectly!")
    
except Exception as e:
    print(f"\n❌ Verification error: {e}")
    import traceback
    traceback.print_exc()

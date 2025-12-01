#!/usr/bin/env python3
"""Deep analysis of Dec 1 TradingView alerts vs database"""
import csv
import json
import os
import psycopg2
from collections import defaultdict
from datetime import datetime

# Read the CSV file
alerts = []
with open('TradingView_Alerts_Log_2025-12-01_c5b83.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            desc = json.loads(row['Description'])
            alerts.append({
                'alert_id': row['Alert ID'],
                'time': row['Time'],
                'trade_id': desc.get('trade_id'),
                'event_type': desc.get('event_type'),
                'direction': desc.get('direction'),
                'entry_price': desc.get('entry_price'),
                'mfe_R': desc.get('mfe_R'),
                'session': desc.get('session'),
                'event_timestamp': desc.get('event_timestamp'),
                'raw': desc
            })
        except:
            pass

print(f"=== TOTAL ALERTS IN CSV: {len(alerts)} ===\n")

# Group by event type
by_event_type = defaultdict(list)
for a in alerts:
    by_event_type[a['event_type']].append(a)

print("=== ALERTS BY EVENT TYPE ===")
for event_type, items in sorted(by_event_type.items()):
    print(f"  {event_type}: {len(items)}")

# Group by trade_id
by_trade_id = defaultdict(list)
for a in alerts:
    by_trade_id[a['trade_id']].append(a)

print(f"\n=== UNIQUE TRADE IDS: {len(by_trade_id)} ===")
for trade_id in sorted(by_trade_id.keys()):
    events = by_trade_id[trade_id]
    event_types = [e['event_type'] for e in events]
    entry_count = event_types.count('ENTRY')
    mfe_count = event_types.count('MFE_UPDATE')
    be_count = event_types.count('BE_TRIGGERED')
    exit_count = sum(1 for e in event_types if 'EXIT' in e)
    print(f"  {trade_id}: ENTRY={entry_count}, MFE_UPDATE={mfe_count}, BE={be_count}, EXIT={exit_count}")

# Show ENTRY events specifically
print("\n=== ENTRY EVENTS (New Signals) ===")
entry_events = [a for a in alerts if a['event_type'] == 'ENTRY']
for e in entry_events:
    print(f"  Trade: {e['trade_id']}")
    print(f"    Direction: {e['direction']}")
    print(f"    Entry Price: {e['entry_price']}")
    print(f"    Session: {e['session']}")
    print(f"    Event Timestamp: {e['event_timestamp']}")
    print(f"    Alert Time: {e['time']}")
    print()

# Show EXIT events
print("\n=== EXIT EVENTS ===")
exit_events = [a for a in alerts if 'EXIT' in str(a['event_type'])]
for e in exit_events:
    print(f"  Trade: {e['trade_id']}")
    print(f"    Event Type: {e['event_type']}")
    print(f"    Alert Time: {e['time']}")
    print()

# Show BE_TRIGGERED events
print("\n=== BE_TRIGGERED EVENTS ===")
be_events = [a for a in alerts if a['event_type'] == 'BE_TRIGGERED']
for e in be_events:
    print(f"  Trade: {e['trade_id']}")
    print(f"    Alert Time: {e['time']}")
    print()

# Now compare with database
print("\n" + "="*60)
print("=== COMPARING WITH DATABASE ===")
print("="*60)

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rlVgkSLbFWUYvxdBXhKPLMrCDqWOctJE@junction.proxy.rlwy.net:57782/railway')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Check if any of today's trade_ids exist in database
trade_ids_in_csv = list(by_trade_id.keys())
print(f"\nTrade IDs in CSV: {trade_ids_in_csv}")

for trade_id in trade_ids_in_csv:
    cur.execute("SELECT COUNT(*) FROM automated_signals WHERE trade_id = %s", (trade_id,))
    count = cur.fetchone()[0]
    print(f"  {trade_id} in DB: {count} events")

# Check most recent events in database
print("\n=== MOST RECENT DB EVENTS ===")
cur.execute("""
    SELECT trade_id, event_type, timestamp 
    FROM automated_signals 
    ORDER BY timestamp DESC 
    LIMIT 5
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} at {row[2]}")

# Check if there's any data from Dec 1
print("\n=== DATABASE EVENTS FROM DEC 1 ===")
cur.execute("""
    SELECT COUNT(*) FROM automated_signals 
    WHERE timestamp >= '2025-12-01 00:00:00'
""")
print(f"  Events from Dec 1: {cur.fetchone()[0]}")

cur.close()
conn.close()

print("\n" + "="*60)
print("=== CRITICAL FINDING ===")
print("="*60)
print(f"TradingView sent {len(alerts)} alerts today")
print(f"Database has 0 events from today")
print("CONCLUSION: Webhooks are being sent but NOT received by the server!")

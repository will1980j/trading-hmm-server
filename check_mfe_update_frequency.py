"""Check how frequently MFE updates are being received"""
import os
import psycopg2
from datetime import datetime, timedelta

database_url = os.environ.get('DATABASE_URL')
conn = psycopg2.connect(database_url)
cursor = conn.cursor()

# Get recent MFE updates for active trades
cursor.execute("""
SELECT 
    trade_id,
    event_type,
    be_mfe,
    no_be_mfe,
    timestamp
FROM automated_signals
WHERE event_type = 'MFE_UPDATE'
AND timestamp > NOW() - INTERVAL '30 minutes'
ORDER BY trade_id, timestamp DESC
""")

rows = cursor.fetchall()

print(f"\n📊 MFE Updates in last 30 minutes: {len(rows)}\n")

# Group by trade_id
from collections import defaultdict
updates_by_trade = defaultdict(list)

for row in rows:
    trade_id, event_type, be_mfe, no_be_mfe, ts = row
    updates_by_trade[trade_id].append({
        'be_mfe': be_mfe,
        'no_be_mfe': no_be_mfe,
        'timestamp': ts
    })

# Analyze each trade
for trade_id, updates in updates_by_trade.items():
    print(f"\n🔍 Trade: {trade_id}")
    print(f"   Total updates: {len(updates)}")
    
    if len(updates) > 1:
        # Calculate time gaps between updates
        sorted_updates = sorted(updates, key=lambda x: x['timestamp'])
        gaps = []
        for i in range(1, len(sorted_updates)):
            gap = (sorted_updates[i]['timestamp'] - sorted_updates[i-1]['timestamp']).total_seconds()
            gaps.append(gap)
        
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        print(f"   Average gap: {avg_gap:.1f} seconds")
        print(f"   Expected: ~60 seconds (1 minute)")
        
        if avg_gap > 120:
            print(f"   ⚠️ PROBLEM: Updates are too infrequent!")
        elif avg_gap < 30:
            print(f"   ⚠️ PROBLEM: Updates are too frequent!")
        else:
            print(f"   ✅ Update frequency looks good")
        
        # Show last 5 updates
        print(f"\n   Last 5 updates:")
        for update in sorted_updates[-5:]:
            print(f"      {update['timestamp']} - BE:{update['be_mfe']:.4f} NoB E:{update['no_be_mfe']:.4f}")
    else:
        print(f"   ⚠️ Only 1 update received - need more data")

# Check if there are any active signals that should be sending updates
cursor.execute("""
SELECT DISTINCT trade_id
FROM automated_signals
WHERE event_type = 'SIGNAL_CREATED'
AND trade_id NOT IN (
    SELECT DISTINCT trade_id 
    FROM automated_signals 
    WHERE event_type = 'EXIT_SL'
)
AND timestamp > NOW() - INTERVAL '2 hours'
""")

active_signals = cursor.fetchall()
print(f"\n\n📈 Active signals (should be sending MFE updates): {len(active_signals)}")
for signal in active_signals:
    trade_id = signal[0]
    
    # Check when last MFE update was received
    cursor.execute("""
    SELECT timestamp
    FROM automated_signals
    WHERE trade_id = %s
    AND event_type = 'MFE_UPDATE'
    ORDER BY timestamp DESC
    LIMIT 1
    """, (trade_id,))
    
    last_update = cursor.fetchone()
    if last_update:
        minutes_ago = (datetime.now() - last_update[0].replace(tzinfo=None)).total_seconds() / 60
        print(f"   {trade_id}: Last update {minutes_ago:.1f} minutes ago")
        if minutes_ago > 2:
            print(f"      ⚠️ No update in {minutes_ago:.1f} minutes - indicator may not be running!")
    else:
        print(f"   {trade_id}: NO MFE UPDATES RECEIVED!")
        print(f"      ❌ Signal created but no MFE updates - webhook not working!")

conn.close()

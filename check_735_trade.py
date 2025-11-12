import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Find the 7:35 trade
cur.execute("""
    SELECT trade_id, event_type, be_mfe, no_be_mfe, mfe, signal_time, timestamp
    FROM automated_signals
    WHERE signal_time = '07:35:00'
    ORDER BY timestamp ASC
""")

rows = cur.fetchall()

print("=" * 120)
print("ALL EVENTS FOR 07:35 TRADE")
print("=" * 120)
print(f"{'Event Type':<20} {'BE MFE':<10} {'No BE MFE':<12} {'Legacy MFE':<12} {'Timestamp':<30}")
print("=" * 120)

for row in rows:
    trade_id, event_type, be_mfe, no_be_mfe, mfe, signal_time, timestamp = row
    be_val = be_mfe if be_mfe is not None else '-'
    no_be_val = no_be_mfe if no_be_mfe is not None else '-'
    mfe_val = mfe if mfe is not None else '-'
    print(f"{event_type:<20} {str(be_val):<10} {str(no_be_val):<12} {str(mfe_val):<12} {str(timestamp):<30}")

print("\n" + "=" * 120)
print("ANALYSIS:")
print("=" * 120)

if rows:
    # Check latest MFE_UPDATE
    mfe_updates = [r for r in rows if r[1] == 'MFE_UPDATE']
    if mfe_updates:
        latest_mfe = mfe_updates[-1]
        print(f"Latest MFE_UPDATE: BE={latest_mfe[2]}, No BE={latest_mfe[3]}")
        print(f"Dashboard should show: {latest_mfe[2]}, {latest_mfe[3]}")
    else:
        print("No MFE_UPDATE events found")
else:
    print("No events found for 07:35 trade")

cur.close()
conn.close()

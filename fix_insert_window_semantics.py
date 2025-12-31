#!/usr/bin/env python3
"""Fix insert window to use OPEN time semantics"""

with open('scripts/phase_c_backfill_triangles.py', 'r') as f:
    content = f.read()

# Find and replace the insert window computation section
old_section = '''if 'T' in start_date:
    insert_start_ts = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
else:
    insert_start_ts = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)

if 'T' in end_date:
    insert_end_ts = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
else:
    insert_end_ts = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=utc_tz)'''

new_section = '''# Compute insert window in OPEN time
if 'T' in start_date:
    insert_open_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
else:
    insert_open_start = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)

if 'T' in end_date:
    insert_open_end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
else:
    insert_open_end = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=utc_tz)

# Compute fetch window (need CLOSE bars to generate OPEN timestamps)
insert_close_end = insert_open_end + BAR_INTERVAL'''

content = content.replace(old_section, new_section)

# Fix PURGE to use OPEN time window
content = content.replace(
    'WHERE symbol = %s AND ts >= %s AND ts <= %s\n    """, (symbol, insert_start_ts, insert_end_ts))',
    'WHERE symbol = %s AND ts >= %s AND ts <= %s\n    """, (symbol, insert_open_start, insert_open_end))'
)

# Fix fetch query to use close_end
content = content.replace(
    'WHERE symbol = %s AND ts >= %s AND ts <= %s\n    ORDER BY ts ASC\n""", (symbol, preload_start_ts, insert_end_ts))',
    'WHERE symbol = %s AND ts >= %s AND ts <= %s\n    ORDER BY ts ASC\n""", (symbol, preload_start_ts, insert_close_end))'
)

# Fix eligibility check to use OPEN time
content = content.replace(
    '''        # Check if this bar is within insert range
        bar_ts = bar_tuple[0]
        if bar_ts >= insert_start_ts and bar_ts <= insert_end_ts:''',
    '''        # Check if this bar's OPEN time is within insert range
        bar_close_ts = bar_tuple[0]
        bar_open_ts_check = bar_close_ts - BAR_INTERVAL
        if bar_open_ts_check >= insert_open_start and bar_open_ts_check <= insert_open_end:'''
)

with open('scripts/phase_c_backfill_triangles.py', 'w') as f:
    f.write(content)

print('Fixed insert window to use OPEN time semantics')
print('  - Insert window defined in OPEN time')
print('  - Fetch window extended by 1 minute for CLOSE bars')
print('  - Eligibility check uses bar OPEN time')
print('  - PURGE uses OPEN time window')

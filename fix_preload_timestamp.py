#!/usr/bin/env python3
with open('scripts/phase_c_backfill_triangles.py', 'r') as f:
    content = f.read()

content = content.replace('WARMUP [PRELOAD_START_DATE]', 'WARMUP [PRELOAD_START_TS]')
content = content.replace('2025-12-02 5 2025-11-30', '2025-12-02 5 2025-11-30T23:00:00Z')
content = content.replace(
    'preload_start_date = sys.argv[5] if len(sys.argv) > 5 else "2025-11-30"',
    'preload_start_ts_arg = sys.argv[5] if len(sys.argv) > 5 else "2025-11-30T23:00:00Z"'
)

# Fix parsing
old = '''# Parse preload start date
if "T" in preload_start_date:
    preload_start_ts = datetime.fromisoformat(preload_start_date.replace("Z", "+00:00"))
else:
    preload_start_ts = datetime.fromisoformat(preload_start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)'''

new = '''# Parse preload start timestamp
preload_start_ts = datetime.fromisoformat(preload_start_ts_arg.replace("Z", "+00:00"))'''

content = content.replace(old, new)
content = content.replace('from {preload_start_date}', 'from {preload_start_ts_arg}')

with open('scripts/phase_c_backfill_triangles.py', 'w') as f:
    f.write(content)

print('Fixed preload to accept full timestamp')

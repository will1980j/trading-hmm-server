#!/usr/bin/env python3
"""Fix timestamp semantics: use bar OPEN time, not CLOSE"""

with open('scripts/phase_c_backfill_triangles.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and replace key sections
new_lines = []
for i, line in enumerate(lines):
    # Change preload_days to preload_start_date in usage
    if 'WARMUP [PRELOAD_DAYS]' in line:
        line = line.replace('[PRELOAD_DAYS]', '[PRELOAD_START_DATE]')
    elif 'GLBX.MDP3:NQ 2025-12-02 2025-12-02 5 10' in line:
        line = line.replace('5 10', '5 2025-11-30')
    
    # Change preload_days variable to preload_start_date
    elif line.strip().startswith('preload_days = int(sys.argv[5])'):
        line = 'preload_start_date = sys.argv[5] if len(sys.argv) > 5 else "2025-11-30"\n'
    
    # Change preload computation
    elif 'preload_start_ts = insert_start_ts - timedelta(days=preload_days)' in line:
        new_lines.append('# Parse preload start date\n')
        new_lines.append('if "T" in preload_start_date:\n')
        new_lines.append('    preload_start_ts = datetime.fromisoformat(preload_start_date.replace("Z", "+00:00"))\n')
        new_lines.append('else:\n')
        new_lines.append('    preload_start_ts = datetime.fromisoformat(preload_start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)\n')
        continue
    
    # Update print statements
    elif 'Preload: {preload_days} days before insert range' in line:
        line = line.replace('{preload_days} days before insert range', 'from {preload_start_date}')
    elif 'Warmup: {warmup} bars' in line and 'preload' in line:
        line = line.replace('preload: {preload_days} days', 'preload from {preload_start_date}')
    
    # Add BAR_INTERVAL constant after imports
    elif 'from market_parity.signal_generation import generate_signals' in line:
        new_lines.append(line)
        new_lines.append('\n# Bar interval for timestamp conversion\n')
        new_lines.append('BAR_INTERVAL = timedelta(minutes=1)\n')
        continue
    
    # Change confirmation_ts calculation
    elif 'confirmation_ts = bar_tuple[0] + timedelta(minutes=1)' in line:
        line = '            # Databento ts is bar CLOSE; compute bar OPEN for TradingView alignment\n'
        new_lines.append(line)
        new_lines.append('            bar_close_ts = bar_tuple[0]\n')
        new_lines.append('            bar_open_ts = bar_close_ts - BAR_INTERVAL\n')
        new_lines.append('            \n')
        continue
    
    # Change triangle timestamp to bar_open_ts
    elif 'symbol, confirmation_ts,' in line:
        line = line.replace('confirmation_ts', 'bar_open_ts')
    
    new_lines.append(line)

with open('scripts/phase_c_backfill_triangles.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed timestamp semantics:")
print("  - Databento ts treated as bar CLOSE")
print("  - Triangle ts = bar OPEN (close - 1 minute)")
print("  - PRELOAD_DAYS changed to PRELOAD_START_DATE")

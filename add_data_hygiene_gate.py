#!/usr/bin/env python3
"""Add data hygiene gate to backfill script"""

with open('scripts/phase_c_backfill_triangles.py', 'r') as f:
    lines = f.readlines()

# Find the line where we initialize counters
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    
    # Add bad_skipped counter after processed_count initialization
    if 'processed_count = 0' in line:
        new_lines.append('bad_skipped = 0\n')
        new_lines.append('prev_good_close = None\n')
    
    # Add hygiene check right after bar_dict creation
    if "bar_dict = {" in line and i > 100:  # Make sure we're in the main loop
        # Find the closing brace of bar_dict
        j = i
        while j < len(lines) and '}' not in lines[j]:
            new_lines.append(lines[j+1])
            j += 1
        
        # Add hygiene check after bar_dict
        new_lines.append('\n')
        new_lines.append('    # Data hygiene gate\n')
        new_lines.append('    o, h, l, c = bar_dict["open"], bar_dict["high"], bar_dict["low"], bar_dict["close"]\n')
        new_lines.append('    is_bad = False\n')
        new_lines.append('    \n')
        new_lines.append('    # Check 1: OHLC integrity\n')
        new_lines.append('    if h < max(o, c) or l > min(o, c) or h < l:\n')
        new_lines.append('        is_bad = True\n')
        new_lines.append('    \n')
        new_lines.append('    # Check 2: Price discontinuity (>200 points)\n')
        new_lines.append('    if prev_good_close is not None and abs(c - prev_good_close) > 200:\n')
        new_lines.append('        is_bad = True\n')
        new_lines.append('    \n')
        new_lines.append('    # Check 3: Flat bar with discontinuity\n')
        new_lines.append('    if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:\n')
        new_lines.append('        is_bad = True\n')
        new_lines.append('    \n')
        new_lines.append('    if is_bad:\n')
        new_lines.append('        bad_skipped += 1\n')
        new_lines.append('        processed_count += 1\n')
        new_lines.append('        continue\n')
        new_lines.append('    \n')
        break

# Continue with rest of file
new_lines.extend(lines[j+1:])

# Add bad_skipped to final output
final_lines = []
for line in new_lines:
    if 'print(f"Generated {len(triangle_events)} triangle events")' in line:
        final_lines.append(line)
        final_lines.append('print(f"Bad bars skipped: {bad_skipped}")\n')
    else:
        final_lines.append(line)

# Add prev_good_close update at end of loop
final_lines2 = []
for line in final_lines:
    final_lines2.append(line)
    if '# Update for next iteration' in line:
        final_lines2.append('    prev_good_close = bar_dict["close"]\n')

with open('scripts/phase_c_backfill_triangles.py', 'w') as f:
    f.writelines(final_lines2)

print('Added data hygiene gate')
print('  - OHLC integrity check')
print('  - Price discontinuity check (>200 points)')
print('  - Flat bar discontinuity check (>50 points)')

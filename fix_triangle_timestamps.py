#!/usr/bin/env python3
"""Fix triangle timestamps to use confirmation bar"""

with open('scripts/phase_c_backfill_triangles.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Ensure timedelta is imported
if 'from datetime import datetime, timedelta' not in content:
    content = content.replace('from datetime import datetime', 'from datetime import datetime, timedelta')

# Find and replace the triangle collection section
old_section = """            # Collect triangle events
            if signals['show_bull_triangle']:
                triangle_events.append((
                    symbol, bar_tuple[0], 'BULL',"""

new_section = """            # Collect triangle events (use confirmation bar timestamp)
            confirmation_ts = bar_tuple[0] + timedelta(minutes=1)
            
            if signals['show_bull_triangle']:
                triangle_events.append((
                    symbol, confirmation_ts, 'BULL',"""

content = content.replace(old_section, new_section)

# Fix BEAR triangle timestamp
content = content.replace(
    "symbol, bar_tuple[0], 'BEAR',",
    "symbol, confirmation_ts, 'BEAR',"
)

with open('scripts/phase_c_backfill_triangles.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed triangle timestamps to use confirmation bar (current + 1 minute)")

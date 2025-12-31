#!/usr/bin/env python3
with open('scripts/phase_c_backfill_triangles.py', 'r') as f:
    content = f.read()

# Remove all checks after Check 3
old = '''    # Check 4: Regime thousands mismatch
    if prev_good_close is not None:
        regime_base = int(prev_good_close // 1000)
        if int(c // 1000) != regime_base:
            is_bad = True
    
    # Check 5: Near-flat with discontinuity
    if (h - l) <= 1.0 and prev_good_close is not None and abs(c - prev_good_close) > 50:
        is_bad = True
    
    # Check 6: Small range with discontinuity
    if prev_good_close is not None and (h - l) <= 10.0 and abs(c - prev_good_close) > 50:
        is_bad = True
    
    # Check 7: Flat bar with discontinuity
    if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:
        is_bad = True'''

content = content.replace(old, '')

# Remove extra reasons
old_reasons = '''        if prev_good_close is not None:
            regime_base = int(prev_good_close // 1000)
            if int(c // 1000) != regime_base:
                reasons.append('REGIME_THOUSANDS_MISMATCH')
        if (h - l) <= 1.0 and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('NEAR_FLAT_DISCONTINUITY_50')
        if prev_good_close is not None and (h - l) <= 10.0 and abs(c - prev_good_close) > 50:
            reasons.append('SMALL_RANGE_DISCONTINUITY_50')
        if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('FLAT_DISCONTINUITY_50')'''

content = content.replace(old_reasons, '')

with open('scripts/phase_c_backfill_triangles.py', 'w') as f:
    f.write(content)

print('Simplified to 3 proven rules only')

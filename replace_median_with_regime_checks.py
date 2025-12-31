#!/usr/bin/env python3
with open('scripts/phase_c_backfill_triangles.py', 'r') as f:
    content = f.read()

# Remove statistics import
content = content.replace('import os, sys, psycopg2, statistics', 'import os, sys, psycopg2')

# Remove last_closes initialization
content = content.replace('\nlast_closes = []', '')

# Remove median check from hygiene gate
old_median_check = '''    # Check 4: Median dislocation (regime safety)
    if len(last_closes) >= 10:
        median_close = statistics.median(last_closes)
        if abs(c - median_close) > 200:
            is_bad = True'''

content = content.replace(old_median_check, '')

# Remove median from reasons
old_median_reason = '''        if len(last_closes) >= 10:
            median_close = statistics.median(last_closes)
            if abs(c - median_close) > 200:
                reasons.append('MEDIAN_DISLOCATION_200')'''

content = content.replace(old_median_reason, '')

# Remove last_closes update
content = content.replace(
    '''    prev_good_close = c
    last_closes.append(c)
    if len(last_closes) > 20:
        last_closes.pop(0)''',
    '    prev_good_close = c'
)

# Add new regime checks after DISCONTINUITY_500
old_checks = '''    # Check 2: Price discontinuity (>500 points)
    if prev_good_close is not None and abs(c - prev_good_close) > 500:
        is_bad = True
    
    # Check 3: Flat bar with discontinuity'''

new_checks = '''    # Check 2: Price < 1000 (hard reject)
    if o < 1000 or h < 1000 or l < 1000 or c < 1000:
        is_bad = True
    
    # Check 3: Price discontinuity (>500 points)
    if prev_good_close is not None and abs(c - prev_good_close) > 500:
        is_bad = True
    
    # Check 4: Regime thousands mismatch
    if prev_good_close is not None:
        regime_base = int(prev_good_close // 1000)
        if int(c // 1000) != regime_base:
            is_bad = True
    
    # Check 5: Near-flat with discontinuity
    if (h - l) <= 1.0 and prev_good_close is not None and abs(c - prev_good_close) > 50:
        is_bad = True
    
    # Check 6: Flat bar with discontinuity'''

content = content.replace(old_checks, new_checks)

# Add new reasons
old_reasons = '''        if prev_good_close is not None and abs(c - prev_good_close) > 500:
            reasons.append('DISCONTINUITY_500')
        if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('FLAT_DISCONTINUITY_50')'''

new_reasons = '''        if o < 1000 or h < 1000 or l < 1000 or c < 1000:
            reasons.append('PRICE_LT_1000')
        if prev_good_close is not None and abs(c - prev_good_close) > 500:
            reasons.append('DISCONTINUITY_500')
        if prev_good_close is not None:
            regime_base = int(prev_good_close // 1000)
            if int(c // 1000) != regime_base:
                reasons.append('REGIME_THOUSANDS_MISMATCH')
        if (h - l) <= 1.0 and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('NEAR_FLAT_DISCONTINUITY_50')
        if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('FLAT_DISCONTINUITY_50')'''

content = content.replace(old_reasons, new_reasons)

with open('scripts/phase_c_backfill_triangles.py', 'w') as f:
    f.write(content)

print('Replaced median filter with regime checks')
print('  - PRICE_LT_1000')
print('  - REGIME_THOUSANDS_MISMATCH')
print('  - NEAR_FLAT_DISCONTINUITY_50')

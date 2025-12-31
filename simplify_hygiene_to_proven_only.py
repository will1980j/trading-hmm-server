#!/usr/bin/env python3
with open('scripts/phase_c_backfill_triangles.py', 'r') as f:
    content = f.read()

# Replace all hygiene checks with simplified version
old_checks = '''    # Data hygiene gate
    o, h, l, c = bar_dict['open'], bar_dict['high'], bar_dict['low'], bar_dict['close']
    is_bad = False
    
    # Check 1: OHLC integrity
    if h < max(o, c) or l > min(o, c) or h < l:
        is_bad = True
    
    # Check 2: Price < 1000 (hard reject)
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
    
    # Check 6: Small range with discontinuity
    if prev_good_close is not None and (h - l) <= 10.0 and abs(c - prev_good_close) > 50:
        is_bad = True
    
    # Check 7: Flat bar with discontinuity
    if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:
        is_bad = True'''

new_checks = '''    # Data hygiene gate (proven corruption only)
    o, h, l, c = bar_dict['open'], bar_dict['high'], bar_dict['low'], bar_dict['close']
    is_bad = False
    
    # Check 1: OHLC integrity
    if h < max(o, c) or l > min(o, c) or h < l:
        is_bad = True
    
    # Check 2: Price < 1000 (catches 253.xx corruption)
    if o < 1000 or h < 1000 or l < 1000 or c < 1000:
        is_bad = True
    
    # Check 3: Price discontinuity (>500 points)
    if prev_good_close is not None and abs(c - prev_good_close) > 500:
        is_bad = True'''

content = content.replace(old_checks, new_checks)

# Simplify reasons
old_reasons = '''        if h < max(o, c) or l > min(o, c) or h < l:
            reasons.append('OHLC_INTEGRITY')
        if o < 1000 or h < 1000 or l < 1000 or c < 1000:
            reasons.append('PRICE_LT_1000')
        if prev_good_close is not None and abs(c - prev_good_close) > 500:
            reasons.append('DISCONTINUITY_500')
        if prev_good_close is not None:
            regime_base = int(prev_good_close // 1000)
            if int(c // 1000) != regime_base:
                reasons.append('REGIME_THOUSANDS_MISMATCH')
        if (h - l) <= 1.0 and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('NEAR_FLAT_DISCONTINUITY_50')
        if prev_good_close is not None and (h - l) <= 10.0 and abs(c - prev_good_close) > 50:
            reasons.append('SMALL_RANGE_DISCONTINUITY_50')
        if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('FLAT_DISCONTINUITY_50')'''

new_reasons = '''        if h < max(o, c) or l > min(o, c) or h < l:
            reasons.append('OHLC_INTEGRITY')
        if o < 1000 or h < 1000 or l < 1000 or c < 1000:
            reasons.append('PRICE_LT_1000')
        if prev_good_close is not None and abs(c - prev_good_close) > 500:
            reasons.append('DISCONTINUITY_500')'''

content = content.replace(old_reasons, new_reasons)

with open('scripts/phase_c_backfill_triangles.py', 'w') as f:
    f.write(content)

print('Simplified hygiene to proven corruption only')
print('  - OHLC_INTEGRITY')
print('  - PRICE_LT_1000')
print('  - DISCONTINUITY_500')

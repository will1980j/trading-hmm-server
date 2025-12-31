#!/usr/bin/env python3
with open('scripts/phase_c_backfill_triangles.py', 'r') as f:
    content = f.read()

content = content.replace(
    'bad_skipped = 0',
    'bad_skipped = 0\nskipped_bars = []'
)

old_skip = '''    if is_bad:
        bad_skipped += 1
        processed_count += 1
        continue'''

new_skip = '''    if is_bad:
        bad_skipped += 1
        reasons = []
        if h < max(o, c) or l > min(o, c) or h < l:
            reasons.append('OHLC_INTEGRITY')
        if prev_good_close is not None and abs(c - prev_good_close) > 200:
            reasons.append('DISCONTINUITY_200')
        if o == h == l == c and prev_good_close is not None and abs(c - prev_good_close) > 50:
            reasons.append('FLAT_DISCONTINUITY_50')
        
        bar_close_ts = bar_tuple[0]
        bar_open_ts = bar_close_ts - BAR_INTERVAL
        skipped_bars.append({
            'ts_close': bar_close_ts.isoformat(),
            'ts_open': bar_open_ts.isoformat(),
            'open': o,
            'high': h,
            'low': l,
            'close': c,
            'prev_good_close': prev_good_close,
            'reasons': reasons
        })
        processed_count += 1
        continue'''

content = content.replace(old_skip, new_skip)

old_print = '''print(f"Processed {processed_count} bars")
print(f"Bad bars skipped: {bad_skipped}")'''

new_print = '''print(f"Processed {processed_count} bars")
print(f"Bad bars skipped: {bad_skipped}")

if skipped_bars:
    print("\\nFirst 30 skipped bars:")
    hdr = f"{'TS_OPEN':<20} {'TS_CLOSE':<20} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8} {'PrevClose':>10} Reasons"
    print(hdr)
    print("-" * 120)
    for bar in skipped_bars[:30]:
        reasons_str = ','.join(bar['reasons'])
        prev_str = f"{bar['prev_good_close']:.2f}" if bar['prev_good_close'] is not None else 'None'
        print(f"{bar['ts_open']:<20} {bar['ts_close']:<20} {bar['open']:>8.2f} {bar['high']:>8.2f} {bar['low']:>8.2f} {bar['close']:>8.2f} {prev_str:>10} {reasons_str}")'''

content = content.replace(old_print, new_print)

with open('scripts/phase_c_backfill_triangles.py', 'w') as f:
    f.write(content)

print('Added debug logging')

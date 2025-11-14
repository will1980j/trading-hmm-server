from collections import defaultdict

# Manually parse the alerts from the CSV
alerts_data = []

with open('TradingView_Alerts_Log_2025-11-14_575e3.csv', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Find all signal_ids
    import re
    signal_ids = re.findall(r'"signal_id":"([\d_A-Z]+)"', content)
    types = re.findall(r'"type":"([A-Z_]+)"', content)
    times = re.findall(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', content)
    
    # Combine them
    for i in range(min(len(signal_ids), len(types), len(times))):
        alerts_data.append({
            'signal_id': signal_ids[i],
            'type': types[i],
            'time': times[i]
        })

# Reverse to chronological order
alerts_data.reverse()

# Group by signal
signals = defaultdict(list)
for alert in alerts_data:
    signals[alert['signal_id']].append(alert)

print("=" * 80)
print("ALERT ANALYSIS - DUPLICATE FIX VERIFICATION")
print("=" * 80)
print(f"\nTotal Signals: {len(signals)}")
print(f"Total Alerts: {len(alerts_data)}\n")

# Analyze each signal
for signal_id in sorted(signals.keys()):
    signal_alerts = signals[signal_id]
    print(f"\n{'='*80}")
    print(f"SIGNAL: {signal_id}")
    print(f"{'='*80}")
    
    # Count alert types
    entry_count = sum(1 for a in signal_alerts if a['type'] == 'ENTRY')
    mfe_count = sum(1 for a in signal_alerts if a['type'] == 'MFE_UPDATE')
    be_count = sum(1 for a in signal_alerts if a['type'] == 'BE_TRIGGERED')
    exit_count = sum(1 for a in signal_alerts if 'EXIT' in a['type'])
    
    print(f"ENTRY: {entry_count} | MFE_UPDATE: {mfe_count} | BE_TRIGGERED: {be_count} | EXIT: {exit_count}")
    print()
    
    # Show first 5 alerts
    print("First 5 Alerts:")
    for i, alert in enumerate(signal_alerts[:5], 1):
        print(f"  {i}. {alert['time']} - {alert['type']}")
    if len(signal_alerts) > 5:
        print(f"  ... ({len(signal_alerts) - 5} more)")
    print()
    
    # Check for issues
    issues = []
    
    # Check 1: Multiple ENTRY
    if entry_count > 1:
        issues.append(f"❌ DUPLICATE ENTRY: {entry_count} ENTRY alerts")
    elif entry_count == 1:
        print("✅ Single ENTRY alert")
    
    # Check 2: ENTRY first
    if signal_alerts and signal_alerts[0]['type'] != 'ENTRY':
        issues.append(f"❌ ENTRY NOT FIRST: First is {signal_alerts[0]['type']}")
    elif signal_alerts:
        print("✅ ENTRY is first alert")
    
    # Check 3: Duplicate MFE at same time
    mfe_alerts = [a for a in signal_alerts if a['type'] == 'MFE_UPDATE']
    mfe_times = {}
    for alert in mfe_alerts:
        t = alert['time']
        mfe_times[t] = mfe_times.get(t, 0) + 1
    
    dups = {t: c for t, c in mfe_times.items() if c > 1}
    if dups:
        for t, c in dups.items():
            issues.append(f"❌ {c} MFE_UPDATE at {t}")
    else:
        print("✅ No duplicate MFE_UPDATE")
    
    # Check 4: Signal ID format (milliseconds)
    parts = signal_id.split('_')
    if len(parts) >= 2:
        time_part = parts[1]
        if len(time_part) >= 9:  # HHMMSSMMM
            print(f"✅ Signal ID has milliseconds ({time_part})")
        else:
            issues.append(f"❌ NO milliseconds in ID ({time_part})")
    
    if issues:
        print("\n⚠️  ISSUES:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ ALL CHECKS PASSED!")

print("\n" + "=" * 80)
print("OVERALL ASSESSMENT")
print("=" * 80)

# Check if all signal IDs have milliseconds
all_have_ms = all(len(sid.split('_')[1]) >= 9 for sid in signals.keys() if len(sid.split('_')) >= 2)
if all_have_ms:
    print("✅ All signal IDs have milliseconds (FIX WORKING)")
else:
    print("❌ Some signal IDs missing milliseconds (FIX NOT APPLIED)")

# Check for any duplicate ENTRY alerts
any_dup_entry = any(sum(1 for a in alerts if a['type'] == 'ENTRY') > 1 for alerts in signals.values())
if not any_dup_entry:
    print("✅ No duplicate ENTRY alerts (FIX WORKING)")
else:
    print("❌ Found duplicate ENTRY alerts (FIX NOT WORKING)")

# Check if ENTRY is always first
all_entry_first = all(alerts[0]['type'] == 'ENTRY' for alerts in signals.values() if alerts)
if all_entry_first:
    print("✅ ENTRY always first (FIX WORKING)")
else:
    print("❌ ENTRY not always first (FIX NOT WORKING)")

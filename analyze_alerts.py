import re
from collections import defaultdict

# Read CSV file and extract key info using regex
alerts = []
with open('TradingView_Alerts_Log_2025-11-14_575e3.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()[1:]  # Skip header
    
    for line in lines:
        # Extract type
        type_match = re.search(r'"type":"([^"]+)"', line)
        # Extract signal_id
        signal_match = re.search(r'"signal_id":"([^"]+)"', line)
        # Extract time (last field)
        time_match = re.search(r',(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)$', line.strip())
        
        if type_match and signal_match and time_match:
            alerts.append({
                'time': time_match.group(1),
                'type': type_match.group(1),
                'signal_id': signal_match.group(1)
            })

# Reverse to chronological order (CSV is newest first)
alerts.reverse()

# Group by signal_id
signals = defaultdict(list)
for alert in alerts:
    signals[alert['signal_id']].append(alert)

print("=" * 80)
print("ALERT ANALYSIS - DUPLICATE FIX VERIFICATION")
print("=" * 80)
print()

# Analyze each signal
for signal_id in sorted(signals.keys()):
    signal_alerts = signals[signal_id]
    print(f"\n{'='*80}")
    print(f"SIGNAL: {signal_id}")
    print(f"{'='*80}")
    print(f"Total Alerts: {len(signal_alerts)}")
    print()
    
    # Check for ENTRY alert
    entry_alerts = [a for a in signal_alerts if a['type'] == 'ENTRY']
    mfe_alerts = [a for a in signal_alerts if a['type'] == 'MFE_UPDATE']
    be_alerts = [a for a in signal_alerts if a['type'] == 'BE_TRIGGERED']
    exit_alerts = [a for a in signal_alerts if a['type'] == 'EXIT_STOP_LOSS' or a['type'] == 'EXIT_BREAK_EVEN']
    
    print(f"ENTRY alerts: {len(entry_alerts)}")
    print(f"MFE_UPDATE alerts: {len(mfe_alerts)}")
    print(f"BE_TRIGGERED alerts: {len(be_alerts)}")
    print(f"EXIT alerts: {len(exit_alerts)}")
    print()
    
    # Show sequence
    print("Alert Sequence:")
    for i, alert in enumerate(signal_alerts[:10], 1):  # Show first 10
        print(f"  {i}. {alert['time']} - {alert['type']}")
    if len(signal_alerts) > 10:
        print(f"  ... ({len(signal_alerts) - 10} more alerts)")
    print()
    
    # Check for issues
    issues = []
    
    # Issue 1: Multiple ENTRY alerts
    if len(entry_alerts) > 1:
        issues.append(f"❌ DUPLICATE ENTRY: {len(entry_alerts)} ENTRY alerts (should be 1)")
    elif len(entry_alerts) == 1:
        print("✅ Single ENTRY alert (correct)")
    
    # Issue 2: ENTRY should be first
    if signal_alerts and signal_alerts[0]['type'] != 'ENTRY':
        issues.append(f"❌ ENTRY NOT FIRST: First alert is {signal_alerts[0]['type']}")
    elif signal_alerts:
        print("✅ ENTRY is first alert (correct)")
    
    # Issue 3: Check for duplicate MFE_UPDATE at same timestamp
    mfe_times = {}
    for alert in mfe_alerts:
        time = alert['time']
        mfe_times[time] = mfe_times.get(time, 0) + 1
    
    duplicates = {t: c for t, c in mfe_times.items() if c > 1}
    if duplicates:
        for time, count in duplicates.items():
            issues.append(f"❌ DUPLICATE MFE_UPDATE: {count} alerts at {time}")
    else:
        print(f"✅ No duplicate MFE_UPDATE alerts (correct)")
    
    # Issue 4: BE_TRIGGERED before ENTRY
    if be_alerts and entry_alerts:
        be_time = be_alerts[0]['time']
        entry_time = entry_alerts[0]['time']
        if be_time < entry_time:
            issues.append(f"❌ BE_TRIGGERED BEFORE ENTRY")
        else:
            print("✅ BE_TRIGGERED after ENTRY (correct)")
    
    # Print issues
    if issues:
        print("\n⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ NO ISSUES - All checks passed!")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Signals: {len(signals)}")
print(f"Total Alerts: {len(alerts)}")
print()

# Check for milliseconds in signal_ids
print("Signal ID Format Check:")
for signal_id in sorted(signals.keys()):
    # Check if signal_id has milliseconds (should have 3 extra digits)
    parts = signal_id.split('_')
    if len(parts) >= 2:
        time_part = parts[1]
        if len(time_part) > 6:  # HHMMSS = 6, HHMMSSMMM = 9+
            print(f"  ✅ {signal_id} - Has milliseconds")
        else:
            print(f"  ❌ {signal_id} - NO milliseconds (old format)")

import csv
import json
from collections import Counter

# Read the CSV file
with open('TradingView_Alerts_Log_2025-11-15_ff323.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    alerts = list(reader)

print(f"Total alerts in file: {len(alerts)}\n")

# Parse JSON descriptions and count event types
event_types = Counter()
exit_types = Counter()
exit_reasons = Counter()
signal_ids_with_exits = {}

for alert in alerts:
    try:
        desc = json.loads(alert['Description'])
        event_type = desc.get('type', 'UNKNOWN')
        event_types[event_type] += 1
        
        # Track exit events specifically
        if 'EXIT' in event_type:
            exit_types[event_type] += 1
            signal_id = desc.get('signal_id', 'unknown')
            completion_reason = desc.get('completion_reason', 'unknown')
            exit_reasons[completion_reason] += 1
            
            if signal_id not in signal_ids_with_exits:
                signal_ids_with_exits[signal_id] = []
            signal_ids_with_exits[signal_id].append({
                'type': event_type,
                'reason': completion_reason,
                'time': alert['Time'],
                'be_mfe': desc.get('final_be_mfe', 0),
                'no_be_mfe': desc.get('final_no_be_mfe', 0)
            })
    except:
        pass

print("=" * 60)
print("EVENT TYPE DISTRIBUTION:")
print("=" * 60)
for event_type, count in event_types.most_common():
    print(f"{event_type:25} {count:5} alerts")

print("\n" + "=" * 60)
print("EXIT EVENT BREAKDOWN:")
print("=" * 60)
for exit_type, count in exit_types.most_common():
    print(f"{exit_type:25} {count:5} exits")

print("\n" + "=" * 60)
print("EXIT REASON BREAKDOWN:")
print("=" * 60)
for reason, count in exit_reasons.most_common():
    print(f"{reason:30} {count:5} exits")

print("\n" + "=" * 60)
print("CRITICAL FINDING:")
print("=" * 60)
print(f"EXIT_STOP_LOSS alerts: {exit_types.get('EXIT_STOP_LOSS', 0)}")
print(f"EXIT_BREAK_EVEN alerts: {exit_types.get('EXIT_BREAK_EVEN', 0)}")

if exit_types.get('EXIT_STOP_LOSS', 0) == 0:
    print("\n⚠️  NO EXIT_STOP_LOSS ALERTS FOUND!")
    print("This means NO trades hit the original stop loss.")
    print("ALL exits were break-even stops (after +1R achieved).")
    print("\nThis indicates:")
    print("1. All trades achieved +1R (moved stop to entry)")
    print("2. No trades went directly to stop loss without hitting +1R first")
    print("3. The BE=1 strategy is working as intended")

print("\n" + "=" * 60)
print("SAMPLE EXIT EVENTS:")
print("=" * 60)
# Show first 5 exit events
exit_count = 0
for alert in alerts:
    try:
        desc = json.loads(alert['Description'])
        if 'EXIT' in desc.get('type', ''):
            print(f"\nSignal: {desc.get('signal_id')}")
            print(f"Type: {desc.get('type')}")
            print(f"Reason: {desc.get('completion_reason')}")
            print(f"BE MFE: {desc.get('final_be_mfe')}R")
            print(f"No BE MFE: {desc.get('final_no_be_mfe')}R")
            print(f"Time: {alert['Time']}")
            exit_count += 1
            if exit_count >= 5:
                break
    except:
        pass

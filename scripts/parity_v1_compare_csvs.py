#!/usr/bin/env python3
import csv, sys

python_csv = sys.argv[1] if len(sys.argv) > 1 else 'python_bias.csv'
tv_csv = sys.argv[2] if len(sys.argv) > 2 else 'tv_bias.csv'

# Read Python CSV
python_data = {}
with open(python_csv, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        python_data[row['ts_utc']] = int(row['bias_code'])

# Read TradingView CSV (exported chart data)
tv_data = {}
with open(tv_csv, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # TradingView exports with 'time' column
        ts = row.get('time', row.get('Time', row.get('ts_utc', '')))
        bias_code = int(float(row.get('Bias Code', row.get('bias_code', 0))))
        tv_data[ts] = bias_code

# Compare
mismatches = []
for ts in python_data:
    if ts not in tv_data:
        continue
    if python_data[ts] != tv_data[ts]:
        mismatches.append((ts, python_data[ts], tv_data[ts]))

print(f"Total bars compared: {len(python_data)}")
print(f"Mismatches: {len(mismatches)}")

if mismatches:
    print(f"\nFirst 50 mismatches:")
    for ts, py_code, tv_code in mismatches[:50]:
        py_str = "Bullish" if py_code == 1 else "Bearish" if py_code == -1 else "Neutral"
        tv_str = "Bullish" if tv_code == 1 else "Bearish" if tv_code == -1 else "Neutral"
        print(f"  {ts}: Python={py_str}({py_code}), TV={tv_str}({tv_code})")
    sys.exit(1)
else:
    print("✅ PERFECT MATCH - Parity V1 PASS")
    sys.exit(0)

"""
Monitor Export Progress
Checks every 5 minutes until export completes
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("MONITORING EXPORT PROGRESS")
print("=" * 80)
print()

target_signals = 2147
last_count = 0
start_time = time.time()

while True:
    # Check inspector
    r = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
    data = r.json()
    current_count = data.get('total_signals', 0)
    
    # Check database
    r2 = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
    db_data = r2.json()
    db_count = db_data['stats']['active_count'] + db_data['stats']['completed_count']
    
    elapsed = int((time.time() - start_time) / 60)
    progress_pct = (current_count / target_signals) * 100 if target_signals > 0 else 0
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ({elapsed}m elapsed)")
    print(f"  Inspector: {current_count}/{target_signals} ({progress_pct:.1f}%)")
    print(f"  Database: {db_count} signals")
    print(f"  Rate: {current_count - last_count} signals/5min")
    
    if current_count >= target_signals:
        print()
        print("=" * 80)
        print("✅ EXPORT COMPLETE!")
        print("=" * 80)
        print()
        print(f"Total signals exported: {current_count}")
        print(f"Total time: {elapsed} minutes")
        print()
        print("Running final import...")
        break
    
    last_count = current_count
    print()
    time.sleep(300)  # Wait 5 minutes

# Run final import
import subprocess
import sys
result = subprocess.run([sys.executable, "import_indicator_data.py"], capture_output=True, text=True)
print(result.stdout)

# Final verification
r = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
data = r.json()
print()
print("=" * 80)
print("FINAL DATABASE STATUS")
print("=" * 80)
print(f"Active: {data['stats']['active_count']}")
print(f"Completed: {data['stats']['completed_count']}")
print(f"Total: {data['stats']['active_count'] + data['stats']['completed_count']}")
print()
print("✅ Export and import complete!")
print("Open dashboard: https://web-production-f8c3.up.railway.app/automated-signals")

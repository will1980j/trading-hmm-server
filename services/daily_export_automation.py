"""
Daily Export Automation Service
Automatically exports indicator data daily at 3:30 PM ET
"""

import schedule
import time
import requests
from datetime import datetime
import pytz
import subprocess
import sys

BASE_URL = "https://web-production-f8c3.up.railway.app"

def run_daily_export():
    """Run the complete daily export workflow"""
    print("=" * 80)
    print(f"DAILY EXPORT STARTED - {datetime.now()}")
    print("=" * 80)
    print()
    
    # Step 1: Wait for export to complete (monitor inspector)
    print("Step 1: Monitoring export completion...")
    max_wait = 180  # 3 hours max
    waited = 0
    target_signals = 1576  # Approximate
    
    while waited < max_wait:
        try:
            r = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
            data = r.json()
            current_count = data.get('total_signals', 0)
            
            print(f"  [{waited}m] Inspector has {current_count} signals")
            
            # Check if export is complete (no new signals for 10 minutes)
            if current_count > 0:
                time.sleep(600)  # Wait 10 minutes
                r2 = requests.get(f"{BASE_URL}/api/indicator-inspector/summary")
                new_count = r2.json().get('total_signals', 0)
                
                if new_count == current_count:
                    print(f"  Export complete! {current_count} signals exported")
                    break
            
            waited += 10
            time.sleep(600)  # Check every 10 minutes
            
        except Exception as e:
            print(f"  Error monitoring: {e}")
            time.sleep(600)
    
    # Step 2: Import confirmed signals
    print()
    print("Step 2: Importing confirmed signals...")
    try:
        result = subprocess.run(
            [sys.executable, "import_indicator_data.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"  Error importing: {e}")
    
    # Step 3: Clear inspector
    print()
    print("Step 3: Clearing inspector...")
    try:
        r = requests.post(f"{BASE_URL}/api/indicator-inspector/clear")
        print(f"  {r.json()['message']}")
    except Exception as e:
        print(f"  Error clearing: {e}")
    
    # Step 4: Verify database
    print()
    print("Step 4: Verifying database...")
    try:
        r = requests.get(f"{BASE_URL}/api/automated-signals/stats-live")
        stats = r.json()['stats']
        total = stats['active_count'] + stats['completed_count']
        print(f"  Active: {stats['active_count']}")
        print(f"  Completed: {stats['completed_count']}")
        print(f"  Total: {total}")
    except Exception as e:
        print(f"  Error verifying: {e}")
    
    print()
    print("=" * 80)
    print("DAILY EXPORT COMPLETE")
    print("=" * 80)
    print()

def schedule_daily_exports():
    """Schedule daily exports at 3:30 PM ET"""
    eastern = pytz.timezone('America/New_York')
    
    # Schedule for weekdays only (Mon-Fri)
    schedule.every().monday.at("15:30").do(run_daily_export)
    schedule.every().tuesday.at("15:30").do(run_daily_export)
    schedule.every().wednesday.at("15:30").do(run_daily_export)
    schedule.every().thursday.at("15:30").do(run_daily_export)
    schedule.every().friday.at("15:30").do(run_daily_export)
    
    print("=" * 80)
    print("DAILY EXPORT AUTOMATION SERVICE")
    print("=" * 80)
    print()
    print("Scheduled: 3:30 PM ET (Mon-Fri)")
    print("Process:")
    print("  1. Monitor export completion")
    print("  2. Import to database")
    print("  3. Clear inspector")
    print("  4. Verify data")
    print()
    print("Service running... (Ctrl+C to stop)")
    print("=" * 80)
    print()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    schedule_daily_exports()

#!/usr/bin/env python3
"""
Daily Level Tracking Job
Run this script daily to:
1. Capture today's predicted levels
2. Analyze yesterday's level hits
3. Update accuracy scores
"""

import schedule
import time
from datetime import datetime
from level_tracker import run_daily_level_tracking

def daily_job():
    """Daily level tracking job"""
    print(f"Running daily level tracking at {datetime.now()}")
    
    try:
        report = run_daily_level_tracking()
        print("Level tracking completed successfully")
        print("Current accuracy report:")
        for row in report:
            level_type, total, hits, accuracy, confidence = row[1], row[2], row[3], float(row[4]), float(row[5])
            print(f"  {level_type.upper()}: {accuracy:.1f}% accuracy ({confidence:.1f}% confidence)")
    
    except Exception as e:
        print(f"Error in daily level tracking: {e}")

if __name__ == "__main__":
    # Schedule daily job at 6 AM EST (before market open)
    schedule.every().day.at("06:00").do(daily_job)
    
    # Run once immediately for testing
    print("Running initial level tracking...")
    daily_job()
    
    print("Daily level tracking scheduled for 6:00 AM EST")
    print("Press Ctrl+C to stop")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
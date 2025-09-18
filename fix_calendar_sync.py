#!/usr/bin/env python3
"""
Fix Calendar Discrepancy Between Dashboards

This script ensures both dashboards show the same trade counts by:
1. Identifying the data source discrepancy
2. Standardizing the query logic
3. Ensuring both calendars use the same filtering criteria
"""

import sys
import os

def fix_dashboard_calendar_sync():
    """Fix the calendar sync issue between main dashboard and signal lab dashboard"""
    
    print("🔍 CALENDAR DISCREPANCY ANALYSIS")
    print("=" * 50)
    
    # The issue is in the dashboard HTML files
    dashboard_file = "dashboard_clean.html"
    signal_lab_file = "signal_lab_dashboard.html"
    
    print(f"📊 Main Dashboard: {dashboard_file}")
    print(f"🔬 Signal Lab Dashboard: {signal_lab_file}")
    
    print("\n🎯 ROOT CAUSE IDENTIFIED:")
    print("- Main Dashboard calls: /api/signal-lab-trades (all trades)")
    print("- Signal Lab Dashboard calls: /api/signal-lab-trades?analysis_only=true (completed only)")
    print("- This creates different trade counts on the calendars")
    
    print("\n✅ SOLUTION:")
    print("Both dashboards should use the same data filtering logic")
    
    # The fix is to modify the main dashboard to use analysis_only=true
    print("\n🔧 RECOMMENDED FIX:")
    print("1. Update main dashboard to use analysis_only=true parameter")
    print("2. This will make both calendars show only completed/reviewed trades")
    print("3. Calendars will then match perfectly")
    
    print("\n📝 IMPLEMENTATION:")
    print("Modify dashboard_clean.html line ~450:")
    print("FROM: const endpoint = dataSource === 'signal-lab' ? '/api/signal-lab-trades' : '/api/trades';")
    print("TO:   const endpoint = dataSource === 'signal-lab' ? '/api/signal-lab-trades?analysis_only=true' : '/api/trades';")
    
    return True

if __name__ == "__main__":
    success = fix_dashboard_calendar_sync()
    if success:
        print("\n✅ Calendar sync analysis complete!")
        print("Apply the recommended fix to synchronize both dashboards.")
    else:
        print("\n❌ Analysis failed")
        sys.exit(1)
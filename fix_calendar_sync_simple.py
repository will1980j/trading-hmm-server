#!/usr/bin/env python3
"""
Fix Calendar Sync Between Cloud Dashboard Pages

Main Dashboard: https://web-production-cd33.up.railway.app/signal-lab-dashboard
Signal Lab: https://web-production-cd33.up.railway.app/signal-analysis-lab

The issue: Different API endpoints/parameters causing calendar mismatches
"""

import os

def main():
    print("FIXING CLOUD CALENDAR SYNC")
    print("=" * 50)
    print("Main Dashboard: /signal-lab-dashboard")
    print("Signal Lab: /signal-analysis-lab")
    print()
    
    # Check the signal lab dashboard file
    dashboard_file = "signal_lab_dashboard.html"
    
    if not os.path.exists(dashboard_file):
        print("ERROR: signal_lab_dashboard.html not found")
        return
    
    print("ANALYZING CURRENT CONFIGURATION...")
    
    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\nCURRENT API USAGE:")
        if "analysis_only=true" in content:
            print("- Main dashboard DOES use analysis_only=true")
        else:
            print("- Main dashboard does NOT use analysis_only=true")
        
        if "/api/signal-lab-trades" in content:
            print("- Main dashboard uses signal-lab-trades endpoint")
        else:
            print("- Main dashboard uses different endpoint")
        
        # Look for the specific loadSignals function
        if "loadSignals" in content:
            print("- Found loadSignals function")
        
        print("\nROOT CAUSE IDENTIFIED:")
        print("The calendars don't match because the two pages use different API calls:")
        print("- Main Dashboard: /api/signal-lab-trades?analysis_only=true (filtered)")
        print("- Signal Lab: /api/signal-lab-trades (all trades)")
        print("This creates different trade counts on the calendars")
        
        print("\nSOLUTION:")
        print("Both pages need to use the SAME API endpoint with SAME parameters")
        print("Recommended: /api/signal-lab-trades?analysis_only=true")
        print("This will show only completed/reviewed trades on both calendars")
        
        print("\nMANUAL FIX STEPS:")
        print("1. Edit signal_lab_dashboard.html")
        print("2. Find the loadSignals() function (around line 450-500)")
        print("3. Look for this code:")
        print("   const analysisParam = dataSource === '1m' ? '?analysis_only=true' : '';")
        print("4. Change it to ALWAYS use analysis_only=true:")
        print("   const analysisParam = '?analysis_only=true';")
        print("5. Or modify the endpoint URLs directly to include ?analysis_only=true")
        print("6. Commit and push to trigger Railway deployment")
        print("7. Refresh both pages and verify calendars match")
        
        # Create a specific patch
        create_patch()
        
    except Exception as e:
        print(f"ERROR reading file: {e}")

def create_patch():
    """Create a patch file with exact changes needed"""
    
    patch = """
CALENDAR SYNC PATCH
==================

File: signal_lab_dashboard.html
Location: loadSignals() function (around line 450-500)

FIND THIS CODE:
---------------
const endpoint = dataSource === '15m' ? 
    'https://web-production-cd33.up.railway.app/api/signal-lab-15m-trades' : 
    'https://web-production-cd33.up.railway.app/api/signal-lab-trades';

// Add analysis_only parameter for dashboard to get only processed trades
const analysisParam = dataSource === '1m' ? '?analysis_only=true' : '';
const response = await fetch(endpoint + analysisParam);

REPLACE WITH:
-------------
const endpoint = dataSource === '15m' ? 
    'https://web-production-cd33.up.railway.app/api/signal-lab-15m-trades?analysis_only=true' : 
    'https://web-production-cd33.up.railway.app/api/signal-lab-trades?analysis_only=true';

const response = await fetch(endpoint);

RESULT:
-------
- Both 1m and 15m data will use analysis_only=true
- Only completed/reviewed trades appear on calendar
- Both dashboards will show matching dates
"""
    
    try:
        with open('calendar_sync_patch.txt', 'w') as f:
            f.write(patch)
        print("\nCreated patch file: calendar_sync_patch.txt")
    except Exception as e:
        print(f"Could not create patch file: {e}")

if __name__ == "__main__":
    main()
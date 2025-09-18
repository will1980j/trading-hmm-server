#!/usr/bin/env python3
"""
Fix Calendar Sync Between Cloud Dashboard Pages

Main Dashboard: https://web-production-cd33.up.railway.app/signal-lab-dashboard
Signal Lab: https://web-production-cd33.up.railway.app/signal-analysis-lab

The issue: Different API endpoints/parameters causing calendar mismatches
Solution: Ensure both use the same data filtering logic
"""

import os
import sys

def fix_cloud_calendar_sync():
    """Fix calendar sync between cloud dashboard pages"""
    
    print("FIXING CLOUD CALENDAR SYNC")
    print("=" * 50)
    print("Main Dashboard: /signal-lab-dashboard")
    print("Signal Lab: /signal-analysis-lab")
    print()
    
    # Find the relevant HTML files
    files_to_check = [
        "signal_lab_dashboard.html",  # Main dashboard
        "signal_analysis_lab.html",   # Signal lab (if exists)
        "migrate_signal_lab.html",    # Alternative signal lab file
    ]
    
    files_found = []
    for file_path in files_to_check:
        if os.path.exists(file_path):
            files_found.append(file_path)
            print(f"Found: {file_path}")
    
    if not files_found:
        print("No dashboard files found in current directory")
        return False
    
    print(f"\n🎯 IDENTIFIED ISSUE:")
    print("The calendars don't match because:")
    print("• Main dashboard may use: /api/signal-lab-trades?analysis_only=true")
    print("• Signal lab may use: /api/signal-lab-trades (all trades)")
    print("• This creates different trade counts on calendars")
    
    print(f"\n✅ SOLUTION:")
    print("Both pages should use the SAME API endpoint with SAME parameters")
    print("Recommended: /api/signal-lab-trades?analysis_only=true")
    print("This shows only completed/reviewed trades on both calendars")
    
    # Check signal_lab_dashboard.html for current API usage
    dashboard_file = "signal_lab_dashboard.html"
    if os.path.exists(dashboard_file):
        print(f"\n🔍 Analyzing {dashboard_file}...")
        
        try:
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check current API usage
            if "analysis_only=true" in content:
                print("✅ Main dashboard already uses analysis_only=true")
            else:
                print("⚠️  Main dashboard may not use analysis_only=true")
            
            if "/api/signal-lab-trades" in content:
                print("✅ Main dashboard uses signal-lab-trades endpoint")
            else:
                print("⚠️  Main dashboard may use different endpoint")
                
        except Exception as e:
            print(f"❌ Error reading {dashboard_file}: {e}")
    
    print(f"\n🔧 MANUAL FIX REQUIRED:")
    print("Since these are cloud-deployed pages, you need to:")
    print()
    print("1. 📝 Edit the source files:")
    print("   • signal_lab_dashboard.html (main dashboard)")
    print("   • Any signal lab HTML file")
    print()
    print("2. 🔍 Find the JavaScript code that loads calendar data:")
    print("   Look for: fetch('/api/signal-lab-trades')")
    print("   Or: loadSignals() function")
    print()
    print("3. ✏️  Ensure BOTH files use the SAME endpoint:")
    print("   Change to: '/api/signal-lab-trades?analysis_only=true'")
    print()
    print("4. 🚀 Redeploy to Railway:")
    print("   • Commit changes to git")
    print("   • Push to trigger Railway deployment")
    print()
    print("5. ✅ Verify fix:")
    print("   • Refresh both pages")
    print("   • Check calendars show same dates")
    
    # Create a patch file for easy application
    create_patch_file()
    
    return True

def create_patch_file():
    """Create a patch file with the exact changes needed"""
    
    patch_content = '''
# CALENDAR SYNC PATCH
# Apply these changes to fix calendar discrepancy

## File: signal_lab_dashboard.html
## Location: Around line 450-500 in loadSignals() function

### FIND THIS CODE:
const endpoint = dataSource === '15m' ? 
    'https://web-production-cd33.up.railway.app/api/signal-lab-15m-trades' : 
    'https://web-production-cd33.up.railway.app/api/signal-lab-trades';

// Add analysis_only parameter for dashboard to get only processed trades
const analysisParam = dataSource === '1m' ? '?analysis_only=true' : '';
const response = await fetch(endpoint + analysisParam);

### REPLACE WITH:
const endpoint = dataSource === '15m' ? 
    'https://web-production-cd33.up.railway.app/api/signal-lab-15m-trades?analysis_only=true' : 
    'https://web-production-cd33.up.railway.app/api/signal-lab-trades?analysis_only=true';

const response = await fetch(endpoint);

## This ensures BOTH 1m and 15m data use analysis_only=true
## Result: Only completed/reviewed trades appear on calendar
## Both dashboards will then show matching dates
'''
    
    try:
        with open('calendar_sync_patch.txt', 'w', encoding='utf-8') as f:
            f.write(patch_content)
        print(f"\n📄 Created patch file: calendar_sync_patch.txt")
        print("   Use this as a reference for manual fixes")
    except Exception as e:
        print(f"⚠️  Could not create patch file: {e}")

if __name__ == "__main__":
    success = fix_cloud_calendar_sync()
    if success:
        print(f"\n🎯 SUMMARY:")
        print("Calendar sync issue identified and solution provided")
        print("Manual deployment required to fix cloud pages")
    else:
        print(f"\n❌ Could not complete analysis")
#!/usr/bin/env python3
"""
Final Calendar Sync Fix

The issue is that the Signal Lab Dashboard uses analysis_only=true parameter
while the main dashboard doesn't, causing different trade counts.

This script fixes the discrepancy by updating the main dashboard to use
the same filtering logic as the Signal Lab Dashboard.
"""

import os

def fix_calendar_sync():
    """Fix calendar sync by updating main dashboard to use analysis_only=true"""
    
    print("🔧 FIXING CALENDAR SYNC DISCREPANCY")
    print("=" * 50)
    
    # Find the main dashboard file
    dashboard_files = [
        "trading-hmm-server/advanced_trading_dashboard.html",
        "advanced_trading_dashboard.html"
    ]
    
    main_dashboard = None
    for file_path in dashboard_files:
        if os.path.exists(file_path):
            main_dashboard = file_path
            break
    
    if not main_dashboard:
        print("❌ Main dashboard file not found")
        return False
    
    print(f"📊 Found main dashboard: {main_dashboard}")
    
    # Read the file
    try:
        with open(main_dashboard, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Look for the API endpoint that needs fixing
    original_line = "const response = await fetch('/api/trades');"
    replacement_line = "const response = await fetch('/api/signal-lab-trades?analysis_only=true');"
    
    # Also look for alternative patterns
    patterns_to_fix = [
        ("'/api/trades'", "'/api/signal-lab-trades?analysis_only=true'"),
        ("const response = await fetch('/api/trades');", "const response = await fetch('/api/signal-lab-trades?analysis_only=true');"),
        ("fetch('/api/trades')", "fetch('/api/signal-lab-trades?analysis_only=true')"),
    ]
    
    changes_made = 0
    for old_pattern, new_pattern in patterns_to_fix:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            changes_made += 1
            print(f"✅ Fixed: {old_pattern} → {new_pattern}")
    
    if changes_made == 0:
        print("⚠️  No matching patterns found to fix")
        print("Looking for existing patterns in file...")
        
        # Check what's actually in the file
        if "signal-lab-trades" in content:
            print("✅ File already uses signal-lab-trades endpoint")
        if "analysis_only=true" in content:
            print("✅ File already uses analysis_only=true parameter")
        
        if "signal-lab-trades" in content and "analysis_only=true" in content:
            print("✅ Calendar sync should already be working!")
            return True
        
        return False
    
    # Write the updated content back
    try:
        with open(main_dashboard, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {main_dashboard} with {changes_made} changes")
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False
    
    print("\n🎯 CALENDAR SYNC FIX COMPLETE!")
    print("=" * 50)
    print("✅ Both dashboards now use the same data source:")
    print("   • Main Dashboard: /api/signal-lab-trades?analysis_only=true")
    print("   • Signal Lab Dashboard: /api/signal-lab-trades?analysis_only=true")
    print("\n📋 Next Steps:")
    print("1. Refresh both dashboard pages")
    print("2. Check that calendar dates now match")
    print("3. Both should show only completed/processed trades")
    
    return True

if __name__ == "__main__":
    success = fix_calendar_sync()
    if success:
        print("\n✅ Fix applied successfully!")
    else:
        print("\n❌ Fix failed - manual intervention required")
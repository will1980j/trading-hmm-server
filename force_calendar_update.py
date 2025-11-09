"""
Force update the automated signals dashboard with calendar
This adds a comment to ensure Git detects the change
"""

def force_update():
    file_path = 'templates/automated_signals_dashboard.html'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add a timestamp comment at the top of the script section to force Git to see a change
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Find the script tag and add a comment
    script_marker = '<script>'
    if script_marker in content:
        comment = f'\n        // Calendar implementation updated: {timestamp}\n'
        content = content.replace(script_marker, script_marker + comment, 1)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Added timestamp comment to force Git detection")
        print(f"  Timestamp: {timestamp}")
        print(f"\nNow check GitHub Desktop - the file should appear!")
        print(f"\nIf it still doesn't show:")
        print(f"1. Close GitHub Desktop completely")
        print(f"2. Delete the file: templates/automated_signals_dashboard.html")
        print(f"3. Reopen GitHub Desktop (it will show as deleted)")
        print(f"4. Run this script again to recreate it")
        print(f"5. GitHub Desktop will then show it as a new file")
        
        return True
    else:
        print("✗ Could not find script tag")
        return False

if __name__ == '__main__':
    force_update()

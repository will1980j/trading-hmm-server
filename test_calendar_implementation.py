"""
Test to verify the calendar implementation is present in the automated signals dashboard
"""

def test_calendar_in_file():
    with open('templates/automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for calendar HTML elements
    checks = {
        'Calendar Section': '<h2 class="panel-title">Trading Calendar</h2>' in content,
        'Calendar Grid': '<div class="calendar-grid" id="calendarGrid">' in content,
        'Month Navigation': 'function changeMonth(direction)' in content,
        'Update Calendar Function': 'function updateCalendar()' in content,
        'Filter Date Function': 'function filterDate(dateStr)' in content,
        'Calendar CSS': '.calendar-grid {' in content,
        'Calendar Day CSS': '.calendar-day {' in content,
        'Calendar Initialization': 'updateCalendar();' in content,
    }
    
    print("Calendar Implementation Check:")
    print("=" * 50)
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("✓ All calendar components are present!")
        print("\nThe calendar is fully implemented in the file.")
        print("If you don't see it in GitHub Desktop, try:")
        print("1. Refresh GitHub Desktop (Ctrl+R)")
        print("2. Close and reopen GitHub Desktop")
        print("3. Check you're in the correct repository")
    else:
        print("✗ Some calendar components are missing!")
    
    return all_passed

if __name__ == '__main__':
    test_calendar_in_file()

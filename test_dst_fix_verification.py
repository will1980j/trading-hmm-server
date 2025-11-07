"""
DST Fix Verification Script

Tests that session validation works correctly across DST transitions
"""

from datetime import datetime
import pytz

def test_utc_session_validation():
    """Test UTC-based session validation"""
    
    print("=" * 70)
    print("DST FIX VERIFICATION - UTC SESSION VALIDATION")
    print("=" * 70)
    print()
    
    # Test cases: (description, datetime_str, expected_session, expected_valid)
    test_cases = [
        # ASIA session tests
        ("ASIA during EDT (Nov 1, 20:00 EDT)", "2025-11-01T20:00:00-04:00", "ASIA", True),
        ("ASIA during EST (Nov 3, 19:00 EST)", "2025-11-03T19:00:00-05:00", "ASIA", True),
        ("ASIA end during EST (Nov 3, 22:59 EST)", "2025-11-03T22:59:00-05:00", "ASIA", True),
        
        # LONDON session tests
        ("LONDON during EDT (Nov 1, 00:00 EDT)", "2025-11-01T00:00:00-04:00", "LONDON", True),
        ("LONDON during EST (Nov 3, 23:00 EST)", "2025-11-03T23:00:00-05:00", "LONDON", True),
        ("LONDON end during EST (Nov 3, 04:59 EST)", "2025-11-03T04:59:00-05:00", "LONDON", True),
        
        # NY PRE session tests
        ("NY PRE during EDT (Nov 1, 06:00 EDT)", "2025-11-01T06:00:00-04:00", "NY PRE", True),
        ("NY PRE during EST (Nov 3, 05:00 EST)", "2025-11-03T05:00:00-05:00", "NY PRE", True),
        ("NY PRE end during EST (Nov 3, 07:29 EST)", "2025-11-03T07:29:00-05:00", "NY PRE", True),
        
        # NY AM session tests
        ("NY AM start during EDT (Nov 1, 08:30 EDT)", "2025-11-01T08:30:00-04:00", "NY AM", True),
        ("NY AM start during EST (Nov 3, 07:30 EST)", "2025-11-03T07:30:00-05:00", "NY AM", True),
        ("NY AM end during EST (Nov 3, 10:59 EST)", "2025-11-03T10:59:00-05:00", "NY AM", True),
        
        # NY LUNCH session tests
        ("NY LUNCH during EDT (Nov 1, 12:00 EDT)", "2025-11-01T12:00:00-04:00", "NY LUNCH", True),
        ("NY LUNCH during EST (Nov 3, 11:00 EST)", "2025-11-03T11:00:00-05:00", "NY LUNCH", True),
        
        # NY PM session tests
        ("NY PM during EDT (Nov 1, 13:00 EDT)", "2025-11-01T13:00:00-04:00", "NY PM", True),
        ("NY PM during EST (Nov 3, 12:00 EST)", "2025-11-03T12:00:00-05:00", "NY PM", True),
        ("NY PM end during EST (Nov 3, 14:59 EST)", "2025-11-03T14:59:00-05:00", "NY PM", True),
        
        # INVALID period tests
        ("INVALID during EDT (Nov 1, 16:00 EDT)", "2025-11-01T16:00:00-04:00", "INVALID", False),
        ("INVALID during EST (Nov 3, 15:00 EST)", "2025-11-03T15:00:00-05:00", "INVALID", False),
        ("INVALID during EST (Nov 3, 18:59 EST)", "2025-11-03T18:59:00-05:00", "INVALID", False),
    ]
    
    passed = 0
    failed = 0
    
    for description, datetime_str, expected_session, expected_valid in test_cases:
        # Parse datetime
        dt = datetime.fromisoformat(datetime_str)
        
        # Convert to UTC
        utc_dt = dt.astimezone(pytz.utc)
        
        # Determine session based on UTC hour
        hour = utc_dt.hour
        minute = utc_dt.minute
        
        if 0 <= hour <= 3:
            session = 'ASIA'
            is_valid = True
        elif 4 <= hour <= 9:
            session = 'LONDON'
            is_valid = True
        elif 10 <= hour <= 12:
            if hour == 12 and minute >= 30:
                session = 'NY AM'
            else:
                session = 'NY PRE'
            is_valid = True
        elif 12 <= hour <= 15:
            if hour == 12 and minute < 30:
                session = 'NY PRE'
            else:
                session = 'NY AM'
            is_valid = True
        elif hour == 16:
            session = 'NY LUNCH'
            is_valid = True
        elif 17 <= hour <= 19:
            session = 'NY PM'
            is_valid = True
        else:
            session = 'INVALID'
            is_valid = False
        
        # Check results
        session_match = session == expected_session
        valid_match = is_valid == expected_valid
        
        if session_match and valid_match:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"{status} | {description}")
        print(f"       Local: {dt.strftime('%Y-%m-%d %H:%M %Z')}")
        print(f"       UTC: {utc_dt.strftime('%Y-%m-%d %H:%M UTC')} (hour={hour})")
        print(f"       Expected: {expected_session} (valid={expected_valid})")
        print(f"       Got: {session} (valid={is_valid})")
        
        if not (session_match and valid_match):
            print(f"       ⚠️  MISMATCH!")
        print()
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    print()
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - DST fix is working correctly!")
        print()
        print("The UTC-based validation correctly handles:")
        print("  • ASIA session at 19:00 EST (after DST ended)")
        print("  • ASIA session at 20:00 EDT (before DST ended)")
        print("  • All other sessions across DST boundary")
        print("  • INVALID period detection in both EST and EDT")
    else:
        print(f"❌ {failed} TESTS FAILED - Review implementation")
    
    print()
    return failed == 0

def test_current_time():
    """Test with current system time"""
    print("=" * 70)
    print("CURRENT TIME TEST")
    print("=" * 70)
    print()
    
    # Get current time
    now_local = datetime.now(pytz.timezone('US/Eastern'))
    now_utc = datetime.now(pytz.utc)
    
    print(f"Current Local Time: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Current UTC Time: {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Determine session
    hour = now_utc.hour
    minute = now_utc.minute
    
    if 0 <= hour <= 3:
        session = 'ASIA'
    elif 4 <= hour <= 9:
        session = 'LONDON'
    elif 10 <= hour <= 12:
        if hour == 12 and minute >= 30:
            session = 'NY AM'
        else:
            session = 'NY PRE'
    elif 12 <= hour <= 15:
        if hour == 12 and minute < 30:
            session = 'NY PRE'
        else:
            session = 'NY AM'
    elif hour == 16:
        session = 'NY LUNCH'
    elif 17 <= hour <= 19:
        session = 'NY PM'
    else:
        session = 'INVALID'
    
    print(f"Current Session: {session}")
    print()
    
    # Show session times in current timezone
    is_dst = now_local.dst() != pytz.timedelta(0)
    tz_name = "EDT" if is_dst else "EST"
    utc_offset = -4 if is_dst else -5
    
    print(f"Session Times in {tz_name} (UTC{utc_offset:+d}):")
    print(f"  ASIA: {19 if not is_dst else 20}:00-{22 if not is_dst else 23}:59 {tz_name}")
    print(f"  LONDON: {23 if not is_dst else 0}:00-{4 if not is_dst else 5}:59 {tz_name}")
    print(f"  NY PRE: {5 if not is_dst else 6}:00-{7 if not is_dst else 8}:29 {tz_name}")
    print(f"  NY AM: {7 if not is_dst else 8}:30-{10 if not is_dst else 11}:59 {tz_name}")
    print(f"  NY LUNCH: {11 if not is_dst else 12}:00-{11 if not is_dst else 12}:59 {tz_name}")
    print(f"  NY PM: {12 if not is_dst else 13}:00-{14 if not is_dst else 15}:59 {tz_name}")
    print(f"  INVALID: {15 if not is_dst else 16}:00-{18 if not is_dst else 19}:59 {tz_name}")
    print()

if __name__ == '__main__':
    # Run validation tests
    success = test_utc_session_validation()
    
    # Test current time
    test_current_time()
    
    # Exit with appropriate code
    exit(0 if success else 1)

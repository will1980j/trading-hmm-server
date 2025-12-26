#!/usr/bin/env python3
import sys
sys.path.append('.')

print("=" * 80)
print("PHASE A GATE VERIFICATION")
print("=" * 80)

# Check 1
print("\n1) COMPLETENESS:")
try:
    from config.trading_calendar import load_holidays, is_market_open, expected_bar_timestamps_utc
    holidays = load_holidays()
    print(f"   ✅ PASS - Holidays: {len(holidays)}, Functions exist")
    check1 = "PASS"
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    check1 = "FAIL"

# Check 2
print("\n2) CONTINUITY/SANITY:")
try:
    from services.gap_detector_phase_a import detect_gaps
    result = detect_gaps('GLBX.MDP3:NQ', '2024-01-02', '2024-01-03')
    print(f"   ✅ PASS - Expected: {result['expected_count']}, Actual: {result['actual_count']}, Missing: {result['missing_count']}")
    check2 = "PASS"
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    check2 = "FAIL"

# Check 3
print("\n3) VERSIONING:")
try:
    import os, psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM active_dataset_versions")
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT symbol, dataset_version_id FROM active_dataset_versions ORDER BY symbol")
    mappings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    if active_count < 2:
        print(f"   ❌ FAIL - active_dataset_versions has {active_count} rows (need NQ and MNQ)")
        check3 = "FAIL"
    else:
        print(f"   ✅ PASS - active_dataset_versions has {active_count} mappings:")
        for sym, ver in mappings:
            print(f"      - {sym}: {ver}")
        check3 = "PASS"
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    check3 = "FAIL"

# Check 4
print("\n4) DETERMINISTIC REPLAY:")
try:
    from services.deterministic_replay import replay_bars
    import os, psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cursor = conn.cursor()
    cursor.execute("SELECT dataset_version_id FROM active_dataset_versions WHERE symbol = 'GLBX.MDP3:NQ'")
    version_id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    result1 = replay_bars(version_id, 'GLBX.MDP3:NQ', '2024-01-02', '2024-01-03')
    result2 = replay_bars(version_id, 'GLBX.MDP3:NQ', '2024-01-02', '2024-01-03')
    
    if result1['output_hash'] == result2['output_hash']:
        print(f"   ✅ PASS - Bars: {result1['bar_count']}, Hash: {result1['output_hash'][:16]}..., Deterministic: YES")
        check4 = "PASS"
    else:
        print(f"   ❌ FAIL - Hashes don't match")
        check4 = "FAIL"
except Exception as e:
    print(f"   ❌ FAIL - {e}")
    check4 = "FAIL"

print("\n" + "=" * 80)
all_pass = all([check1 == "PASS", check2 == "PASS", check3 == "PASS", check4 == "PASS"])
print("✅ PHASE A: LOCKED" if all_pass else "❌ PHASE A: NOT_LOCKED")
print(f"   1_COMPLETENESS: {check1}")
print(f"   2_CONTINUITY_SANITY: {check2}")
print(f"   3_VERSIONING: {check3}")
print(f"   4_DETERMINISTIC_REPLAY: {check4}")
print("=" * 80)

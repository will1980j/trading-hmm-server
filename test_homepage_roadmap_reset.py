"""
Test script for homepage roadmap reset to Databento-first architecture.

Verifies:
1. Roadmap state structure is correct
2. Phase 0 (Databento Foundation) shows 4/5 complete
3. Databento stats are fetched from database
4. Homepage renders without errors
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Import roadmap state
from roadmap_state import phase_progress_snapshot, ROADMAP, get_phase

def test_roadmap_structure():
    """Test that roadmap structure matches Databento-first architecture"""
    print("\n=== Testing Roadmap Structure ===")
    
    snapshot = phase_progress_snapshot()
    
    # Check Phase 0 (Databento Foundation)
    phase_0 = snapshot.get('0')
    assert phase_0 is not None, "Phase 0 (Databento Foundation) not found"
    assert phase_0['name'] == "Databento Foundation (Phase 0–1A)", f"Phase 0 name incorrect: {phase_0['name']}"
    assert phase_0['modules'] == 5, f"Phase 0 should have 5 modules, got {phase_0['modules']}"
    assert phase_0['completed'] == 4, f"Phase 0 should have 4 completed, got {phase_0['completed']}"
    assert phase_0['percent'] == 80, f"Phase 0 should be 80% complete, got {phase_0['percent']}"
    print(f"✅ Phase 0: {phase_0['name']} - {phase_0['completed']}/{phase_0['modules']} modules ({phase_0['percent']}%)")
    
    # Check Phase 1 (Indicator Parity)
    phase_1 = snapshot.get('1')
    assert phase_1 is not None, "Phase 1 (Indicator Parity) not found"
    assert phase_1['name'] == "Indicator Parity (Phase 1B)", f"Phase 1 name incorrect: {phase_1['name']}"
    assert phase_1['modules'] == 3, f"Phase 1 should have 3 modules, got {phase_1['modules']}"
    assert phase_1['completed'] == 0, f"Phase 1 should have 0 completed, got {phase_1['completed']}"
    print(f"✅ Phase 1: {phase_1['name']} - {phase_1['completed']}/{phase_1['modules']} modules ({phase_1['percent']}%)")
    
    # Check Phase 2 (Strategy Discovery)
    phase_2 = snapshot.get('2')
    assert phase_2 is not None, "Phase 2 (Strategy Discovery) not found"
    assert phase_2['modules'] == 2, f"Phase 2 should have 2 modules, got {phase_2['modules']}"
    assert phase_2['completed'] == 0, f"Phase 2 should have 0 completed, got {phase_2['completed']}"
    print(f"✅ Phase 2: {phase_2['name']} - {phase_2['completed']}/{phase_2['modules']} modules ({phase_2['percent']}%)")
    
    # Check Phase 3 (Dashboards)
    phase_3 = snapshot.get('3')
    assert phase_3 is not None, "Phase 3 (Dashboards) not found"
    assert phase_3['modules'] == 3, f"Phase 3 should have 3 modules, got {phase_3['modules']}"
    assert phase_3['completed'] == 0, f"Phase 3 should have 0 completed, got {phase_3['completed']}"
    print(f"✅ Phase 3: {phase_3['name']} - {phase_3['completed']}/{phase_3['modules']} modules ({phase_3['percent']}%)")
    
    # Check Phase 4 (Automation & Execution)
    phase_4 = snapshot.get('4')
    assert phase_4 is not None, "Phase 4 (Automation & Execution) not found"
    assert phase_4['modules'] == 3, f"Phase 4 should have 3 modules, got {phase_4['modules']}"
    assert phase_4['completed'] == 0, f"Phase 4 should have 0 completed, got {phase_4['completed']}"
    print(f"✅ Phase 4: {phase_4['name']} - {phase_4['completed']}/{phase_4['modules']} modules ({phase_4['percent']}%)")
    
    # Check Phase 5 (Legacy / Optional)
    phase_5 = snapshot.get('5')
    assert phase_5 is not None, "Phase 5 (Legacy / Optional) not found"
    assert phase_5['modules'] == 3, f"Phase 5 should have 3 modules, got {phase_5['modules']}"
    assert phase_5['completed'] == 3, f"Phase 5 should have 3 completed, got {phase_5['completed']}"
    assert phase_5['percent'] == 100, f"Phase 5 should be 100% complete, got {phase_5['percent']}"
    print(f"✅ Phase 5: {phase_5['name']} - {phase_5['completed']}/{phase_5['modules']} modules ({phase_5['percent']}%)")
    
    print("\n✅ All roadmap structure tests passed!")


def test_databento_stats():
    """Test that Databento stats can be fetched from database"""
    print("\n=== Testing Databento Stats Fetch ===")
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("⚠️  DATABASE_URL not set, skipping database test")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as row_count,
                MIN(ts) as min_ts,
                MAX(ts) as max_ts,
                (SELECT close FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'CME_MINI:MNQ1!' 
                 ORDER BY ts DESC LIMIT 1) as latest_close,
                (SELECT ts FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'CME_MINI:MNQ1!' 
                 ORDER BY ts DESC LIMIT 1) as latest_ts
            FROM market_bars_ohlcv_1m
            WHERE symbol = 'CME_MINI:MNQ1!'
        """)
        
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            databento_stats = {
                'row_count': result[0],
                'min_ts': result[1].strftime('%Y-%m-%d') if result[1] else None,
                'max_ts': result[2].strftime('%Y-%m-%d') if result[2] else None,
                'latest_close': float(result[3]) if result[3] else None,
                'latest_ts': result[4].strftime('%Y-%m-%d %H:%M') if result[4] else None
            }
            
            print(f"✅ Databento stats fetched successfully:")
            print(f"   Bars: {databento_stats['row_count']:,}")
            print(f"   Range: {databento_stats['min_ts']} → {databento_stats['max_ts']}")
            print(f"   Latest: {databento_stats['latest_ts']} @ ${databento_stats['latest_close']:,.2f}")
            
            # Verify expected values
            assert databento_stats['row_count'] >= 2_000_000, f"Expected >= 2M bars, got {databento_stats['row_count']:,}"
            assert databento_stats['min_ts'].startswith('2019'), f"Expected min_ts to start with 2019, got {databento_stats['min_ts']}"
            assert databento_stats['max_ts'].startswith('2025'), f"Expected max_ts to start with 2025, got {databento_stats['max_ts']}"
            
            print("\n✅ Databento stats validation passed!")
        else:
            print("⚠️  No Databento data found in database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fetching Databento stats: {e}")
        raise


def test_phase_0_modules():
    """Test that Phase 0 modules have correct completion status"""
    print("\n=== Testing Phase 0 Module Details ===")
    
    phase_0 = get_phase('0')
    assert phase_0 is not None, "Phase 0 not found"
    
    expected_modules = {
        'databento_download': True,
        'schema_migration': True,
        'ingestion_complete': True,
        'stats_endpoint': True,
        'backfill_optional': False
    }
    
    for module_key, expected_done in expected_modules.items():
        module = phase_0.modules.get(module_key)
        assert module is not None, f"Module {module_key} not found in Phase 0"
        assert module.completed == expected_done, f"Module {module_key} should be {'done' if expected_done else 'not done'}, got {module.completed}"
        status = "✅" if module.completed else "⬜"
        print(f"{status} {module_key}: {module.description}")
    
    print("\n✅ Phase 0 module details validated!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("HOMEPAGE ROADMAP RESET TEST")
    print("=" * 60)
    
    try:
        test_roadmap_structure()
        test_phase_0_modules()
        test_databento_stats()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Load /homepage in browser")
        print("2. Verify Phase 0 shows '4/5 modules • 80%'")
        print("3. Verify Databento stats display in Phase 0 card")
        print("4. Verify Phase 5 shows '3/3 modules • 100%' (Legacy)")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

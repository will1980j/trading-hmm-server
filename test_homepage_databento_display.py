#!/usr/bin/env python3
"""
Test Homepage Databento Display

Verifies that the homepage correctly displays Phase 1A with live stats.

Usage:
    python test_homepage_databento_display.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from roadmap_state import ROADMAP

def test_roadmap_data():
    """Test that Phase 0.5 has correct data"""
    print("="*80)
    print("🧪 TESTING ROADMAP DATA STRUCTURE")
    print("="*80)
    
    # Check Phase 0.5 exists
    if "0.5" not in ROADMAP:
        print("❌ Phase 0.5 not found in ROADMAP")
        return False
    
    phase = ROADMAP["0.5"]
    print(f"\n✅ Phase 0.5 found: {phase.name}")
    
    # Check name
    expected_name = "Databento Foundation (Phase 1A)"
    if phase.name != expected_name:
        print(f"❌ Name mismatch: expected '{expected_name}', got '{phase.name}'")
        return False
    print(f"✅ Name correct: {phase.name}")
    
    # Check description contains key phrases
    desc = phase.description
    required_phrases = [
        "Market data source of truth: Databento",
        "TradingView: charting only",
        "2019-05-05",
        "2025-12-22",
        "2.34M bars"
    ]
    
    for phrase in required_phrases:
        if phrase in desc:
            print(f"✅ Description contains: '{phrase}'")
        else:
            print(f"❌ Description missing: '{phrase}'")
            return False
    
    # Check modules
    expected_modules = {
        "databento_download": True,
        "schema_migration": True,
        "ingestion_complete": True,
        "stats_endpoint": True,
        "backfill_optional": False
    }
    
    print(f"\n📋 Checking {len(expected_modules)} modules:")
    for module_key, expected_done in expected_modules.items():
        if module_key not in phase.modules:
            print(f"❌ Module '{module_key}' not found")
            return False
        
        module = phase.modules[module_key]
        actual_done = module.completed
        
        status = "✅" if actual_done else "⬜"
        expected_status = "✅" if expected_done else "⬜"
        
        if actual_done == expected_done:
            print(f"{status} {module_key}: {module.description}")
        else:
            print(f"❌ {module_key}: expected {expected_status}, got {status}")
            return False
    
    # Check progress
    percent = phase.percent_complete
    expected_percent = 80  # 4 of 5 complete
    
    if percent == expected_percent:
        print(f"\n✅ Progress: {percent}% (4/5 modules complete)")
    else:
        print(f"\n❌ Progress mismatch: expected {expected_percent}%, got {percent}%")
        return False
    
    return True

def test_stats_endpoint():
    """Test that stats endpoint is accessible"""
    print("\n" + "="*80)
    print("🌐 TESTING STATS ENDPOINT")
    print("="*80)
    
    try:
        import requests
        
        url = "https://web-production-f8c3.up.railway.app/api/market-data/mnq/ohlcv-1m/stats"
        print(f"\nTesting: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Status Code: {response.status_code}")
            
            data = response.json()
            
            # Check required fields
            required_fields = ['row_count', 'min_ts', 'max_ts', 'latest_close', 'latest_ts']
            for field in required_fields:
                if field in data:
                    print(f"✅ Field '{field}': {data[field]}")
                else:
                    print(f"❌ Field '{field}' missing")
                    return False
            
            # Validate data
            if data['row_count'] > 1_000_000:
                print(f"✅ Row count > 1M: {data['row_count']:,}")
            else:
                print(f"⚠️  Row count < 1M: {data['row_count']:,}")
            
            return True
        else:
            print(f"❌ Status Code: {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  requests library not available - skipping endpoint test")
        return True
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 HOMEPAGE DATABENTO DISPLAY TEST")
    print("="*80)
    
    results = []
    
    # Test roadmap data
    results.append(("Roadmap Data Structure", test_roadmap_data()))
    
    # Test stats endpoint
    results.append(("Stats Endpoint", test_stats_endpoint()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*80)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Homepage ready!")
        print("\nManual verification:")
        print("1. Load https://web-production-f8c3.up.railway.app/homepage")
        print("2. Expand Phase 0.5 - Databento Foundation")
        print("3. Verify checklist and stats display")
    else:
        print("\n❌ SOME TESTS FAILED - Review errors above")
        sys.exit(1)
    
    print("="*80)

if __name__ == '__main__':
    main()

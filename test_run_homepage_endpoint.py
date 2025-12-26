"""
Test script for /api/debug/run-homepage endpoint

This endpoint executes the same logic as /homepage but returns JSON
with detailed stage-by-stage results, allowing deterministic debugging.
"""

import requests
import json

BASE_URL = "https://web-production-f8c3.up.railway.app"
TOKEN = "nQ-EXPORT-9f3a2c71a9e44d0c"

def test_run_homepage():
    """Test the /api/debug/run-homepage endpoint"""
    print("\n" + "=" * 60)
    print("TEST: /api/debug/run-homepage")
    print("=" * 60)
    
    headers = {"X-Auth-Token": TOKEN}
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug/run-homepage", headers=headers)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n--- EXECUTION RESULTS ---")
            print(f"Success: {data.get('success')}")
            print(f"Stage: {data.get('stage')}")
            print(f"Server Time: {data.get('server_time_utc')}")
            
            print("\n--- ROADMAP V3 ---")
            print(f"Loaded: {data.get('roadmap_v3_loaded')}")
            print(f"Phase Count: {data.get('roadmap_v3_phase_count')}")
            if data.get('roadmap_error'):
                print(f"Error: {data.get('roadmap_error')[:200]}...")
            if data.get('roadmap_v3'):
                print(f"Version: {data['roadmap_v3'].get('version')}")
            
            print("\n--- DATABENTO STATS ---")
            print(f"Loaded: {data.get('databento_stats_loaded')}")
            print(f"Row Count: {data.get('databento_row_count')}")
            if data.get('stats_error'):
                print(f"Error: {data.get('stats_error')[:200]}...")
            if data.get('databento_stats'):
                stats = data['databento_stats']
                print(f"Min TS: {stats.get('min_ts')}")
                print(f"Max TS: {stats.get('max_ts')}")
                print(f"Latest Close: {stats.get('latest_close')}")
                print(f"Latest TS: {stats.get('latest_ts')}")
            
            print("\n--- VIDEO FILE ---")
            print(f"Video: {data.get('video_file')}")
            
            if not data.get('success'):
                print("\n" + "!" * 60)
                print("FAILURE DETECTED")
                print("!" * 60)
                print(f"\nFailed at stage: {data.get('stage')}")
                print(f"\nError: {data.get('error')}")
                
                if data.get('traceback'):
                    print("\n--- FULL TRACEBACK ---")
                    print(data.get('traceback'))
                
                return False
            else:
                print("\n" + "✅" * 30)
                print("ALL STAGES COMPLETED SUCCESSFULLY")
                print("✅" * 30)
                return True
                
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auth_required():
    """Test that endpoint requires authentication"""
    print("\n" + "=" * 60)
    print("TEST: Authentication Required")
    print("=" * 60)
    
    # Test without token
    response = requests.get(f"{BASE_URL}/api/debug/run-homepage")
    print(f"\nWithout token: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Correctly returns 401 without token")
        return True
    else:
        print(f"❌ Expected 401, got {response.status_code}")
        return False


def show_powershell_command():
    """Show PowerShell command for manual testing"""
    print("\n" + "=" * 60)
    print("POWERSHELL COMMAND")
    print("=" * 60)
    print("\nInvoke-RestMethod -Method GET -Uri \"https://web-production-f8c3.up.railway.app/api/debug/run-homepage\" -Headers @{ \"X-Auth-Token\" = \"nQ-EXPORT-9f3a2c71a9e44d0c\" }")
    print("\n# Or with formatted output:")
    print("Invoke-RestMethod -Method GET -Uri \"https://web-production-f8c3.up.railway.app/api/debug/run-homepage\" -Headers @{ \"X-Auth-Token\" = \"nQ-EXPORT-9f3a2c71a9e44d0c\" } | ConvertTo-Json -Depth 10")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUN HOMEPAGE DEBUG ENDPOINT TEST")
    print("=" * 60)
    
    # Run tests
    auth_ok = test_auth_required()
    homepage_ok = test_run_homepage()
    
    # Show command
    show_powershell_command()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Auth Test: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    print(f"Homepage Test: {'✅ PASS' if homepage_ok else '❌ FAIL'}")
    
    if auth_ok and homepage_ok:
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("=" * 60)

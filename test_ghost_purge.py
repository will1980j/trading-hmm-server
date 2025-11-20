#!/usr/bin/env python3
"""
Test script for ghost trade purge endpoint
Tests the /api/automated-signals/purge-ghosts endpoint
"""

import requests
import json

# Configuration
BASE_URL = "https://web-production-cd33.up.railway.app"
PURGE_ENDPOINT = f"{BASE_URL}/api/automated-signals/purge-ghosts"

def test_ghost_purge():
    """Test the ghost trade purge endpoint"""
    
    print("=" * 60)
    print("GHOST TRADE PURGE TEST")
    print("=" * 60)
    print()
    
    # Test 1: Check endpoint exists (will fail auth, but that's expected)
    print("Test 1: Checking endpoint accessibility...")
    try:
        response = requests.post(PURGE_ENDPOINT)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("  ✅ Endpoint exists (authentication required)")
        elif response.status_code == 200:
            result = response.json()
            print(f"  ✅ Endpoint accessible")
            print(f"  Deleted: {result.get('deleted', 0)} ghost trades")
        else:
            print(f"  ⚠️  Unexpected status code: {response.status_code}")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
    
    print()
    
    # Test 2: Check response format (if authenticated)
    print("Test 2: Response format validation...")
    print("  Note: This test requires authentication")
    print("  Expected response format:")
    print("  {")
    print('    "success": true,')
    print('    "deleted": <int>,')
    print('    "criteria": {')
    print('      "trade_id_null_or_empty": true,')
    print('      "trade_id_contains_commas": true')
    print("    }")
    print("  }")
    
    print()
    
    # Test 3: Database query simulation
    print("Test 3: Ghost trade criteria...")
    print("  The endpoint will delete rows where:")
    print("    1. trade_id IS NULL")
    print("    2. trade_id = '' (empty string)")
    print("    3. trade_id LIKE '%,%' (contains commas)")
    
    print()
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print()
    print("Endpoint: /api/automated-signals/purge-ghosts")
    print("Method: POST")
    print("Auth: Required (@login_required)")
    print("Purpose: Remove malformed ghost trades")
    print()
    print("To test with authentication:")
    print("1. Log in to the dashboard in a browser")
    print("2. Open browser console")
    print("3. Run:")
    print("   fetch('/api/automated-signals/purge-ghosts', {method: 'POST'})")
    print("     .then(r => r.json())")
    print("     .then(console.log)")
    print()

if __name__ == "__main__":
    test_ghost_purge()

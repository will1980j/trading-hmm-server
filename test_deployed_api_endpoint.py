#!/usr/bin/env python3
"""
Test Deployed API Endpoint

Tests the Railway-deployed stats endpoint for Databento data.

Usage:
    python test_deployed_api_endpoint.py
"""

import requests
import json
import sys
from datetime import datetime

def test_api_endpoint():
    """Test the deployed API endpoint"""
    
    url = "https://web-production-f8c3.up.railway.app/api/market-data/mnq/ohlcv-1m/stats"
    
    print("="*80)
    print("🌐 TESTING DEPLOYED API ENDPOINT")
    print("="*80)
    print(f"\nURL: {url}\n")
    
    try:
        # Make request
        print("📡 Sending request...")
        response = requests.get(url, timeout=10)
        
        # Response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        print(f"Content Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print("\n✅ REQUEST SUCCESSFUL")
            print("-" * 80)
            
            # Parse JSON
            data = response.json()
            
            # Pretty print response
            print("\n📊 API RESPONSE:")
            print(json.dumps(data, indent=2))
            
            # Validation
            print("\n✅ VALIDATION:")
            print("-" * 80)
            
            # Check required fields
            required_fields = ['row_count', 'min_ts', 'max_ts', 'latest_close', 'latest_ts', 'symbol', 'timeframe', 'vendor']
            for field in required_fields:
                if field in data:
                    print(f"  ✅ Field '{field}' present")
                else:
                    print(f"  ❌ Field '{field}' missing")
            
            # Validate values
            print("\n📈 DATA VALIDATION:")
            print("-" * 80)
            
            row_count = data.get('row_count', 0)
            if row_count >= 1_000_000:
                print(f"  ✅ Row count >= 1M: {row_count:,}")
            elif row_count > 0:
                print(f"  ⚠️  Row count < 1M: {row_count:,}")
            else:
                print(f"  ❌ Row count is 0")
            
            min_ts = data.get('min_ts')
            if min_ts:
                min_year = int(min_ts[:4])
                if min_year <= 2011:
                    print(f"  ✅ Min timestamp is historical: {min_ts}")
                else:
                    print(f"  ⚠️  Min timestamp: {min_ts}")
            else:
                print(f"  ❌ Min timestamp missing")
            
            max_ts = data.get('max_ts')
            if max_ts:
                max_year = int(max_ts[:4])
                if max_year >= 2025:
                    print(f"  ✅ Max timestamp is recent: {max_ts}")
                else:
                    print(f"  ⚠️  Max timestamp: {max_ts}")
            else:
                print(f"  ❌ Max timestamp missing")
            
            latest_close = data.get('latest_close')
            if latest_close and latest_close > 0:
                print(f"  ✅ Latest close is valid: ${latest_close:,.2f}")
            else:
                print(f"  ❌ Latest close invalid: {latest_close}")
            
            symbol = data.get('symbol')
            if symbol == 'CME_MINI:MNQ1!':
                print(f"  ✅ Symbol correct: {symbol}")
            else:
                print(f"  ⚠️  Symbol: {symbol}")
            
            timeframe = data.get('timeframe')
            if timeframe == '1m':
                print(f"  ✅ Timeframe correct: {timeframe}")
            else:
                print(f"  ⚠️  Timeframe: {timeframe}")
            
            vendor = data.get('vendor')
            if vendor == 'databento':
                print(f"  ✅ Vendor correct: {vendor}")
            else:
                print(f"  ⚠️  Vendor: {vendor}")
            
            # Performance check
            response_time = response.elapsed.total_seconds()
            if response_time < 1.0:
                print(f"\n  ✅ Response time < 1s: {response_time:.2f}s")
            else:
                print(f"\n  ⚠️  Response time >= 1s: {response_time:.2f}s")
            
            print("\n" + "="*80)
            print("✅ API ENDPOINT TEST COMPLETE")
            print("="*80)
            
        else:
            print(f"\n❌ REQUEST FAILED")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)
            
    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out after 10 seconds")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error - check if Railway is deployed")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    test_api_endpoint()

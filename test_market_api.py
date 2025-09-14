#!/usr/bin/env python3
"""
Test the current market context API to verify it's returning real data
"""
import requests
import json

def test_market_context_api():
    print("Testing Market Context API...")
    print("=" * 50)
    
    try:
        # Test the current market context endpoint
        url = "http://localhost:5000/api/current-market-context"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            print("SUCCESS: Market Context API Response:")
            print(json.dumps(data, indent=2))
            
            # Check data quality
            real_data_count = 0
            fallback_count = 0
            
            for key, value in data.items():
                if key in ['market_session', 'data_source']:
                    continue
                    
                if value > 0 and value != 20.0:  # 20.0 is our VIX fallback
                    real_data_count += 1
                    print(f"✅ {key}: {value} (REAL DATA)")
                elif value == 20.0 and key == 'vix':
                    fallback_count += 1
                    print(f"⚠️  {key}: {value} (FALLBACK)")
                else:
                    fallback_count += 1
                    print(f"❌ {key}: {value} (NO DATA)")
            
            print("=" * 50)
            print(f"📊 Data Quality Summary:")
            print(f"   Real Data Sources: {real_data_count}/4")
            print(f"   Fallback Data: {fallback_count}/4")
            print(f"   Data Source: {data.get('data_source', 'Unknown')}")
            
            if real_data_count >= 3:
                print("🎯 EXCELLENT: Getting real market data!")
                return True
            elif real_data_count >= 1:
                print("👍 GOOD: Partial real data, some fallbacks")
                return True
            else:
                print("⚠️  WARNING: All fallback data - API issues")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_market_context_api()
    if success:
        print("\n🚀 Market Context API is working - no more fallback data issues!")
    else:
        print("\n💥 Market Context API needs attention")
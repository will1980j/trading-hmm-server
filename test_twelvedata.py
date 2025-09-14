#!/usr/bin/env python3
"""
Test TwelveData API with corrected symbols
"""
import requests
import json

def test_twelvedata_api():
    api_key = "130662f9ebe34885a16bea088b096c70"
    
    # Corrected symbols that work with TwelveData
    symbols = {
        'VXX': 'vix',           # VXX ETF as proxy for VIX volatility
        'QQQ': 'nq_price',      # QQQ ETF as proxy for NQ
        'SPY': 'spy_price',     # SPY ETF
        'UUP': 'dxy_price'      # UUP ETF as proxy for DXY
    }
    
    print("🔥 Testing TwelveData API with corrected symbols...")
    print("=" * 50)
    
    results = {}
    
    for symbol, key in symbols.items():
        try:
            url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    price = float(data['price'])
                    results[key] = price
                    print(f"✅ {symbol}: ${price:.2f}")
                else:
                    results[key] = 0
                    print(f"❌ {symbol}: No price data - {data}")
            else:
                results[key] = 0
                print(f"❌ {symbol}: HTTP {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            results[key] = 0
            print(f"❌ {symbol}: Error - {str(e)}")
    
    print("=" * 50)
    print(f"📊 Results: {len([v for v in results.values() if v > 0])}/4 symbols successful")
    print(f"📈 Market Context: {json.dumps(results, indent=2)}")
    
    # Test if we're getting real data vs fallback
    if all(v > 0 for v in results.values()):
        print("🎯 SUCCESS: All symbols returning REAL DATA!")
        print("🚀 TwelveData API is working correctly - no more fallback data!")
    else:
        failed_symbols = [k for k, v in results.items() if v == 0]
        print(f"⚠️  Some symbols failed: {failed_symbols}")
    
    return results

if __name__ == "__main__":
    test_twelvedata_api()
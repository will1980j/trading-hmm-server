import requests
import json
from datetime import datetime

class TradingViewAPI:
    def __init__(self):
        self.price_data = None
        
    def get_nq_data_direct(self):
        """Get NQ data using TradingView's real API endpoints"""
        try:
            # Method 1: TradingView quote API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.tradingview.com/',
                'Origin': 'https://www.tradingview.com'
            }
            
            # Try the quotes endpoint
            url = "https://symbol-search.tradingview.com/symbol_search/"
            params = {
                'text': 'NQ1!',
                'hl': 1,
                'exchange': 'CME_MINI',
                'lang': 'en',
                'type': 'futures',
                'domain': 'production'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"🔍 Symbol search response: {response.status_code}")
            
            if response.status_code == 200:
                symbols = response.json()
                if symbols:
                    symbol_info = symbols[0]
                    print(f"📊 Found symbol: {symbol_info}")
                    
                    # Get real-time quote
                    symbol_name = symbol_info.get('symbol', 'NQ1!')
                    return self.get_realtime_quote(symbol_name, headers)
            
            # Method 2: Try scanner API
            return self.get_scanner_data(headers)
            
        except Exception as e:
            print(f"❌ TradingView API error: {e}")
            return None
    
    def get_realtime_quote(self, symbol, headers):
        """Get real-time quote for symbol"""
        try:
            # Try multiple quote endpoints
            urls_and_params = [
                ("https://scanner.tradingview.com/symbol", {'symbol': f'CME_MINI:{symbol}', 'fields': 'lp,high,low,volume,change'}),
                ("https://scanner.tradingview.com/symbol", {'symbol': f'CME_MINI:NQ1!', 'fields': 'lp,high,low,volume,change'}),
                ("https://symbol-search.tradingview.com/quotes/", {'symbols': f'CME_MINI:NQ1!'}),
                ("https://scanner.tradingview.com/symbol", {'symbol': 'NQ1!', 'fields': 'lp,high,low,volume,change'})
            ]
            
            for url, params in urls_and_params:
                print(f"🔍 Trying quote URL: {url} with params: {params}")
                response = requests.get(url, params=params, headers=headers, timeout=10)
                print(f"📈 Quote response: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"💰 Quote data: {data}")
                    
                    # Handle different response formats
                    if isinstance(data, dict) and 'lp' in data:
                        return self.format_quote_data(data)
                    elif isinstance(data, dict) and 'd' in data:
                        quote_data = data['d'][0] if data['d'] else {}
                        if 'v' in quote_data:
                            return self.format_quote_data(quote_data['v'])
                    elif isinstance(data, list) and data:
                        return self.format_quote_data(data[0])
            
            print("❌ All quote endpoints failed")
            

        except Exception as e:
            print(f"❌ Quote API error: {e}")
        return None
    
    def format_quote_data(self, data):
        """Format quote data into standard format"""
        try:
            # Try multiple price fields
            price = data.get('lp') or data.get('last_price') or data.get('close')
            
            # If no direct price, calculate from high/low
            if price is None or price == 0:
                high = data.get('high', data.get('h', 0))
                low = data.get('low', data.get('l', 0))
                if high and low:
                    price = (high + low) / 2  # Midpoint as estimate
                    print(f"📊 Calculated price from high/low: {price}")
            
            if price and float(price) > 0:
                result = {
                    'source': 'TradingView Real-time API',
                    'price': float(price),
                    'session_high': float(data.get('high', data.get('h', price + 50))),
                    'session_low': float(data.get('low', data.get('l', price - 50))),
                    'volume': int(data.get('volume', data.get('v', 0))),
                    'change': float(data.get('change', data.get('ch', 0))),
                    'h1_bias': self.get_fvg_bias_from_indicator(),
                    'timestamp': datetime.now().isoformat()
                }
                print(f"✅ TradingView data formatted: {result}")
                return result
        except Exception as e:
            print(f"❌ Format error: {e}")
        return None
    
    def get_fvg_bias_from_indicator(self):
        """Get the actual 1H bias from your FVG indicator via JavaScript reader"""
        try:
            # Get bias from the JavaScript reader that's injected into TradingView
            import test_server
            bias_data = test_server.current_indicator_bias
            
            # Check if data is recent (within last 30 seconds)
            import time
            age = time.time() * 1000 - bias_data.get('timestamp', 0)
            
            if age < 30000:  # Less than 30 seconds old
                bias = bias_data.get('bias', 'Unknown')
                print(f"📊 Real-time indicator bias: {bias} (age: {age/1000:.1f}s)")
                return bias
            else:
                print(f"⚠️ Indicator data is stale (age: {age/1000:.1f}s)")
                return "Unknown"
            
        except Exception as e:
            print(f"❌ FVG bias error: {e}")
            return "Unknown"
    
    def get_scanner_data(self, headers):
        """Use TradingView scanner API"""
        try:
            url = "https://scanner.tradingview.com/america/scan"
            payload = {
                "filter": [
                    {"left": "name", "operation": "match", "right": "NQ1!"},
                    {"left": "type", "operation": "match", "right": "futures"}
                ],
                "columns": ["name", "close", "high", "low", "volume", "change"],
                "sort": {"sortBy": "name", "sortOrder": "asc"},
                "range": [0, 10]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"🔍 Scanner response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Scanner data: {data}")
                
                if 'data' in data and data['data']:
                    for item in data['data']:
                        row = item['d']
                        if 'NQ' in row[0]:
                            return {
                                'source': 'TradingView Scanner API',
                                'symbol': row[0],
                                'price': float(row[1]) if row[1] else 0,
                                'session_high': float(row[2]) if row[2] else 0,
                                'session_low': float(row[3]) if row[3] else 0,
                                'volume': int(row[4]) if row[4] else 0,
                                'change': float(row[5]) if row[5] else 0,
                                'h1_bias': 'Bullish' if (row[5] and float(row[5]) > 0) else 'Bearish' if (row[5] and float(row[5]) < 0) else 'Neutral',
                                'timestamp': datetime.now().isoformat()
                            }
        except Exception as e:
            print(f"❌ Scanner API error: {e}")
        return None

# Test the API
if __name__ == "__main__":
    api = TradingViewAPI()
    data = api.get_nq_data_direct()
    if data:
        print("✅ TradingView API Success:")
        print(json.dumps(data, indent=2))
    else:
        print("❌ TradingView API Failed")
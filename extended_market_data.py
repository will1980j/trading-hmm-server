import requests
import json
from datetime import datetime
from tradingview_api import TradingViewAPI

class ExtendedMarketData:
    def __init__(self):
        self.sources = [
            self.get_tradingview_data,
            self.get_cme_data,
            self.get_yahoo_data,
            self.get_investing_data,
            self.get_marketwatch_data
        ]
    
    def get_nq_data(self):
        """Try multiple sources for NQ futures data"""
        for source in self.sources:
            try:
                print(f"🔍 Trying {source.__name__}...")
                data = source()
                if data:
                    print(f"✅ Got data from {source.__name__}: {data.get('price', 'No price')}")
                    return data
                else:
                    print(f"❌ {source.__name__} returned None")
            except Exception as e:
                print(f"❌ {source.__name__} failed: {e}")
                continue
        
        print("❌ All data sources failed")
        return None
    
    def get_cme_data(self):
        """CME Group DataMine API - Official NQ futures data"""
        try:
            # CME DataMine real-time API
            # Note: This requires CME DataMine subscription for real-time data
            # Free delayed data is also available
            
            # CME Real-time API endpoint
            base_url = "https://datamine.cmegroup.com/api/v1"
            
            # For NQ futures (E-mini NASDAQ-100)
            # Contract: NQ (Globex symbol)
            symbol = "NQ"
            
            # Get current front month contract
            contracts_url = f"{base_url}/instruments"
            params = {
                'productCode': 'NQ',
                'venue': 'GLOBEX',
                'active': 'true'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            # First get active contracts
            response = requests.get(contracts_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                contracts = response.json()
                if contracts and len(contracts) > 0:
                    # Get the front month contract
                    front_contract = contracts[0]['symbol']  # e.g., 'NQZ24'
                    
                    # Get real-time market data
                    market_data_url = f"{base_url}/marketdata"
                    data_params = {
                        'symbol': front_contract,
                        'fields': 'last,high,low,volume,timestamp'
                    }
                    
                    data_response = requests.get(market_data_url, params=data_params, headers=headers, timeout=10)
                    
                    if data_response.status_code == 200:
                        market_data = data_response.json()
                        
                        if market_data and 'data' in market_data:
                            data_point = market_data['data'][0]
                            
                            return {
                                'source': 'CME DataMine (Official)',
                                'contract': front_contract,
                                'price': float(data_point.get('last', 0)),
                                'session_high': float(data_point.get('high', 0)),
                                'session_low': float(data_point.get('low', 0)),
                                'volume': int(data_point.get('volume', 0)),
                                'h1_bias': 'Neutral',
                                'timestamp': data_point.get('timestamp', datetime.now().isoformat()),
                                'exchange': 'CME Globex',
                                'official': True
                            }
            
            # Fallback to CME public delayed data
            return self.get_cme_delayed_data()
            
        except Exception as e:
            print(f"CME API error: {e}")
            return None
    
    def get_cme_delayed_data(self):
        """CME delayed data (free, 10-15 minute delay)"""
        try:
            # CME Group public delayed data feed
            url = "https://www.cmegroup.com/CmeWS/mvc/ProductSlate/V1/List"
            params = {
                'productIds': '7442',  # NQ product ID
                'venue': 'G'  # Globex
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.html'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'products' in data and len(data['products']) > 0:
                    nq_data = data['products'][0]
                    
                    if 'quotes' in nq_data and len(nq_data['quotes']) > 0:
                        quote = nq_data['quotes'][0]  # Front month
                        
                        return {
                            'source': 'CME Delayed (Official)',
                            'contract': quote.get('expirationMonth', 'NQ'),
                            'price': float(quote.get('last', 0)),
                            'session_high': float(quote.get('high', 0)),
                            'session_low': float(quote.get('low', 0)),
                            'volume': int(quote.get('volume', 0)),
                            'h1_bias': 'Neutral',
                            'timestamp': datetime.now().isoformat(),
                            'exchange': 'CME Globex',
                            'delayed': True,
                            'delay_minutes': 15
                        }
        except Exception as e:
            print(f"CME delayed data error: {e}")
            return None
    
    def get_yahoo_data(self):
        """Yahoo Finance - includes premarket/afterhours"""
        url = "https://query1.finance.yahoo.com/v8/finance/chart/NQ=F"
        params = {
            'interval': '1m',
            'range': '1d',
            'includePrePost': 'true',
            'prepost': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'chart' in data and data['chart']['result']:
            result = data['chart']['result'][0]
            indicators = result['indicators']['quote'][0]
            
            # Get latest valid data
            closes = [c for c in indicators['close'] if c is not None]
            highs = [h for h in indicators['high'] if h is not None]
            lows = [l for l in indicators['low'] if l is not None]
            
            if closes:
                return {
                    'source': 'Yahoo Finance',
                    'price': round(closes[-1], 2),
                    'session_high': round(max(highs[-60:]), 2),  # Last hour
                    'session_low': round(min(lows[-60:]), 2),
                    'h1_bias': 'Neutral',  # Will be calculated by FVG
                    'timestamp': datetime.now().isoformat()
                }
        return None
    
    def get_investing_data(self):
        """Investing.com API"""
        try:
            # Investing.com has NQ futures data
            url = "https://api.investing.com/api/financialdata/8874/historical/chart"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    latest = data['data'][-1]
                    return {
                        'source': 'Investing.com',
                        'price': float(latest.get('price', 0)),
                        'session_high': float(latest.get('high', 0)),
                        'session_low': float(latest.get('low', 0)),
                        'h1_bias': 'Neutral',
                        'timestamp': datetime.now().isoformat()
                    }
        except:
            pass
        return None
    
    def get_tradingview_data(self):
        """TradingView real-time data - API client"""
        try:
            # Use the proper API client
            api = TradingViewAPI()
            data = api.get_nq_data_direct()
            if data:
                return data
        except Exception as e:
            print(f"TradingView API failed: {e}")
        
        # Fallback to API methods
        methods = [
            self.get_tradingview_quote,
            self.get_tradingview_scanner,
            self.get_tradingview_websocket_data
        ]
        
        for method in methods:
            try:
                data = method()
                if data:
                    return data
            except Exception as e:
                print(f"TradingView method {method.__name__} failed: {e}")
                continue
        return None
    
    def get_tradingview_quote(self):
        """TradingView quote API"""
        try:
            url = "https://symbol-search.tradingview.com/symbol_search/"
            params = {
                'text': 'NQ1!',
                'hl': 1,
                'exchange': 'CME',
                'lang': 'en',
                'type': 'futures',
                'domain': 'production'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.tradingview.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    symbol_data = data[0]
                    
                    # Get real-time quote
                    quote_url = f"https://symbol-search.tradingview.com/quotes/"
                    quote_params = {
                        'symbols': f"CME:{symbol_data.get('symbol', 'NQ1!')}"
                    }
                    
                    quote_response = requests.get(quote_url, params=quote_params, headers=headers, timeout=10)
                    if quote_response.status_code == 200:
                        quote_data = quote_response.json()
                        if quote_data and 'd' in quote_data:
                            quote = quote_data['d'][0]
                            return {
                                'source': 'TradingView Quote',
                                'price': float(quote.get('v', {}).get('lp', 0)),
                                'session_high': float(quote.get('v', {}).get('h', 0)),
                                'session_low': float(quote.get('v', {}).get('l', 0)),
                                'volume': int(quote.get('v', {}).get('volume', 0)),
                                'h1_bias': 'Neutral',
                                'timestamp': datetime.now().isoformat()
                            }
        except Exception as e:
            print(f"TradingView quote error: {e}")
        return None
    
    def get_tradingview_scanner(self):
        """TradingView scanner API"""
        try:
            url = "https://scanner.tradingview.com/america/scan"
            payload = {
                "filter": [
                    {"left": "name", "operation": "match", "right": "NQ1!"},
                    {"left": "type", "operation": "match", "right": "futures"}
                ],
                "columns": ["name", "close", "high", "low", "volume", "change"],
                "sort": {"sortBy": "name", "sortOrder": "asc"},
                "range": [0, 50]
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/json',
                'Referer': 'https://www.tradingview.com/'
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    for item in data['data']:
                        if 'NQ' in item['d'][0]:  # Find NQ contract
                            row = item['d']
                            return {
                                'source': 'TradingView Scanner',
                                'symbol': row[0],
                                'price': float(row[1]) if row[1] else 0,
                                'session_high': float(row[2]) if row[2] else 0,
                                'session_low': float(row[3]) if row[3] else 0,
                                'volume': int(row[4]) if row[4] else 0,
                                'h1_bias': 'Neutral',
                                'timestamp': datetime.now().isoformat()
                            }
        except Exception as e:
            print(f"TradingView scanner error: {e}")
        return None
    
    def get_tradingview_websocket_data(self):
        """TradingView WebSocket data simulation"""
        try:
            # TradingView chart data endpoint
            url = "https://symbol-search.tradingview.com/symbol_info/"
            params = {
                'symbol': 'CME:NQ1!'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.tradingview.com/chart/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'price' in data:
                    return {
                        'source': 'TradingView WebSocket',
                        'price': float(data.get('price', 0)),
                        'session_high': float(data.get('high', 0)),
                        'session_low': float(data.get('low', 0)),
                        'h1_bias': 'Neutral',
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"TradingView websocket error: {e}")
        return None
    
    def get_marketwatch_data(self):
        """MarketWatch data"""
        try:
            url = "https://api.wsj.com/api/michelangelo/timeseries/history"
            params = {
                'json': '{"Step":"PT1M","TimeFrame":"P1D","EntitlementToken":"cecc4267a0194af89ca343805a3e57af","ckey":"cecc4267a0","instruments":[{"symbol":"FUTURES/US/NMX/NQ/MAIN","series":[{"key":"CLOSE"}]}]}'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'TimeseriesData' in data:
                    series = data['TimeseriesData'][0]['Series'][0]['DataPoints']
                    if series:
                        latest = series[-1]
                        recent_data = series[-60:]  # Last hour
                        highs = [p['Value'] for p in recent_data if p['Value']]
                        lows = [p['Value'] for p in recent_data if p['Value']]
                        
                        return {
                            'source': 'MarketWatch',
                            'price': round(latest['Value'], 2),
                            'session_high': round(max(highs), 2),
                            'session_low': round(min(lows), 2),
                            'h1_bias': 'Neutral',
                            'timestamp': datetime.now().isoformat()
                        }
        except:
            pass
        return None
    
    def get_market_hours_status(self):
        """Check if markets are in regular/extended hours"""
        now = datetime.now()
        hour = now.hour
        
        # NQ futures trading hours (nearly 24/7 except weekends)
        if 0 <= hour <= 4:  # Sunday night / Monday morning
            return "EXTENDED_HOURS"
        elif 4 <= hour <= 17:  # Regular session
            return "REGULAR_HOURS"
        else:  # After hours
            return "EXTENDED_HOURS"

# Test the extended data
if __name__ == "__main__":
    provider = ExtendedMarketData()
    data = provider.get_nq_data()
    if data:
        print("Extended Market Data:", json.dumps(data, indent=2))
        print("Market Status:", provider.get_market_hours_status())
    else:
        print("No data available from any source")
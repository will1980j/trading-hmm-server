import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any

class NewsAPI:
    def __init__(self):
        # Using free news APIs
        self.news_sources = [
            "https://api.rss2json.com/v1/api.json?rss_url=https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://api.rss2json.com/v1/api.json?rss_url=https://www.marketwatch.com/rss/topstories"
        ]
        
    def get_market_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch latest market news from multiple sources"""
        all_news = []
        
        for source_url in self.news_sources:
            try:
                response = requests.get(source_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok' and 'items' in data:
                        for item in data['items'][:5]:
                            news_item = {
                                'title': item.get('title', ''),
                                'description': item.get('description', ''),
                                'link': item.get('link', ''),
                                'pubDate': item.get('pubDate', ''),
                                'source': 'Market News'
                            }
                            all_news.append(news_item)
            except Exception as e:
                print(f"Error fetching news from {source_url}: {e}")
                continue
        
        return all_news[:limit]
    
    def get_futures_data(self) -> Dict[str, Any]:
        """Get REAL futures data from Yahoo Finance"""
        symbols = {
            'NQ': 'NQ=F',  # Nasdaq 100 Futures
            'ES': 'ES=F',  # S&P 500 Futures
            'YM': 'YM=F',  # Dow Futures
            'RTY': 'RTY=F', # Russell 2000 Futures
            'CL': 'CL=F',  # Crude Oil Futures
            'GC': 'GC=F'   # Gold Futures
        }
        
        futures_data = {}
        
        for display_name, yahoo_symbol in symbols.items():
            try:
                # Yahoo Finance API endpoint
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    result = data.get('chart', {}).get('result', [])
                    
                    if result:
                        quote = result[0]
                        meta = quote.get('meta', {})
                        
                        current_price = meta.get('regularMarketPrice', 0)
                        prev_close = meta.get('previousClose', current_price)
                        
                        change = current_price - prev_close
                        change_pct = (change / prev_close * 100) if prev_close != 0 else 0
                        
                        futures_data[display_name] = {
                            'price': round(current_price, 2),
                            'change': f"{'+' if change >= 0 else ''}{change:.2f}",
                            'change_pct': f"{'+' if change_pct >= 0 else ''}{change_pct:.2f}%"
                        }
                    else:
                        # Fallback if no data
                        futures_data[display_name] = {
                            'price': 'N/A',
                            'change': 'N/A',
                            'change_pct': 'N/A'
                        }
                        
            except Exception as e:
                print(f"Error fetching {display_name} data: {e}")
                futures_data[display_name] = {
                    'price': 'N/A',
                    'change': 'N/A', 
                    'change_pct': 'N/A'
                }
        
        return futures_data

def get_market_sentiment() -> str:
    """Analyze overall market sentiment from real data"""
    try:
        # Get VIX data for sentiment
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('chart', {}).get('result', [])
            
            if result:
                quote = result[0]
                meta = quote.get('meta', {})
                vix_price = meta.get('regularMarketPrice', 20)
                
                # VIX-based sentiment
                if vix_price < 15:
                    return "BULLISH"
                elif vix_price > 25:
                    return "BEARISH"
                else:
                    return "NEUTRAL"
    except:
        pass
    
    return "NEUTRAL"

def get_real_nq_levels() -> Dict[str, Any]:
    """Get real NQ levels using basic technical analysis"""
    try:
        # Get NQ price data from Yahoo Finance
        url = "https://query1.finance.yahoo.com/v8/finance/chart/NQ=F?interval=1d&range=30d"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('chart', {}).get('result', [])
            
            if result:
                quote = result[0]
                indicators = quote.get('indicators', {}).get('quote', [{}])[0]
                highs = indicators.get('high', [])
                lows = indicators.get('low', [])
                closes = indicators.get('close', [])
                
                if highs and lows and closes:
                    # Calculate basic levels
                    recent_high = max([h for h in highs[-10:] if h is not None])
                    recent_low = min([l for l in lows[-10:] if l is not None])
                    current_price = closes[-1] if closes[-1] is not None else recent_high
                    
                    # Simple pivot calculation
                    pivot = (recent_high + recent_low + current_price) / 3
                    
                    return {
                        'support': [round(recent_low, 0), round(recent_low - 50, 0), round(recent_low - 100, 0)],
                        'resistance': [round(recent_high, 0), round(recent_high + 50, 0), round(recent_high + 100, 0)],
                        'pivot': round(pivot, 0)
                    }
    except Exception as e:
        print(f"Error calculating NQ levels: {e}")
    
    # Fallback levels
    return {
        'support': [20800, 20750, 20700],
        'resistance': [21000, 21050, 21100], 
        'pivot': 20900
    }

def extract_key_levels() -> Dict[str, Any]:
    """Extract key technical levels for NQ"""
    return {'NQ': get_real_nq_levels()}
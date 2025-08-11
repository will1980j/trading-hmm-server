import requests
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any

class NewsAPI:
    def __init__(self):
        # Using free news APIs - no API key required for basic functionality
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
                        for item in data['items'][:5]:  # Get 5 from each source
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
        
        # Sort by date and return limited results
        return all_news[:limit]
    
    def get_futures_data(self) -> Dict[str, Any]:
        """Get basic futures data - simplified for demo"""
        # In production, you'd use a real futures API
        return {
            'NQ': {'price': 15234.50, 'change': '+12.25', 'change_pct': '+0.08%'},
            'ES': {'price': 4567.75, 'change': '+8.50', 'change_pct': '+0.19%'},
            'YM': {'price': 34567.25, 'change': '+45.75', 'change_pct': '+0.13%'},
            'RTY': {'price': 1987.50, 'change': '-3.25', 'change_pct': '-0.16%'},
            'CL': {'price': 78.45, 'change': '+1.23', 'change_pct': '+1.59%'},
            'GC': {'price': 1987.60, 'change': '-5.40', 'change_pct': '-0.27%'}
        }

def get_market_sentiment() -> str:
    """Analyze overall market sentiment"""
    # Simplified sentiment analysis
    return "BULLISH"  # In production, this would analyze news sentiment

def extract_key_levels() -> Dict[str, List[float]]:
    """Extract key technical levels for NQ"""
    # In production, this would use technical analysis
    return {
        'NQ': {
            'support': [15200, 15150, 15100],
            'resistance': [15300, 15350, 15400],
            'pivot': 15250
        }
    }
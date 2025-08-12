import requests
import json
import re
from datetime import datetime

def get_tradingview_nq_data():
    """Direct scrape of TradingView NQ data"""
    try:
        print("🔍 TradingView scraper starting...")
        # Use generic NQ futures chart URL
        url = "https://www.tradingview.com/chart/?symbol=CME_MINI%3ANQ1%21"
        print(f"📡 Requesting chart: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        print(f"📊 Response status: {response.status_code}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"📡 Requesting: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Extract price data from the HTML - Enhanced patterns
            price_patterns = [
                r'"lp":(\d+\.?\d*)',  # Last price
                r'"price":(\d+\.?\d*)',  # Price
                r'"close":(\d+\.?\d*)',  # Close
                r'data-symbol-last="(\d+\.?\d*)"',  # Symbol last
                r'class="tv-symbol-price-quote__value[^"]*">([0-9,]+\.?[0-9]*)',  # Price display
                r'"last_price":(\d+\.?\d*)',  # Last price JSON
                r'"regularMarketPrice":(\d+\.?\d*)',  # Regular market price
                r'data-field="last_price"[^>]*>([0-9,]+\.?[0-9]*)',  # Data field
                r'<span[^>]*data-field="last"[^>]*>([0-9,]+\.?[0-9]*)',  # Span with last
                r'"last":(\d+\.?\d*)',  # Simple last
                r'NQ1![^}]*"lp":(\d+\.?\d*)',  # NQ1! specific
                r'CME_MINI:NQ1![^}]*"lp":(\d+\.?\d*)'  # CME_MINI specific
            ]
            
            high_patterns = [
                r'"h":(\d+\.?\d*)',  # High
                r'"high":(\d+\.?\d*)',  # High
                r'data-field="high"[^>]*>([0-9,]+\.?[0-9]*)'
            ]
            
            low_patterns = [
                r'"l":(\d+\.?\d*)',  # Low
                r'"low":(\d+\.?\d*)',  # Low
                r'data-field="low"[^>]*>([0-9,]+\.?[0-9]*)'
            ]
            
            # Try to extract price
            price = None
            for pattern in price_patterns:
                match = re.search(pattern, html_content)
                if match:
                    price = float(match.group(1).replace(',', ''))
                    break
            
            # Try to extract high
            high = None
            for pattern in high_patterns:
                match = re.search(pattern, html_content)
                if match:
                    high = float(match.group(1).replace(',', ''))
                    break
            
            # Try to extract low
            low = None
            for pattern in low_patterns:
                match = re.search(pattern, html_content)
                if match:
                    low = float(match.group(1).replace(',', ''))
                    break
            
            print(f"💰 Extracted - Price: {price}, High: {high}, Low: {low}")
            
            if price:
                result = {
                    'source': 'TradingView Scraper',
                    'price': price,
                    'session_high': high or price + 50,
                    'session_low': low or price - 50,
                    'h1_bias': 'Neutral',
                    'timestamp': datetime.now().isoformat(),
                    'scraped': True
                }
                print(f"✅ TradingView scraper success: {result}")
                return result
            else:
                print("❌ No price found in HTML")
                # Save HTML to debug
                with open('tradingview_debug.html', 'w', encoding='utf-8') as f:
                    f.write(html_content[:5000])  # First 5000 chars
                print("💾 Saved HTML sample to tradingview_debug.html for analysis")
        
        print("🔄 Trying TradingView API fallback...")
        # Fallback: Try TradingView API endpoints
        return get_tradingview_api_data()
        
    except Exception as e:
        print(f"❌ TradingView scraper error: {e}")
        return None

def get_tradingview_api_data():
    """TradingView API fallback"""
    try:
        # Try the real-time quote endpoint
        url = "https://scanner.tradingview.com/symbol"
        params = {
            'symbol': 'CMENQ1!',
            'fields': 'last_price,high,low,volume,change'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.tradingview.com/'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and 'last_price' in data:
                return {
                    'source': 'TradingView API',
                    'price': float(data['last_price']),
                    'session_high': float(data.get('high', data['last_price'] + 50)),
                    'session_low': float(data.get('low', data['last_price'] - 50)),
                    'volume': int(data.get('volume', 0)),
                    'h1_bias': 'Neutral',
                    'timestamp': datetime.now().isoformat()
                }
    
    except Exception as e:
        print(f"TradingView API fallback error: {e}")
    
    return None

# Test the scraper
if __name__ == "__main__":
    data = get_tradingview_nq_data()
    if data:
        print("TradingView NQ Data:", json.dumps(data, indent=2))
    else:
        print("Failed to get TradingView data")
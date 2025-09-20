import requests
import json
import logging

logger = logging.getLogger(__name__)

def scrape_qqq_volume():
    """Get QQQ volume using stock-web-scraper approach"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Use Yahoo Finance query API
        url = 'https://query1.finance.yahoo.com/v8/finance/chart/QQQ'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Yahoo API returned status {response.status_code}")
            return None
            
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
            result = data['chart']['result'][0]
            if 'meta' in result and 'regularMarketVolume' in result['meta']:
                volume = result['meta']['regularMarketVolume']
                return int(volume)
        
        logger.warning("Could not find QQQ volume in Yahoo API response")
        return None
        
    except Exception as e:
        logger.error(f"Error getting QQQ volume: {str(e)}")
        return None
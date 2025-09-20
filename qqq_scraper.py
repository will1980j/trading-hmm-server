import requests
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

def scrape_qqq_volume():
    """Scrape QQQ volume from MarketWatch"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get('https://www.marketwatch.com/investing/fund/qqq', headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"MarketWatch returned status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for volume in various patterns
        volume_patterns = [
            r'Volume[^>]*>([^<]*)',
            r'data-module="Volume"[^>]*>.*?<span[^>]*>([^<]*)',
            r'Volume.*?([0-9,]+\.?[0-9]*[KMB]?)',
            r'([0-9,]+\.?[0-9]*[KMB]?).*?Volume'
        ]
        
        for pattern in volume_patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            for match in matches:
                # Clean and parse volume
                volume_str = match.strip().replace(',', '')
                if 'M' in volume_str:
                    volume = float(volume_str.replace('M', '')) * 1000000
                    return int(volume)
                elif 'K' in volume_str:
                    volume = float(volume_str.replace('K', '')) * 1000
                    return int(volume)
                elif volume_str.replace('.', '').isdigit():
                    return int(float(volume_str))
        
        logger.warning("Could not find QQQ volume in MarketWatch response")
        return None
        
    except Exception as e:
        logger.error(f"Error scraping QQQ volume: {str(e)}")
        return None
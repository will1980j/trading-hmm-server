import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Your actual webhook.site URLs
DIVERGENCE_WEBHOOKS = {
    'DXY_BEARISH_NQ_LONG': 'https://webhook.site/d984f203-aa83-4266-8822-e8415c44061a',
    'DXY_BULLISH_NQ_SHORT': 'https://webhook.site/3da6b446-0f7b-426c-b40f-264e6ddb1b3f', 
    'ES_BULLISH_NQ_LONG': 'https://webhook.site/f353ae43-b2c4-4013-aed1-19ded3593cd2',
    'ES_BEARISH_NQ_SHORT': 'https://webhook.site/9130a450-403d-4871-ba09-b9c395a046b1',
    'YM_BULLISH_NQ_LONG': 'https://webhook.site/c6f100a7-9faa-4657-8251-6ce9d9403a34',
    'YM_BEARISH_NQ_SHORT': 'https://webhook.site/f3fd178e-c1d5-4332-a6fb-866abd5f1f18'
}

def detect_divergence_opportunities(signal):
    """Detect divergence opportunities and send alerts to TradingView"""
    alerts = []
    
    try:
        symbol = signal.get('symbol', '')
        bias = signal.get('bias', '')
        
        # DXY Inverse Correlation Divergences
        if 'DXY' in symbol:
            if bias == 'Bearish':
                alerts.append({
                    'webhook_url': DIVERGENCE_WEBHOOKS['DXY_BEARISH_NQ_LONG'],
                    'message': 'NQ_DIVERGENCE_LONG_DXY_BEARISH',
                    'type': 'DXY_BEARISH_NQ_LONG'
                })
            elif bias == 'Bullish':
                alerts.append({
                    'webhook_url': DIVERGENCE_WEBHOOKS['DXY_BULLISH_NQ_SHORT'],
                    'message': 'NQ_DIVERGENCE_SHORT_DXY_BULLISH',
                    'type': 'DXY_BULLISH_NQ_SHORT'
                })
        
        # ES Positive Correlation Divergences
        elif 'ES' in symbol:
            if bias == 'Bullish':
                alerts.append({
                    'webhook_url': DIVERGENCE_WEBHOOKS['ES_BULLISH_NQ_LONG'],
                    'message': 'NQ_DIVERGENCE_LONG_ES_BULLISH',
                    'type': 'ES_BULLISH_NQ_LONG'
                })
            elif bias == 'Bearish':
                alerts.append({
                    'webhook_url': DIVERGENCE_WEBHOOKS['ES_BEARISH_NQ_SHORT'],
                    'message': 'NQ_DIVERGENCE_SHORT_ES_BEARISH',
                    'type': 'ES_BEARISH_NQ_SHORT'
                })
        
        # YM Positive Correlation Divergences  
        elif 'YM' in symbol:
            if bias == 'Bullish':
                alerts.append({
                    'webhook_url': DIVERGENCE_WEBHOOKS['YM_BULLISH_NQ_LONG'],
                    'message': 'NQ_DIVERGENCE_LONG_YM_BULLISH',
                    'type': 'YM_BULLISH_NQ_LONG'
                })
            elif bias == 'Bearish':
                alerts.append({
                    'webhook_url': DIVERGENCE_WEBHOOKS['YM_BEARISH_NQ_SHORT'],
                    'message': 'NQ_DIVERGENCE_SHORT_YM_BEARISH',
                    'type': 'YM_BEARISH_NQ_SHORT'
                })
        
        return alerts
        
    except Exception as e:
        logger.error(f"Error detecting divergences: {str(e)}")
        return []

def send_divergence_alert(alert):
    """Send divergence alert to TradingView webhook"""
    try:
        response = requests.post(
            alert['webhook_url'], 
            data=alert['message'], 
            timeout=5,
            headers={'Content-Type': 'text/plain'}
        )
        
        if response.status_code == 200:
            logger.info(f"Divergence alert sent: {alert['type']}")
            return True
        else:
            logger.error(f"Failed to send alert: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending divergence alert: {str(e)}")
        return False
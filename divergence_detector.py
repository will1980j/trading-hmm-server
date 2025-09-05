import requests
from logging import getLogger
from datetime import datetime
import pytz

logger = getLogger(__name__)

# Your actual TradingView webhook URLs for divergence alerts
DIVERGENCE_WEBHOOKS = {
    'DXY_BEARISH_NQ_LONG': 'https://webhook.site/d984f203-aa83-4266-8822-e8415c44061a',
    'DXY_BULLISH_NQ_SHORT': 'https://webhook.site/3da6b446-0f7b-426c-b40f-264e6ddb1b3f', 
    'ES_BEARISH_NQ_SHORT': 'https://webhook.site/f353ae43-b2c4-4013-aed1-19ded3593cd2',
    'ES_BULLISH_NQ_LONG': 'https://webhook.site/9130a450-403d-4871-ba09-b9c395a046b1',
    'YM_BEARISH_NQ_SHORT': 'https://webhook.site/c6f100a7-9faa-4657-8251-6ce9d9403a34',
    'YM_BULLISH_NQ_LONG': 'https://webhook.site/f3fd178e-c1d5-4332-a6fb-866abd5f1f18'
}

def detect_divergence_opportunities(signal):
    """Detect NQ divergence opportunities from correlated symbol signals"""
    divergences = []
    
    symbol = signal.get('symbol', '')
    bias = signal.get('bias', '')
    
    # DXY inverse correlation with NQ
    if symbol == 'DXY':
        if bias == 'Bearish':
            divergences.append({
                'type': 'DXY_BEARISH_NQ_LONG',
                'message': f"DXY Bearish at {signal.get('price', 0)} → NQ Long Opportunity",
                'nq_direction': 'LONG',
                'strength': signal.get('strength', 50) + 15
            })
        elif bias == 'Bullish':
            divergences.append({
                'type': 'DXY_BULLISH_NQ_SHORT', 
                'message': f"DXY Bullish at {signal.get('price', 0)} → NQ Short Opportunity",
                'nq_direction': 'SHORT',
                'strength': signal.get('strength', 50) + 15
            })
    
    # ES positive correlation with NQ (divergence when opposite)
    elif symbol == 'ES1!':
        if bias == 'Bearish':
            divergences.append({
                'type': 'ES_BEARISH_NQ_SHORT',
                'message': f"ES Bearish at {signal.get('price', 0)} → NQ Short Alignment", 
                'nq_direction': 'SHORT',
                'strength': signal.get('strength', 50) + 10
            })
        elif bias == 'Bullish':
            divergences.append({
                'type': 'ES_BULLISH_NQ_LONG',
                'message': f"ES Bullish at {signal.get('price', 0)} → NQ Long Alignment",
                'nq_direction': 'LONG', 
                'strength': signal.get('strength', 50) + 10
            })
    
    # YM positive correlation with NQ (divergence when opposite)
    elif symbol == 'YM1!':
        if bias == 'Bearish':
            divergences.append({
                'type': 'YM_BEARISH_NQ_SHORT',
                'message': f"YM Bearish at {signal.get('price', 0)} → NQ Short Alignment",
                'nq_direction': 'SHORT',
                'strength': signal.get('strength', 50) + 10
            })
        elif bias == 'Bullish':
            divergences.append({
                'type': 'YM_BULLISH_NQ_LONG', 
                'message': f"YM Bullish at {signal.get('price', 0)} → NQ Long Alignment",
                'nq_direction': 'LONG',
                'strength': signal.get('strength', 50) + 10
            })
    
    return divergences

def send_divergence_alert(alert):
    """Send divergence alert to TradingView via webhook"""
    try:
        webhook_url = DIVERGENCE_WEBHOOKS.get(alert['type'])
        if not webhook_url:
            logger.error(f"No webhook URL configured for {alert['type']}")
            return False
        
        payload = {
            'type': alert['type'],
            'message': alert['message'],
            'nq_direction': alert['nq_direction'],
            'strength': alert['strength'],
            'timestamp': datetime.now(pytz.timezone('America/New_York')).isoformat()
        }
        
        response = requests.post(webhook_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            logger.info(f"✅ Divergence alert sent: {alert['type']}")
            return True
        else:
            logger.error(f"❌ Webhook failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending divergence alert: {str(e)}")
        return False
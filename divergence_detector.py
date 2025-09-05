import requests
from logging import getLogger
from datetime import datetime
import pytz

logger = getLogger(__name__)

# Use your existing 6 webhook URLs from divergence_detector.py
DIVERGENCE_WEBHOOKS = {
    'DXY_BEARISH_NQ_LONG': 'https://webhook.site/dxy-bearish-nq-long',
    'DXY_BULLISH_NQ_SHORT': 'https://webhook.site/dxy-bullish-nq-short', 
    'ES_BEARISH_NQ_SHORT': 'https://webhook.site/es-bearish-nq-short',
    'ES_BULLISH_NQ_LONG': 'https://webhook.site/es-bullish-nq-long',
    'YM_BEARISH_NQ_SHORT': 'https://webhook.site/ym-bearish-nq-short',
    'YM_BULLISH_NQ_LONG': 'https://webhook.site/ym-bullish-nq-long'
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
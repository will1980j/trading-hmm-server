def detect_divergence_opportunities(signal):
    """Detect divergence opportunities for NQ based on correlated symbols"""
    alerts = []
    symbol = signal['symbol']
    bias = signal['bias']
    
    # DXY Divergences (inverse correlation with NQ)
    if 'DXY' in symbol:
        if bias == 'Bearish':
            alerts.append({
                'type': 'DXY_BEARISH_NQ_LONG',
                'webhook_url': 'https://webhook.site/DXY_BEARISH_ALERT',  # Replace with actual URL
                'message': 'DXY_BEARISH_DIVERGENCE'
            })
        elif bias == 'Bullish':
            alerts.append({
                'type': 'DXY_BULLISH_NQ_SHORT', 
                'webhook_url': 'https://webhook.site/DXY_BULLISH_ALERT',  # Replace with actual URL
                'message': 'DXY_BULLISH_DIVERGENCE'
            })
    
    # ES Divergences (positive correlation with NQ)
    elif 'ES' in symbol:
        if bias == 'Bullish':
            alerts.append({
                'type': 'ES_BULLISH_NQ_LONG',
                'webhook_url': 'https://webhook.site/ES_BULLISH_ALERT',  # Replace with actual URL
                'message': 'ES_BULLISH_DIVERGENCE'
            })
        elif bias == 'Bearish':
            alerts.append({
                'type': 'ES_BEARISH_NQ_SHORT',
                'webhook_url': 'https://webhook.site/ES_BEARISH_ALERT',  # Replace with actual URL
                'message': 'ES_BEARISH_DIVERGENCE'
            })
    
    # YM Divergences (positive correlation with NQ)
    elif 'YM' in symbol:
        if bias == 'Bullish':
            alerts.append({
                'type': 'YM_BULLISH_NQ_LONG',
                'webhook_url': 'https://webhook.site/YM_BULLISH_ALERT',  # Replace with actual URL
                'message': 'YM_BULLISH_DIVERGENCE'
            })
        elif bias == 'Bearish':
            alerts.append({
                'type': 'YM_BEARISH_NQ_SHORT',
                'webhook_url': 'https://webhook.site/YM_BEARISH_ALERT',  # Replace with actual URL
                'message': 'YM_BEARISH_DIVERGENCE'
            })
    
    return alerts
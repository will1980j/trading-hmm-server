from datetime import datetime, timedelta

class DivergenceDetector:
    def __init__(self):
        self.correlation_rules = {
            'NQ1!': {'positive': ['ES1!', 'YM1!'], 'negative': ['DXY']},
            'ES1!': {'positive': ['YM1!', 'NQ1!'], 'negative': ['DXY']},
            'YM1!': {'positive': ['ES1!', 'NQ1!'], 'negative': ['DXY']}, 
            'DXY': {'negative': ['ES1!', 'YM1!', 'NQ1!']}
        }
    
    def analyze_divergences(self, recent_signals):
        """Detect institutional divergences - when correlations break down"""
        divergences = []
        
        # Group by symbol and get latest triangle bias
        symbol_bias = {}
        for signal in recent_signals:
            symbol = signal['symbol']
            if symbol not in symbol_bias or signal['timestamp'] > symbol_bias[symbol]['timestamp']:
                symbol_bias[symbol] = {
                    'bias': signal['bias'],
                    'timestamp': signal['timestamp'],
                    'strength': signal['strength']
                }
        
        # Check for institutional divergences
        institutional_alerts = []
        
        # Positive correlations breaking down (NQ/ES/YM should move together)
        indices = ['NQ1!', 'ES1!', 'YM1!']
        index_biases = {sym: symbol_bias.get(sym, {}).get('bias') for sym in indices}
        active_indices = {k: v for k, v in index_biases.items() if v}
        
        if len(active_indices) >= 2:
            biases = list(active_indices.values())
            if not all(b == biases[0] for b in biases):
                # Indices showing different triangle directions = institutional divergence
                divergences.append({
                    'type': 'INSTITUTIONAL_DIVERGENCE',
                    'message': f"🚨 INDICES DIVERGING: {', '.join([f'{k}={v}' for k, v in active_indices.items()])}",
                    'significance': 'HIGH',
                    'interpretation': 'Institutional money may be repositioning'
                })
        
        # Negative correlation alignment (DXY vs Indices should be opposite)
        if 'DXY' in symbol_bias:
            dxy_bias = symbol_bias['DXY']['bias']
            for index in indices:
                if index in symbol_bias:
                    index_bias = symbol_bias[index]['bias']
                    if dxy_bias == index_bias:
                        # DXY and indices moving same direction = institutional divergence
                        divergences.append({
                            'type': 'INSTITUTIONAL_DIVERGENCE',
                            'message': f"🚨 DXY & {index} BOTH {dxy_bias}: Institutional flow detected",
                            'significance': 'HIGH',
                            'interpretation': 'Major institutional positioning change'
                        })
        
        return divergences
    


# Global detector instance
divergence_detector = DivergenceDetector()
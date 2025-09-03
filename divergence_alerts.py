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
        """Analyze signals for regular and hidden divergences"""
        divergences = []
        
        # Group signals by symbol
        symbol_signals = {}
        for signal in recent_signals:
            symbol = signal['symbol']
            if symbol not in symbol_signals:
                symbol_signals[symbol] = []
            symbol_signals[symbol].append(signal)
        
        # Check each symbol against its correlations
        for symbol, correlations in self.correlation_rules.items():
            if symbol not in symbol_signals:
                continue
                
            symbol_bias = self._get_dominant_bias(symbol_signals[symbol])
            symbol_strength = self._get_avg_strength(symbol_signals[symbol])
            
            # Check positive correlations (should move together)
            for corr_symbol in correlations.get('positive', []):
                if corr_symbol in symbol_signals:
                    corr_bias = self._get_dominant_bias(symbol_signals[corr_symbol])
                    corr_strength = self._get_avg_strength(symbol_signals[corr_symbol])
                    
                    # Regular divergence - opposite bias
                    if symbol_bias != corr_bias:
                        divergences.append({
                            'type': 'REGULAR_DIVERGENCE',
                            'symbols': [symbol, corr_symbol],
                            'message': f"🔴 {symbol} {symbol_bias} vs {corr_symbol} {corr_bias}",
                            'strength': abs(symbol_strength - corr_strength),
                            'correlation': 'positive'
                        })
                    
                    # Hidden divergence - same bias, different strength
                    elif abs(symbol_strength - corr_strength) > 25:
                        stronger = symbol if symbol_strength > corr_strength else corr_symbol
                        weaker = corr_symbol if symbol_strength > corr_strength else symbol
                        
                        divergences.append({
                            'type': 'HIDDEN_DIVERGENCE', 
                            'symbols': [symbol, corr_symbol],
                            'message': f"🟡 {stronger} strong, {weaker} weak ({symbol_bias})",
                            'strength': abs(symbol_strength - corr_strength),
                            'correlation': 'positive'
                        })
            
            # Check negative correlations (should move opposite)
            for corr_symbol in correlations.get('negative', []):
                if corr_symbol in symbol_signals:
                    corr_bias = self._get_dominant_bias(symbol_signals[corr_symbol])
                    corr_strength = self._get_avg_strength(symbol_signals[corr_symbol])
                    
                    # Regular divergence - same bias (should be opposite)
                    if symbol_bias == corr_bias:
                        divergences.append({
                            'type': 'REGULAR_DIVERGENCE',
                            'symbols': [symbol, corr_symbol],
                            'message': f"🔴 {symbol} & {corr_symbol} both {symbol_bias} (should be opposite)",
                            'strength': (symbol_strength + corr_strength) / 2,
                            'correlation': 'negative'
                        })
        
        return sorted(divergences, key=lambda x: x['strength'], reverse=True)
    
    def _get_dominant_bias(self, signals):
        """Get the dominant bias from recent signals"""
        if not signals:
            return None
            
        bullish = sum(1 for s in signals if s['bias'] == 'Bullish')
        bearish = sum(1 for s in signals if s['bias'] == 'Bearish')
        
        return 'Bullish' if bullish > bearish else 'Bearish'
    
    def _get_avg_strength(self, signals):
        """Get average strength from recent signals"""
        if not signals:
            return 0
            
        return sum(s['strength'] for s in signals) / len(signals)

# Global detector instance
divergence_detector = DivergenceDetector()
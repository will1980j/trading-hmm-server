import requests
import json
from datetime import datetime, timedelta
from fvg_bias import FVGBiasCalculator

class MarketDataProvider:
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.fvg_calculator = FVGBiasCalculator()
        
    def get_nq_data(self):
        """Get current NQ futures data"""
        try:
            # NQ futures symbol
            symbol = "NQ=F"
            url = f"{self.base_url}/{symbol}"
            
            params = {
                'interval': '1m',
                'range': '1d',
                'includePrePost': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                indicators = result['indicators']['quote'][0]
                timestamps = result['timestamp']
                
                # Get latest data
                latest_idx = -1
                current_price = indicators['close'][latest_idx]
                high = max(indicators['high'][-20:])  # 20-period high
                low = min(indicators['low'][-20:])    # 20-period low
                volume = sum(indicators['volume'][-5:]) / 5  # 5-period avg volume
                
                # Calculate simple momentum
                if len(indicators['close']) >= 10:
                    momentum = (current_price - indicators['close'][-10]) / indicators['close'][-10] * 100
                else:
                    momentum = 0
                
                return {
                    'symbol': 'NQ1!',
                    'price': round(current_price, 2),
                    'high_20': round(high, 2),
                    'low_20': round(low, 2),
                    'momentum_10': round(momentum, 2),
                    'avg_volume': int(volume) if volume else 0,
                    'timestamp': datetime.now().isoformat(),
                    'session_high': round(high, 2),
                    'session_low': round(low, 2)
                }
                
        except Exception as e:
            print(f"Market data error: {e}")
            return None
    
    def get_market_structure(self, price_data):
        """Analyze market structure for ICT concepts"""
        if not price_data:
            return {}
            
        current_price = price_data['price']
        session_high = price_data['session_high']
        session_low = price_data['session_low']
        momentum = price_data.get('momentum_10', 0)
        
        # Simple market structure analysis
        structure = {
            'trend': 'BULLISH' if momentum > 0.5 else 'BEARISH' if momentum < -0.5 else 'RANGING',
            'position_in_range': ((current_price - session_low) / (session_high - session_low)) * 100 if session_high != session_low else 50,
            'near_highs': abs(current_price - session_high) < (session_high - session_low) * 0.1,
            'near_lows': abs(current_price - session_low) < (session_high - session_low) * 0.1,
            'momentum_strength': 'STRONG' if abs(momentum) > 1 else 'MODERATE' if abs(momentum) > 0.3 else 'WEAK',
            'h1_bias': price_data.get('h1_bias', 'Neutral'),
            'sweep_potential_high': abs(current_price - session_high) < (session_high - session_low) * 0.05 if session_high != session_low else False,
            'sweep_potential_low': abs(current_price - session_low) < (session_high - session_low) * 0.05 if session_high != session_low else False
        }
        
        return structure
    
    def get_session_analysis(self, session):
        """Get session-specific analysis"""
        session_data = {
            'LONDON': {
                'liquidity': 'HIGH',
                'typical_range': '40-80 points',
                'bias_tendency': 'TREND_FOLLOWING',
                'optimal_for': 'Breakouts and momentum'
            },
            'NEW YORK AM': {
                'liquidity': 'VERY HIGH', 
                'typical_range': '60-120 points',
                'bias_tendency': 'DIRECTIONAL',
                'optimal_for': 'Major moves and reversals'
            },
            'NEW YORK PM': {
                'liquidity': 'MODERATE',
                'typical_range': '20-50 points', 
                'bias_tendency': 'MEAN_REVERSION',
                'optimal_for': 'Range trading and scalping'
            },
            'ASIA': {
                'liquidity': 'LOW',
                'typical_range': '15-40 points',
                'bias_tendency': 'CONSOLIDATION', 
                'optimal_for': 'Range bound strategies'
            }
        }
        
        return session_data.get(session, session_data['ASIA'])

# Test the market data
if __name__ == "__main__":
    provider = MarketDataProvider()
    data = provider.get_nq_data()
    if data:
        print("Market Data:", json.dumps(data, indent=2))
        structure = provider.get_market_structure(data)
        print("Market Structure:", json.dumps(structure, indent=2))
    else:
        print("Failed to get market data")
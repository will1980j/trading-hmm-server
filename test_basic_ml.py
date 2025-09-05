#!/usr/bin/env python3
"""
Test basic ML engine to see if it produces real analysis
"""

from ml_engine import get_ml_engine, analyze_signal_with_ml
from datetime import datetime, timedelta
import numpy as np

def test_basic_ml():
    """Test basic ML with real market data"""
    
    print("🤖 TESTING BASIC ML ENGINE")
    print("=" * 50)
    
    # Create realistic market data
    base_price = 20150.0
    market_data = []
    
    for i in range(100):
        # Simulate realistic price movement
        price_change = np.random.normal(0, 5)  # Random walk with volatility
        base_price += price_change
        
        market_data.append({
            'price': base_price,
            'volume': np.random.randint(800, 1500),
            'timestamp': (datetime.now() - timedelta(minutes=100-i)).isoformat()
        })
    
    # Test signal
    test_signal = {
        'symbol': 'NQ1!',
        'bias': 'Bullish',
        'price': base_price,
        'strength': 75,
        'htf_aligned': True,
        'signal_type': 'FVG',
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"📊 Market data: {len(market_data)} price points")
    print(f"   Price range: {min(d['price'] for d in market_data):.2f} - {max(d['price'] for d in market_data):.2f}")
    
    try:
        # Test ML analysis
        enhanced_signal = analyze_signal_with_ml(test_signal, market_data)
        
        print(f"\n🎯 ML ANALYSIS RESULTS:")
        print(f"   Original strength: {test_signal['strength']}%")
        print(f"   Enhanced strength: {enhanced_signal.get('strength', 0)}%")
        print(f"   ML Direction: {enhanced_signal.get('ml_direction', 'N/A')}")
        print(f"   ML Confidence: {enhanced_signal.get('ml_confidence', 0):.1f}%")
        print(f"   Risk Score: {enhanced_signal.get('ml_risk_score', 0):.1f}")
        print(f"   Market Regime: {enhanced_signal.get('market_regime', 'N/A')}")
        print(f"   Features Count: {enhanced_signal.get('ml_features_count', 0)}")
        
        # Test feature engineering directly
        engine = get_ml_engine()
        features = engine.engineer_features(test_signal, market_data)
        
        print(f"\n📈 FEATURE ENGINEERING:")
        print(f"   Total features: {len(features)}")
        print(f"   Non-zero features: {sum(1 for f in features if abs(f) > 0.001)}")
        print(f"   Feature sample: {features[:10]}")
        
        # Check if analysis is meaningful
        meaningful_score = 0
        if enhanced_signal.get('ml_confidence', 0) > 0: meaningful_score += 1
        if enhanced_signal.get('strength', 0) != test_signal['strength']: meaningful_score += 1
        if enhanced_signal.get('ml_direction', 'N/A') != 'NEUTRAL': meaningful_score += 1
        if sum(1 for f in features if abs(f) > 0.001) > 20: meaningful_score += 1
        if enhanced_signal.get('market_regime', 'UNKNOWN') != 'UNKNOWN': meaningful_score += 1
        
        print(f"\n📊 MEANINGFUL ANALYSIS SCORE: {meaningful_score}/5")
        
        if meaningful_score >= 3:
            print("   ✅ ML IS PRODUCING MEANINGFUL ANALYSIS")
            return True
        else:
            print("   ❌ ML IS MOSTLY PLACEHOLDER DATA")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ML: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_ml()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Basic ML produces meaningful analysis")
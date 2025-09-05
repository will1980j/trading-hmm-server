#!/usr/bin/env python3
"""
Test script to verify institutional ML is working with real data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from institutional_ml_engine import get_institutional_engine
from datetime import datetime
import json

def test_institutional_ml():
    """Test institutional ML with sample signal"""
    
    print("🏛️ TESTING INSTITUTIONAL ML ENGINE")
    print("=" * 50)
    
    # Sample signal data
    test_signal = {
        'symbol': 'NQ1!',
        'bias': 'Bullish',
        'price': 20150.25,
        'strength': 75,
        'htf_aligned': True,
        'timestamp': datetime.now().isoformat()
    }
    
    # Sample market data
    test_market_data = [
        {'price': 20150.25, 'volume': 1000, 'timestamp': datetime.now().isoformat()},
        {'price': 20148.50, 'volume': 1200, 'timestamp': datetime.now().isoformat()},
        {'price': 20152.75, 'volume': 800, 'timestamp': datetime.now().isoformat()}
    ]
    
    try:
        # Get institutional engine
        engine = get_institutional_engine()
        
        print(f"✅ Engine initialized: {type(engine).__name__}")
        
        # Test feature engineering
        features = engine.engineer_institutional_features(test_signal, test_market_data)
        print(f"✅ Features engineered: {len(features)} features")
        print(f"   Feature sample: {features[:10]}")
        print(f"   Non-zero features: {sum(1 for f in features if f != 0.0)}")
        
        # Test prediction
        prediction = engine.predict_institutional(test_signal, test_market_data)
        
        print(f"\n🎯 INSTITUTIONAL PREDICTION:")
        print(f"   Direction: {prediction.direction}")
        print(f"   Confidence: {prediction.confidence:.2f}%")
        print(f"   Expected Return: {prediction.expected_return:.4f}")
        print(f"   Sharpe Ratio: {prediction.sharpe_ratio:.4f}")
        print(f"   Kelly Fraction: {prediction.kelly_fraction:.4f}")
        print(f"   VaR 95%: {prediction.var_95:.4f}")
        print(f"   Model Uncertainty: {prediction.model_uncertainty:.4f}")
        print(f"   Liquidity Score: {prediction.liquidity_score:.4f}")
        
        # Check if it's real data or placeholders
        real_data_score = 0
        if prediction.confidence > 0: real_data_score += 1
        if prediction.expected_return != 0: real_data_score += 1
        if prediction.sharpe_ratio != 0: real_data_score += 1
        if prediction.kelly_fraction > 0: real_data_score += 1
        if sum(1 for f in features if f != 0.0) > 10: real_data_score += 1
        
        print(f"\n📊 REAL DATA ASSESSMENT:")
        print(f"   Real data score: {real_data_score}/5")
        
        if real_data_score >= 3:
            print("   ✅ APPEARS TO BE REAL IMPLEMENTATION")
        else:
            print("   ❌ APPEARS TO BE PLACEHOLDER DATA")
            
        return real_data_score >= 3
        
    except Exception as e:
        print(f"❌ Error testing institutional ML: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_institutional_ml()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Institutional ML test")
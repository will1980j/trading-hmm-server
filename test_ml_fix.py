#!/usr/bin/env python3
"""
Direct test of ML endpoints to identify the real problem
"""

import os
import sys
sys.path.append('.')

def test_database_connection():
    """Test if database connection works"""
    try:
        from database.railway_db import RailwayDB
        db = RailwayDB()
        print("[OK] Database connection: SUCCESS")
        return db
    except Exception as e:
        print(f"[FAIL] Database connection: FAILED - {str(e)}")
        return None

def test_ml_engine_import():
    """Test if ML engine can be imported"""
    try:
        from advanced_ml_engine import get_advanced_ml_engine
        print("[OK] ML engine import: SUCCESS")
        return True
    except Exception as e:
        print(f"[FAIL] ML engine import: FAILED - {str(e)}")
        return False

def test_ml_engine_initialization(db):
    """Test if ML engine can be initialized"""
    try:
        from advanced_ml_engine import get_advanced_ml_engine
        ml_engine = get_advanced_ml_engine(db)
        print("[OK] ML engine initialization: SUCCESS")
        return ml_engine
    except Exception as e:
        print(f"[FAIL] ML engine initialization: FAILED - {str(e)}")
        return None

def test_ml_training(ml_engine):
    """Test if ML training works"""
    try:
        result = ml_engine.train_models()
        print(f"[OK] ML training: {result}")
        return result
    except Exception as e:
        print(f"[FAIL] ML training: FAILED - {str(e)}")
        return None

def test_ml_prediction(ml_engine):
    """Test if ML prediction works"""
    try:
        market_context = {
            'vix': 20.0,
            'spy_volume': 50000000,
            'dxy_price': 103.5,
            'nq_price': 15000
        }
        signal_data = {
            'bias': 'Bullish',
            'session': 'London',
            'price': 15000
        }
        result = ml_engine.predict_signal_quality(market_context, signal_data)
        print(f"[OK] ML prediction: {result}")
        return result
    except Exception as e:
        print(f"[FAIL] ML prediction: FAILED - {str(e)}")
        return None

if __name__ == "__main__":
    print("TESTING ML SYSTEM COMPONENTS...")
    print("=" * 50)
    
    # Test database
    db = test_database_connection()
    
    # Test ML engine import
    ml_import_ok = test_ml_engine_import()
    
    if db and ml_import_ok:
        # Test ML engine initialization
        ml_engine = test_ml_engine_initialization(db)
        
        if ml_engine:
            # Test training
            training_result = test_ml_training(ml_engine)
            
            # Test prediction
            prediction_result = test_ml_prediction(ml_engine)
    
    print("=" * 50)
    print("TEST COMPLETE")
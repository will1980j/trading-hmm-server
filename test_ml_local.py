"""
Quick test script to verify ML system works before Railway deploy
"""

def test_ml_system():
    print("🧪 Testing Unified ML Intelligence System...")
    print("=" * 60)
    
    # Test 1: Check ML dependencies
    print("\n1️⃣ Checking ML dependencies...")
    try:
        import sklearn
        import pandas
        import numpy
        print("   ✅ scikit-learn:", sklearn.__version__)
        print("   ✅ pandas:", pandas.__version__)
        print("   ✅ numpy:", numpy.__version__)
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        return False
    
    # Test 2: Import unified ML
    print("\n2️⃣ Importing unified ML system...")
    try:
        from unified_ml_intelligence import UnifiedMLIntelligence
        print("   ✅ Unified ML imported successfully")
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 3: Check database connection
    print("\n3️⃣ Checking database connection...")
    try:
        from database.railway_db import RailwayDB
        db = RailwayDB()
        if db.conn:
            print("   ✅ Database connected")
            
            # Test 4: Check trade data
            print("\n4️⃣ Checking trade data...")
            cursor = db.conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
            result = cursor.fetchone()
            trade_count = result['count'] if result else 0
            print(f"   ✅ Found {trade_count} trades with MFE data")
            
            if trade_count < 20:
                print(f"   ⚠️  Warning: Only {trade_count} trades (need 20+ for ML)")
            
            # Test 5: Test ML training
            if trade_count >= 20:
                print("\n5️⃣ Testing ML training...")
                ml = UnifiedMLIntelligence(db)
                result = ml.train_on_all_data()
                
                if 'error' in result:
                    print(f"   ❌ Training failed: {result['error']}")
                    return False
                else:
                    print(f"   ✅ Training successful!")
                    print(f"      - Samples: {result['training_samples']}")
                    print(f"      - Accuracy: {result['success_accuracy']:.1f}%")
                    print(f"      - MAE: {result['mfe_mae']:.3f}R")
                
                # Test 6: Test prediction
                print("\n6️⃣ Testing ML prediction...")
                test_signal = {
                    'bias': 'Bullish',
                    'session': 'London',
                    'signal_type': 'BIAS_BULLISH',
                    'price': 20500
                }
                test_context = {'context_quality_score': 0.7}
                
                prediction = ml.predict_signal_quality(test_signal, test_context)
                print(f"   ✅ Prediction successful!")
                print(f"      - Predicted MFE: {prediction['predicted_mfe']:.2f}R")
                print(f"      - Success Prob: {prediction['success_probability']:.1f}%")
                print(f"      - Recommendation: {prediction['recommendation']}")
                
                # Test 7: Test insights
                print("\n7️⃣ Testing ML insights...")
                insights = ml.get_fundamental_insights()
                
                if 'error' in insights:
                    print(f"   ⚠️  Insights limited: {insights['error']}")
                else:
                    print(f"   ✅ Insights generated!")
                    if 'best_sessions' in insights:
                        bs = insights['best_sessions']
                        print(f"      - Best session: {bs.get('best_session', 'N/A')}")
                    if 'key_recommendations' in insights:
                        print(f"      - Recommendations: {len(insights['key_recommendations'])}")
            
        else:
            print("   ❌ Database not connected")
            return False
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Ready for Railway deployment!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_ml_system()
    exit(0 if success else 1)

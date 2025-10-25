#!/usr/bin/env python3
"""
🔍 TEST PRODUCTION ML STATUS
Check if ML is actually trained on Railway production
"""

import requests
import json

def test_production_ml():
    print("🔍 TESTING PRODUCTION ML STATUS")
    print("=" * 50)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # 1. Test ML diagnostic endpoint
    print("\n🤖 Step 1: Checking ML Diagnostic")
    try:
        response = requests.get(f"{base_url}/api/ml-diagnostic", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ ML Available: {data.get('ml_available', 'unknown')}")
                print(f"✅ Database: {data.get('database', 'unknown')}")
                print(f"✅ Models: {data.get('models', 'unknown')}")
            except:
                print("❌ Response not JSON")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 2. Test ML prediction endpoint
    print("\n🎯 Step 2: Testing ML Prediction")
    try:
        test_signal = {
            "symbol": "NQ",
            "bias": "bullish",
            "session": "NY AM",
            "signal_type": "breakout",
            "timestamp": "2024-01-15T10:30:00"
        }
        
        response = requests.post(
            f"{base_url}/api/ml-predict", 
            json=test_signal,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                prediction = response.json()
                print(f"🎯 Confidence: {prediction.get('confidence', 0)}")
                print(f"📈 Predicted MFE: {prediction.get('predicted_mfe', 0)}")
                print(f"🎲 Success Probability: {prediction.get('success_probability', 0)}")
                print(f"💡 Recommendation: {prediction.get('recommendation', 'none')}")
                
                if prediction.get('confidence', 0) > 0:
                    print("✅ ML IS TRAINED AND WORKING!")
                else:
                    print("❌ ML not trained or insufficient data")
                    
            except:
                print("❌ Response not JSON")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # 3. Test prediction accuracy endpoint
    print("\n📊 Step 3: Checking Prediction Accuracy Data")
    try:
        response = requests.get(f"{base_url}/api/prediction-accuracy", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                predictions = data.get('predictions', [])
                print(f"📈 Total Predictions: {len(predictions)}")
                
                if len(predictions) > 0:
                    print("✅ PREDICTION ACCURACY DATA EXISTS!")
                    for i, pred in enumerate(predictions[:3]):
                        print(f"   {i+1}. {pred.get('symbol')} {pred.get('bias')} - Confidence: {pred.get('confidence')}%")
                else:
                    print("❌ No prediction accuracy data found")
                    
            except Exception as e:
                print(f"❌ JSON parse error: {e}")
                print("Response might be HTML (login page)")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_production_ml()
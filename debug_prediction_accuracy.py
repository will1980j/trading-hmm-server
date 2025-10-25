#!/usr/bin/env python3
"""
Debug Prediction Accuracy System
Check if the prediction accuracy system is working properly
"""

import requests
import json
from datetime import datetime

def debug_prediction_accuracy():
    """Debug the prediction accuracy system"""
    
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Debugging Prediction Accuracy System")
    print("=" * 50)
    
    # Test 1: Check if the API endpoint exists
    print("\n📡 Test 1: Checking API endpoint")
    try:
        response = requests.get(f"{base_url}/api/prediction-accuracy", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response received: {json.dumps(data, indent=2)}")
        elif response.status_code == 500:
            error_data = response.json()
            print(f"Server Error: {error_data.get('error', 'Unknown error')}")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {response.text}")
    
    # Test 2: Check recent signals to see if ML predictions are being made
    print(f"\n📊 Test 2: Checking recent signals for ML predictions")
    try:
        # This endpoint might not exist, but let's try
        response = requests.get(f"{base_url}/api/recent-signals", timeout=10)
        if response.status_code == 200:
            signals = response.json()
            print(f"Recent signals found: {len(signals)}")
            
            ml_signals = [s for s in signals if 'ml_prediction' in s and s['ml_prediction']]
            print(f"Signals with ML predictions: {len(ml_signals)}")
            
            if ml_signals:
                latest = ml_signals[0]
                print(f"Latest ML prediction: {latest.get('ml_prediction', {})}")
        else:
            print(f"Recent signals endpoint not available: {response.status_code}")
    except Exception as e:
        print(f"Error checking recent signals: {e}")
    
    # Test 3: Send a test signal to see if prediction tracking works
    print(f"\n🧪 Test 3: Sending test signal")
    try:
        test_signal = f"SIGNAL:Bullish:20500.00:85:ALIGNED:ALIGNED:{datetime.now().isoformat()}"
        
        response = requests.post(
            f"{base_url}/api/live-signals",
            data=test_signal,
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Signal processed successfully")
            print(f"Signal ID: {result.get('signal_id')}")
            print(f"ML Prediction: {result.get('ml_prediction', {})}")
            
            # Check if prediction was tracked
            if 'prediction_id' in result:
                print(f"Prediction ID: {result['prediction_id']}")
            else:
                print("⚠️ No prediction ID returned - tracking may not be working")
        else:
            print(f"Signal processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error sending test signal: {e}")

if __name__ == "__main__":
    debug_prediction_accuracy()
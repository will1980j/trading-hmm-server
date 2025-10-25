#!/usr/bin/env python3
"""
Check ML Model Status and Training Data
"""

import requests
import json

def check_ml_status():
    """Check the ML model status and available training data"""
    
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🤖 Checking ML Model Status")
    print("=" * 40)
    
    # Check ML insights
    print("\n📊 ML Model Status:")
    try:
        response = requests.get(f"{base_url}/api/ml-insights", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"ML Status: {json.dumps(data, indent=2)}")
        else:
            print(f"ML insights not available: {response.status_code}")
    except Exception as e:
        print(f"Error checking ML status: {e}")
    
    # Check signal lab trades (training data)
    print(f"\n📈 Training Data Status:")
    try:
        response = requests.get(f"{base_url}/api/signal-lab-trades", timeout=10)
        if response.status_code == 200:
            trades = response.json()
            print(f"Total signal lab trades: {len(trades)}")
            
            # Check for MFE data
            trades_with_mfe = [t for t in trades if t.get('mfe_none') is not None]
            print(f"Trades with MFE data: {len(trades_with_mfe)}")
            
            if len(trades_with_mfe) >= 30:
                print("✅ Sufficient training data available (30+ trades with MFE)")
            else:
                print(f"⚠️ Insufficient training data ({len(trades_with_mfe)}/30 trades with MFE)")
                
        else:
            print(f"Signal lab trades not available: {response.status_code}")
    except Exception as e:
        print(f"Error checking training data: {e}")
    
    # Try to trigger ML training
    print(f"\n🚀 Attempting to trigger ML training:")
    try:
        response = requests.post(f"{base_url}/api/train-ml-models", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"Training result: {json.dumps(result, indent=2)}")
        else:
            print(f"Training failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error triggering training: {e}")

if __name__ == "__main__":
    check_ml_status()
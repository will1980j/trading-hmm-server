#!/usr/bin/env python3
"""
Simple WebSocket Test
Quick test to verify WebSocket functionality
"""

import requests
import json
from datetime import datetime

def test_simple_webhook():
    """Send a simple test signal to verify WebSocket broadcasting"""
    
    webhook_url = 'http://localhost:5000/api/live-signals'
    
    # Simple test signal
    test_signal = f"SIGNAL:Bullish:20500.00:85:ALIGNED:ALIGNED:{datetime.now().isoformat()}"
    
    print("🧪 Testing WebSocket Integration")
    print(f"📊 Sending test signal: Bullish NQ at 20500.00")
    
    try:
        response = requests.post(
            webhook_url,
            data=test_signal,
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Signal processed successfully!")
            print(f"   Signal ID: {result.get('signal_id')}")
            print(f"   Status: {result.get('status')}")
            
            if result.get('ml_prediction'):
                ml_pred = result['ml_prediction']
                print(f"   ML Confidence: {ml_pred.get('confidence', 'N/A')}%")
                print(f"   Prediction: {ml_pred.get('prediction', 'N/A')}")
            
            print(f"\n🚀 WebSocket broadcast sent to connected clients")
            print(f"   Check ML Dashboard for real-time updates")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Simple WebSocket Test")
    print("Make sure your server is running and ML Dashboard is open")
    
    input("Press Enter to send test signal...")
    test_simple_webhook()
    
    print("\n✅ Test complete!")
    print("Check the ML Dashboard - you should see the signal update instantly!")
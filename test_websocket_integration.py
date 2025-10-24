#!/usr/bin/env python3
"""
Test WebSocket Integration
Tests the real-time signal broadcasting functionality
"""

import requests
import time
import json
from datetime import datetime

def test_webhook_with_websocket():
    """Test webhook endpoint and verify WebSocket broadcasting"""
    
    # Test signal data
    test_signals = [
        {
            'bias': 'Bullish',
            'price': 20500.00,
            'symbol': 'NQ1!',
            'strength': 75
        },
        {
            'bias': 'Bearish', 
            'price': 20480.00,
            'symbol': 'NQ1!',
            'strength': 82
        }
    ]
    
    webhook_url = 'http://localhost:5000/api/live-signals'
    
    print("🧪 Testing WebSocket Integration")
    print("=" * 50)
    
    for i, signal in enumerate(test_signals, 1):
        print(f"\n📊 Test Signal {i}: {signal['bias']} at {signal['price']}")
        
        # Create test signal in TradingView format
        test_signal = f"SIGNAL:{signal['bias']}:{signal['price']}:{signal['strength']}:ALIGNED:ALIGNED:{datetime.now().isoformat()}"
        
        try:
            # Send webhook
            response = requests.post(
                webhook_url,
                data=test_signal,
                headers={'Content-Type': 'text/plain'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Webhook processed successfully")
                print(f"   Signal ID: {result.get('signal_id')}")
                print(f"   ML Prediction: {result.get('ml_prediction', {}).get('confidence', 'N/A')}% confidence")
                print(f"   WebSocket broadcast should be active")
            else:
                print(f"❌ Webhook failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error sending webhook: {e}")
        
        # Wait between signals
        if i < len(test_signals):
            print("   Waiting 3 seconds...")
            time.sleep(3)
    
    print("\n" + "=" * 50)
    print("🚀 WebSocket Integration Test Complete")
    print("\nTo verify WebSocket functionality:")
    print("1. Open ML Dashboard: http://localhost:5000/ml-dashboard")
    print("2. Check browser console for WebSocket connection logs")
    print("3. Watch for real-time signal updates in the dashboard")
    print("4. Verify connection status shows 'Connected - Real-time updates active'")

def test_websocket_endpoints():
    """Test WebSocket-related API endpoints"""
    
    base_url = 'http://localhost:5000'
    endpoints = [
        '/api/webhook-stats',
        '/api/webhook-health', 
        '/api/ml-feature-importance'
    ]
    
    print("\n🔍 Testing WebSocket-related endpoints")
    print("-" * 40)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

if __name__ == "__main__":
    print("🚀 WebSocket Integration Test Suite")
    print("Make sure your Flask server is running on localhost:5000")
    
    input("Press Enter to start testing...")
    
    test_webhook_with_websocket()
    test_websocket_endpoints()
    
    print("\n✅ Testing complete!")
    print("Check the ML Dashboard to see real-time updates in action.")
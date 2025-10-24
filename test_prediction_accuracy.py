#!/usr/bin/env python3
"""
Test Prediction Accuracy Tracking System
Tests the complete prediction tracking workflow
"""

import requests
import time
import json
from datetime import datetime

def test_prediction_tracking_workflow():
    """Test the complete prediction tracking workflow"""
    
    base_url = 'http://localhost:5000'
    
    print("🧪 Testing Prediction Accuracy Tracking System")
    print("=" * 60)
    
    # Step 1: Send a signal to generate a prediction
    print("\n📊 Step 1: Sending test signal to generate ML prediction")
    
    test_signal = f"SIGNAL:Bullish:20500.00:85:ALIGNED:ALIGNED:{datetime.now().isoformat()}"
    
    try:
        response = requests.post(
            f"{base_url}/api/live-signals",
            data=test_signal,
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            signal_id = result.get('signal_id')
            ml_prediction = result.get('ml_prediction', {})
            
            print(f"✅ Signal processed: ID {signal_id}")
            print(f"   ML Prediction: {ml_prediction.get('prediction', 'N/A')}")
            print(f"   Confidence: {ml_prediction.get('confidence', 'N/A')}%")
            print(f"   Predicted MFE: {ml_prediction.get('predicted_mfe', 'N/A')}R")
            
            # Step 2: Check prediction accuracy data
            print(f"\n📈 Step 2: Checking prediction accuracy data")
            
            time.sleep(2)  # Wait for processing
            
            accuracy_response = requests.get(f"{base_url}/api/prediction-accuracy")
            if accuracy_response.status_code == 200:
                accuracy_data = accuracy_response.json()
                stats = accuracy_data.get('summary', {})
                
                print(f"✅ Accuracy data loaded:")
                print(f"   Total predictions: {stats.get('total_predictions', 0)}")
                print(f"   Completed predictions: {stats.get('completed_predictions', 0)}")
                print(f"   Overall accuracy: {stats.get('overall_accuracy', 0):.1f}%")
                print(f"   Active predictions: {accuracy_data.get('active_predictions', 0)}")
                
                # Step 3: Simulate trade completion
                print(f"\n✅ Step 3: Simulating trade completion")
                
                # Simulate a successful trade outcome
                outcome_data = {
                    'signal_id': signal_id,
                    'outcome': 'Success',
                    'mfe': 1.5,  # 1.5R profit
                    'targets_hit': {
                        '1R': True,
                        '2R': False,
                        '3R': False
                    }
                }
                
                outcome_response = requests.post(
                    f"{base_url}/api/update-prediction-outcome",
                    json=outcome_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if outcome_response.status_code == 200:
                    print(f"✅ Prediction outcome updated successfully")
                    print(f"   Outcome: Success (1.5R)")
                    print(f"   Targets hit: 1R only")
                    
                    # Step 4: Verify updated accuracy
                    print(f"\n📊 Step 4: Verifying updated accuracy statistics")
                    
                    time.sleep(2)  # Wait for processing
                    
                    updated_accuracy = requests.get(f"{base_url}/api/prediction-accuracy")
                    if updated_accuracy.status_code == 200:
                        updated_data = updated_accuracy.json()
                        updated_stats = updated_data.get('summary', {})
                        
                        print(f"✅ Updated accuracy statistics:")
                        print(f"   Completed predictions: {updated_stats.get('completed_predictions', 0)}")
                        print(f"   Overall accuracy: {updated_stats.get('overall_accuracy', 0):.1f}%")
                        
                        # Check recent outcomes
                        recent_outcomes = updated_data.get('completed_predictions', [])
                        if recent_outcomes:
                            latest = recent_outcomes[-1]
                            print(f"   Latest outcome: {latest.get('predicted')} → {latest.get('actual')} ({'✅' if latest.get('correct') else '❌'})")
                        
                    else:
                        print(f"❌ Failed to get updated accuracy: {updated_accuracy.status_code}")
                        
                else:
                    print(f"❌ Failed to update outcome: {outcome_response.status_code}")
                    print(f"   Response: {outcome_response.text}")
                    
            else:
                print(f"❌ Failed to get accuracy data: {accuracy_response.status_code}")
                
        else:
            print(f"❌ Signal processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error in workflow test: {e}")

def test_pending_predictions():
    """Test pending predictions endpoint"""
    
    print(f"\n🔍 Testing Pending Predictions")
    print("-" * 40)
    
    try:
        response = requests.get('http://localhost:5000/api/pending-predictions')
        
        if response.status_code == 200:
            data = response.json()
            pending = data.get('pending_predictions', [])
            
            print(f"✅ Pending predictions: {len(pending)}")
            
            for pred in pending[:3]:  # Show first 3
                print(f"   - {pred.get('symbol')} {pred.get('bias')} ({pred.get('confidence')}% confidence)")
                
        else:
            print(f"❌ Failed to get pending predictions: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting pending predictions: {e}")

def test_stale_prediction_cleanup():
    """Test stale prediction cleanup"""
    
    print(f"\n🧹 Testing Stale Prediction Cleanup")
    print("-" * 40)
    
    try:
        response = requests.post('http://localhost:5000/api/force-update-stale-predictions')
        
        if response.status_code == 200:
            data = response.json()
            updated_count = data.get('updated_count', 0)
            
            print(f"✅ Stale predictions updated: {updated_count}")
            
        else:
            print(f"❌ Failed to update stale predictions: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error updating stale predictions: {e}")

def test_accuracy_endpoints():
    """Test all accuracy-related endpoints"""
    
    print(f"\n🔗 Testing All Accuracy Endpoints")
    print("-" * 40)
    
    endpoints = [
        '/api/prediction-accuracy',
        '/api/pending-predictions'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

if __name__ == "__main__":
    print("🚀 Prediction Accuracy Tracking Test Suite")
    print("Make sure your Flask server is running on localhost:5000")
    print("This will test the complete prediction tracking workflow")
    
    input("Press Enter to start testing...")
    
    # Run comprehensive workflow test
    test_prediction_tracking_workflow()
    
    # Test additional endpoints
    test_pending_predictions()
    test_stale_prediction_cleanup()
    test_accuracy_endpoints()
    
    print("\n" + "=" * 60)
    print("🎯 Prediction Accuracy Tracking Test Complete!")
    print("\nWhat was tested:")
    print("✅ Signal → ML Prediction → Tracking")
    print("✅ Outcome Update → Accuracy Calculation")
    print("✅ Real-time Statistics Updates")
    print("✅ Pending Predictions Monitoring")
    print("✅ Stale Prediction Cleanup")
    print("\nCheck the ML Dashboard to see real-time accuracy tracking!")
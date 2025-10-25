#!/usr/bin/env python3
"""
Simple test of prediction accuracy endpoint
"""

import requests

def test_prediction_accuracy_endpoint():
    """Test the prediction accuracy endpoint directly"""
    
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Testing Prediction Accuracy Endpoint")
    print("=" * 45)
    
    try:
        response = requests.get(f"{base_url}/api/prediction-accuracy", timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content-Length: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ JSON Response received:")
                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                if isinstance(data, dict):
                    if 'error' in data:
                        print(f"❌ API Error: {data['error']}")
                    else:
                        summary = data.get('summary', {})
                        print(f"Total predictions: {summary.get('total_predictions', 0)}")
                        print(f"Completed predictions: {summary.get('completed_predictions', 0)}")
                        print(f"Overall accuracy: {summary.get('overall_accuracy', 0)}%")
                        
                        active = data.get('active_predictions', [])
                        completed = data.get('completed_predictions', [])
                        print(f"Active predictions: {len(active)}")
                        print(f"Completed predictions: {len(completed)}")
                        
            except Exception as json_error:
                print(f"❌ JSON Parse Error: {json_error}")
                print(f"Raw response (first 200 chars): {response.text[:200]}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")

if __name__ == "__main__":
    test_prediction_accuracy_endpoint()
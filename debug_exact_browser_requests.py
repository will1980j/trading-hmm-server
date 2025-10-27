#!/usr/bin/env python3

import requests
import time

def debug_exact_browser_requests():
    """Debug by making the exact same requests the browser is making"""
    base_url = 'https://web-production-cd33.up.railway.app'
    
    print("🔍 Testing Exact Browser Requests")
    print("=" * 50)
    
    # Test multiple times to see if there's inconsistency
    for attempt in range(5):
        print(f"\n🔄 Attempt {attempt + 1}/5:")
        
        # Test V2 Stats (browser getting 500)
        try:
            response = requests.get(f'{base_url}/api/v2/stats', timeout=5)
            print(f"   V2 Stats: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.text[:100]}")
        except Exception as e:
            print(f"   V2 Stats: ERROR - {e}")
        
        # Test V2 Price (browser getting 404)
        try:
            response = requests.get(f'{base_url}/api/v2/price/current', timeout=5)
            print(f"   V2 Price: {response.status_code}")
            if response.status_code != 200:
                print(f"   Error: {response.text[:100]}")
        except Exception as e:
            print(f"   V2 Price: ERROR - {e}")
        
        # Small delay between attempts
        time.sleep(1)
    
    print(f"\n🔍 Testing Railway Health:")
    
    # Test if Railway is having issues
    try:
        response = requests.get(f'{base_url}/', timeout=10)
        print(f"   Main site: {response.status_code}")
    except Exception as e:
        print(f"   Main site: ERROR - {e}")
    
    # Test a known working endpoint
    try:
        response = requests.get(f'{base_url}/api/webhook-health', timeout=10)
        print(f"   Webhook health: {response.status_code}")
    except Exception as e:
        print(f"   Webhook health: ERROR - {e}")
    
    print(f"\n📊 Analysis:")
    print("If results are inconsistent: Railway load balancer issue")
    print("If all attempts fail: Deployment problem")
    print("If all attempts work: Browser-specific issue")

if __name__ == '__main__':
    debug_exact_browser_requests()
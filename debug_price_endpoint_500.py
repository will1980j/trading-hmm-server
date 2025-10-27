#!/usr/bin/env python3

import requests
import json

def debug_price_endpoint_500():
    """Debug the 500 error from the price endpoint"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 DEBUGGING PRICE ENDPOINT 500 ERROR")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 500:
            try:
                error_data = response.json()
                print("500 Error Response (JSON):")
                print(json.dumps(error_data, indent=2))
                
                # Check for specific error patterns
                error_msg = error_data.get("message", "")
                if error_msg == "0":
                    print("\n🔍 FOUND THE ISSUE: Error message is '0'")
                    print("This is the same psycopg2 error we saw before")
                    print("Likely cause: live_signals table doesn't exist or has wrong schema")
                elif "Live signals table not available" in str(error_data.get("error", "")):
                    print("\n✅ EXPECTED: No live_signals table (this is normal)")
                    print("The endpoint should return 404, not 500")
                else:
                    print(f"\n🔍 DIFFERENT ERROR: {error_msg}")
                    
            except:
                print("500 Error Response (Text):")
                print(response.text[:500])
        else:
            print("Response:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()
    print("=" * 50)
    print("🎯 DIAGNOSIS")
    print("=" * 50)
    
    print("If the error message is '0':")
    print("- The live_signals table query is failing")
    print("- This should be caught and return 404, not 500")
    print("- There might be an exception handling issue")
    
    print()
    print("🔧 SOLUTION:")
    print("- Fix the exception handling in the price endpoint")
    print("- Ensure it returns 404 when no data, not 500")

if __name__ == "__main__":
    debug_price_endpoint_500()
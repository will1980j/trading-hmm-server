"""
Create automated_signals table via web endpoint
"""

import requests
import json

RAILWAY_URL = "https://web-production-cd33.up.railway.app"

def create_table_via_endpoint():
    """Create table by calling Railway endpoint"""
    
    print("🚀 Creating automated_signals table on Railway...")
    print(f"Endpoint: {RAILWAY_URL}/api/create-automated-signals-table")
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/create-automated-signals-table",
            json={},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("\n✅ Table created successfully!")
                print("\n📋 Table structure:")
                for col in data.get('columns', []):
                    print(f"   - {col}")
                return True
            else:
                print(f"\n❌ Table creation failed: {data.get('error')}")
                return False
        else:
            print(f"Response: {response.text}")
            print(f"\n❌ Request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = create_table_via_endpoint()
    
    if success:
        print("\n🎉 Database is ready!")
        print("\nRun the test:")
        print("   python test_automated_webhook_system.py")
    else:
        print("\n⚠️  Need to add the endpoint to web_server.py first")
        print("\nThe endpoint will create the table automatically on first use")
        print("Just run the test and it will create the table:")
        print("   python test_automated_webhook_system.py")

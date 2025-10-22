"""
Reset Railway database connection to clear aborted transactions
Run this AFTER redeploying
"""
import requests

def reset_db():
    print("🔄 Resetting Railway database connection...")
    
    try:
        response = requests.post(
            "https://web-production-cd33.up.railway.app/api/db-reset",
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Database reset successful!")
            print("🎯 Now test the webhook again")
            return True
        else:
            print(f"\n❌ Reset failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    reset_db()

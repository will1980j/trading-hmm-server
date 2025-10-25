#!/usr/bin/env python3

import requests

def verify_v2_tables():
    """Verify what V2 tables actually exist"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🔍 VERIFYING V2 TABLES")
    print("=" * 40)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Check what tables exist
    check_tables_sql = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name LIKE '%v2%'
    ORDER BY table_name;
    """
    
    print("📋 Checking for V2 tables...")
    
    try:
        payload = {"schema_sql": check_tables_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query executed successfully!")
            print(f"Result: {result}")
        else:
            print(f"❌ Query failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Try a simpler approach - check all tables
    print(f"\n📋 Checking all tables...")
    
    all_tables_sql = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """
    
    try:
        payload = {"schema_sql": all_tables_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ All tables query successful!")
            print(f"Result: {result}")
        else:
            print(f"❌ All tables query failed: {response.text}")
            
    except Exception as e:
        print(f"❌ All tables request failed: {e}")

if __name__ == "__main__":
    verify_v2_tables()
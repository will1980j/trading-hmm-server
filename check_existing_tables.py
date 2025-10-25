#!/usr/bin/env python3

import requests

def check_existing_tables():
    """Check existing tables through working endpoints"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🔍 CHECKING EXISTING DATABASE TABLES")
    print("=" * 50)
    
    # Login
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Check webhook stats (this works and shows database info)
    print("📊 Checking webhook stats...")
    try:
        response = session.get(f"{base_url}/api/webhook-stats", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Webhook stats working!")
            print(f"Data: {data}")
        else:
            print(f"❌ Webhook stats failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Webhook stats request failed: {e}")
    
    # Try to create a simple table that we know will work
    print(f"\n📝 Creating a simple test table...")
    
    simple_table_sql = """
    CREATE TABLE IF NOT EXISTS test_deployment_v2 (
        id SERIAL PRIMARY KEY,
        message TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    try:
        payload = {"schema_sql": simple_table_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=30
        )
        
        print(f"Simple table status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Simple table created!")
            print(f"Tables created: {result.get('tables_created', [])}")
            
            # Now try to insert into it
            insert_sql = """
            INSERT INTO test_deployment_v2 (message) 
            VALUES ('V2 deployment test successful!');
            """
            
            insert_payload = {"schema_sql": insert_sql}
            insert_response = session.post(
                f"{base_url}/api/deploy-signal-lab-v2",
                json=insert_payload,
                timeout=30
            )
            
            if insert_response.status_code == 200:
                print("✅ Insert successful - table is working!")
            else:
                print(f"❌ Insert failed: {insert_response.text}")
                
        else:
            print(f"❌ Simple table creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Simple table request failed: {e}")

if __name__ == "__main__":
    check_existing_tables()
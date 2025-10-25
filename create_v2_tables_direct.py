#!/usr/bin/env python3

import requests

def create_v2_tables_via_sql():
    """Create V2 tables by executing SQL through existing endpoints"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    session = requests.Session()
    
    print("🚀 CREATING V2 TABLES VIA DIRECT SQL")
    print("=" * 60)
    
    # Login first
    print("🔐 Logging in...")
    login_data = {'username': 'admin', 'password': 'n2351447'}
    response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Login failed!")
        return
    
    print("✅ Login successful!")
    
    # Read the V2 schema
    try:
        with open('database/signal_lab_v2_schema.sql', 'r') as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("❌ Schema file not found!")
        return
    
    # Split schema into individual CREATE TABLE statements
    statements = []
    current_statement = ""
    
    for line in schema_sql.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
            
        current_statement += line + "\n"
        
        if line.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    print(f"📋 Found {len(statements)} SQL statements")
    
    # Execute each statement individually using a test webhook
    # We'll use the webhook endpoint to execute SQL
    success_count = 0
    
    for i, statement in enumerate(statements):
        if not statement.strip():
            continue
            
        print(f"\n📝 Executing statement {i+1}/{len(statements)}...")
        print(f"   {statement[:60]}...")
        
        # Create a fake signal that will trigger SQL execution
        # This is a workaround - we'll create the tables through the database connection
        
        # For now, let's just print what we would execute
        if 'CREATE TABLE' in statement.upper():
            table_name = "Unknown"
            try:
                parts = statement.split()
                for j, part in enumerate(parts):
                    if part.upper() == 'TABLE':
                        if j + 1 < len(parts):
                            table_name = parts[j + 1].replace('IF', '').replace('NOT', '').replace('EXISTS', '').strip()
                            break
            except:
                pass
            
            print(f"   📋 Would create table: {table_name}")
            success_count += 1
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print(f"📊 {success_count} tables would be created")
    print(f"📋 Tables: signal_lab_trades_v2, signal_targets_v2, signal_prices_v2")
    
    # Alternative approach: Create a simple SQL execution endpoint
    print(f"\n💡 ALTERNATIVE APPROACH:")
    print(f"Since the deployment endpoint has issues, we need to:")
    print(f"1. Fix the deployment endpoint bug (error handling)")
    print(f"2. Or create tables manually through Railway console")
    print(f"3. Or use a different SQL execution method")
    
    # Let's try to create just one table as a test
    print(f"\n🧪 TESTING SIMPLE TABLE CREATION...")
    
    simple_sql = """
    CREATE TABLE IF NOT EXISTS test_v2_deployment (
        id SERIAL PRIMARY KEY,
        created_at TIMESTAMP DEFAULT NOW(),
        message TEXT
    );
    """
    
    # Try using the existing deployment endpoint with just this simple SQL
    try:
        test_payload = {"schema_sql": simple_sql}
        response = session.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=test_payload,
            timeout=30
        )
        
        print(f"Simple table test status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Simple table creation worked: {result}")
        else:
            print(f"❌ Simple table creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Simple table test failed: {e}")

if __name__ == "__main__":
    create_v2_tables_via_sql()
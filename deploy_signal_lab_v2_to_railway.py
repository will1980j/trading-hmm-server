#!/usr/bin/env python3
"""
🚀 DEPLOY SIGNAL LAB V2 TO RAILWAY
Deploy via web server endpoint - cloud-first approach
"""

import requests
import json

def deploy_to_railway():
    """
    Deploy Signal Lab V2 schema via Railway web server
    """
    
    print("🚀 DEPLOYING SIGNAL LAB V2 TO RAILWAY")
    print("=" * 50)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Read the schema file
    print("\n📋 Step 1: Loading V2 Schema...")
    try:
        with open('database/signal_lab_v2_schema.sql', 'r') as f:
            schema_sql = f.read()
        print(f"✅ Schema loaded: {len(schema_sql)} characters")
    except FileNotFoundError:
        print("❌ Schema file not found")
        return False
    
    # Create deployment endpoint payload
    deployment_data = {
        "action": "deploy_signal_lab_v2",
        "schema_sql": schema_sql,
        "verify_v1_integrity": True,
        "create_migration_tools": True
    }
    
    print("\n📡 Step 2: Deploying to Railway...")
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=deployment_data,
            timeout=60  # Schema deployment might take time
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                
                if result.get('success'):
                    print("✅ DEPLOYMENT SUCCESSFUL!")
                    print(f"   📊 V1 Trades Preserved: {result.get('v1_trade_count', 'Unknown')}")
                    print(f"   🗄️ V2 Tables Created: {len(result.get('tables_created', []))}")
                    print(f"   📈 Indexes Created: {result.get('indexes_created', 'Unknown')}")
                    return True
                else:
                    print(f"❌ Deployment failed: {result.get('error', 'Unknown error')}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Invalid JSON response from server")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print("Response might be HTML (endpoint doesn't exist yet)")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def create_deployment_endpoint():
    """
    Since the deployment endpoint doesn't exist yet, 
    let's create it in the web server
    """
    
    print("\n🔧 CREATING DEPLOYMENT ENDPOINT...")
    print("We need to add this endpoint to web_server.py:")
    print()
    
    endpoint_code = '''
@app.route('/api/deploy-signal-lab-v2', methods=['POST'])
def deploy_signal_lab_v2():
    """Deploy Signal Lab V2 schema to Railway database"""
    
    try:
        data = request.get_json()
        schema_sql = data.get('schema_sql')
        
        if not schema_sql:
            return jsonify({'success': False, 'error': 'No schema provided'}), 400
        
        # Get V1 trade count for verification
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM signal_lab_trades")
        v1_count = cursor.fetchone()[0]
        
        # Execute V2 schema
        cursor.execute("BEGIN;")
        
        try:
            # Split and execute statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            tables_created = []
            
            for statement in statements:
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
                    
                    # Track table creation
                    if 'CREATE TABLE' in statement.upper():
                        table_name = statement.split()[2]
                        tables_created.append(table_name)
            
            cursor.execute("COMMIT;")
            
            # Verify V1 integrity
            cursor.execute("SELECT COUNT(*) FROM signal_lab_trades")
            v1_count_after = cursor.fetchone()[0]
            
            if v1_count_after != v1_count:
                return jsonify({
                    'success': False, 
                    'error': f'V1 data integrity issue: {v1_count} -> {v1_count_after}'
                }), 500
            
            return jsonify({
                'success': True,
                'v1_trade_count': v1_count,
                'tables_created': tables_created,
                'message': 'Signal Lab V2 deployed successfully'
            })
            
        except Exception as e:
            cursor.execute("ROLLBACK;")
            return jsonify({'success': False, 'error': str(e)}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
'''
    
    print(endpoint_code)
    print()
    print("📝 MANUAL STEPS:")
    print("1. Add the above endpoint to web_server.py")
    print("2. Deploy to Railway (commit + push)")
    print("3. Run this script again to deploy V2 schema")
    
    return False

if __name__ == "__main__":
    print("🎯 SIGNAL LAB V2 RAILWAY DEPLOYMENT")
    print()
    
    # Try to deploy
    if not deploy_to_railway():
        # If deployment fails, show how to create the endpoint
        create_deployment_endpoint()
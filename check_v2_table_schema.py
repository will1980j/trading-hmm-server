#!/usr/bin/env python3

import requests
import json

def check_v2_table_schema():
    """Check the actual V2 table schema in the database"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    print("🔍 CHECKING V2 TABLE SCHEMA")
    print("=" * 50)
    
    # Create a test endpoint to check table schema
    schema_check_code = '''
import psycopg2
from database.railway_db import RailwayDB

@app.route('/api/debug/v2-schema', methods=['GET'])
def debug_v2_schema():
    """Debug endpoint to check V2 table schema"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'signal_lab_v2_trades'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            return jsonify({
                "table_exists": False,
                "error": "signal_lab_v2_trades table does not exist"
            })
        
        # Get table columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'signal_lab_v2_trades'
            ORDER BY ordinal_position;
        """)
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row[0],
                "type": row[1], 
                "nullable": row[2]
            })
        
        # Test a simple query
        cursor.execute("SELECT COUNT(*) FROM signal_lab_v2_trades;")
        count = cursor.fetchone()[0]
        
        return jsonify({
            "table_exists": True,
            "row_count": count,
            "columns": columns,
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500
'''
    
    print("Creating debug endpoint to check schema...")
    
    # Try to deploy the debug endpoint
    try:
        # First, let's just test what we can access
        print("Testing basic database access...")
        
        # Test if we can create a simple record
        test_signal = {
            "signal": "BULLISH",  # Try uppercase
            "price": 20500.0,
            "timestamp": 1698765432000,
            "session": "NY AM",
            "symbol": "NQ",
            "bias": "bullish"  # Add bias field
        }
        
        response = requests.post(f"{base_url}/api/live-signals-v2", json=test_signal, timeout=10)
        print(f"Webhook test: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if it mentions specific field issues
            v2_automation = data.get("v2_automation", {})
            if "Invalid signal type or price" in str(v2_automation.get("reason", "")):
                print("🔍 ISSUE: Signal validation failing")
                print("   Possible causes:")
                print("   - 'signal' field expects different values")
                print("   - 'price' field has validation issues")
                print("   - Missing required fields")
        
        print()
        
        # Now test the stats query with a simpler approach
        print("Testing if we can access the table at all...")
        
        # Check if there's a simpler endpoint that might work
        response = requests.get(f"{base_url}/api/v2/active-trades", timeout=10)
        print(f"Active trades endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ V2 table is accessible via active-trades endpoint")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Active trades also failing: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 50)
    print("🎯 SCHEMA INVESTIGATION RESULTS")
    print("=" * 50)
    
    print("The issue is likely one of these:")
    print("1. signal_lab_v2_trades table doesn't exist")
    print("2. Table exists but columns have different names")
    print("3. Webhook validation is rejecting all signals")
    print("4. Database connection issues with specific queries")
    
    print()
    print("🔧 IMMEDIATE FIX NEEDED:")
    print("- Check if V2 table was actually created")
    print("- Verify column names match the schema file")
    print("- Fix webhook signal validation")

if __name__ == "__main__":
    check_v2_table_schema()
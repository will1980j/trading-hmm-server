import requests

url = "https://web-production-cd33.up.railway.app/api/run-migration"

# Create migration payload
migration_sql = """
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS be_mfe FLOAT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS no_be_mfe FLOAT DEFAULT NULL;

UPDATE automated_signals 
SET no_be_mfe = mfe 
WHERE no_be_mfe IS NULL AND mfe IS NOT NULL;
"""

payload = {
    "migration_name": "add_dual_mfe_columns",
    "sql": migration_sql
}

print("Sending migration request to Railway...")
print(f"URL: {url}")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Migration completed successfully!")
    else:
        print(f"\n❌ Migration failed with status {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Request failed: {e}")
    print("\nAlternative: Add this endpoint to web_server.py:")
    print("""
@app.route('/api/add-dual-mfe-columns', methods=['POST'])
def add_dual_mfe_columns():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        cursor.execute('''
            ALTER TABLE automated_signals 
            ADD COLUMN IF NOT EXISTS be_mfe FLOAT DEFAULT NULL,
            ADD COLUMN IF NOT EXISTS no_be_mfe FLOAT DEFAULT NULL;
        ''')
        
        cursor.execute('''
            UPDATE automated_signals 
            SET no_be_mfe = mfe 
            WHERE no_be_mfe IS NULL AND mfe IS NOT NULL;
        ''')
        
        rows_updated = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Added dual MFE columns, migrated {rows_updated} rows"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
""")

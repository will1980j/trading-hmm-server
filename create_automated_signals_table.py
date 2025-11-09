"""
Create automated_signals table via the web server's /api/create-table endpoint
"""
import requests
import json

def create_table_via_endpoint():
    """Create table by calling a special endpoint on the web server"""
    
    url = "https://web-production-cd33.up.railway.app/api/create-automated-signals-table"
    
    print("🚀 Creating automated_signals table via web endpoint...")
    print(f"URL: {url}\n")
    
    try:
        response = requests.post(url, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}\n")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Table created successfully!")
                print(f"📋 Columns: {len(data.get('columns', []))}")
                for col in data.get('columns', []):
                    print(f"  - {col}")
                return True
            else:
                print(f"❌ Failed: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_table_via_endpoint()
    
    if success:
        print("\n🎉 Table is ready! Now run: python test_automated_webhook_system.py")
    else:
        print("\n⚠️  Need to add the endpoint to web_server.py first")
        print("Add this endpoint to web_server.py:")
        print("""
@app.route('/api/create-automated-signals-table', methods=['POST'])
def create_automated_signals_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Drop existing table
        cursor.execute("DROP TABLE IF EXISTS automated_signals CASCADE;")
        
        # Create table
        cursor.execute('''
            CREATE TABLE automated_signals (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(20) NOT NULL,
                trade_id VARCHAR(100) NOT NULL,
                direction VARCHAR(10),
                entry_price DECIMAL(10, 2),
                stop_loss DECIMAL(10, 2),
                risk_distance DECIMAL(10, 2),
                target_1r DECIMAL(10, 2),
                target_2r DECIMAL(10, 2),
                target_3r DECIMAL(10, 2),
                target_5r DECIMAL(10, 2),
                target_10r DECIMAL(10, 2),
                target_20r DECIMAL(10, 2),
                session VARCHAR(20),
                bias VARCHAR(20),
                current_price DECIMAL(10, 2),
                mfe DECIMAL(10, 4),
                exit_price DECIMAL(10, 2),
                exit_type VARCHAR(20),
                final_mfe DECIMAL(10, 4),
                account_size DECIMAL(15, 2),
                risk_percent DECIMAL(5, 2),
                contracts INTEGER,
                risk_amount DECIMAL(10, 2),
                timestamp BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX idx_trade_id ON automated_signals(trade_id);
            CREATE INDEX idx_event_type ON automated_signals(event_type);
            CREATE INDEX idx_created_at ON automated_signals(created_at);
        ''')
        
        conn.commit()
        
        # Get column list
        cursor.execute('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'automated_signals'
            ORDER BY ordinal_position;
        ''')
        
        columns = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Table created successfully',
            'columns': columns
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
""")

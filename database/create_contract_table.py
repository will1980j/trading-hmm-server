from railway_db import RailwayDB

# Create missing contract_settings table
with RailwayDB() as db:
    with db.conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS contract_settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                contract_data JSONB NOT NULL DEFAULT '{}',
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
        
        cur.execute('''
            INSERT INTO contract_settings (id, contract_data) 
            VALUES (1, '{"NQ": "NQ1!", "ES": "ES1!", "YM": "YM1!", "RTY": "RTY1!"}')
            ON CONFLICT (id) DO NOTHING
        ''')
    
    db.conn.commit()
    print("Contract settings table created successfully")
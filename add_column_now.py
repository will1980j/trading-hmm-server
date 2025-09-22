import psycopg2

DATABASE_URL = "postgresql://postgres:hvJnnhbUsRppEDPlGAVrEeVLijYXJntS@postgres.railway.internal:5432/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("ALTER TABLE signal_lab_trades ADD COLUMN IF NOT EXISTS target_r_score DECIMAL(5,2) DEFAULT NULL")
    conn.commit()
    
    print("SUCCESS: target_r_score column added")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
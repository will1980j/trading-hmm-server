import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')

def run_migration():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    with open('database/price_snapshots_schema.sql', 'r') as f:
        sql = f.read()
    
    try:
        cur.execute(sql)
        conn.commit()
        print("✓ Price snapshots schema migration complete")
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()

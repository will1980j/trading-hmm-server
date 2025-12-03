"""
Add mae_global_r column to automated_signals table.
This column tracks Maximum Adverse Excursion (worst drawdown) in R-multiples.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def add_mae_column():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'automated_signals' 
            AND column_name = 'mae_global_r'
        """)
        
        if cursor.fetchone():
            print("✅ Column mae_global_r already exists")
            conn.close()
            return True
        
        # Add the column
        print("Adding mae_global_r column to automated_signals table...")
        cursor.execute("""
            ALTER TABLE automated_signals 
            ADD COLUMN IF NOT EXISTS mae_global_r FLOAT DEFAULT NULL
        """)
        
        conn.commit()
        print("✅ Successfully added mae_global_r column")
        
        # Verify
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'automated_signals' 
            AND column_name = 'mae_global_r'
        """)
        result = cursor.fetchone()
        if result:
            print(f"✅ Verified: {result[0]} ({result[1]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    add_mae_column()

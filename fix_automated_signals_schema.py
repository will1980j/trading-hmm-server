import os
import psycopg2
from psycopg2 import sql

print("=== FIXING AUTOMATED_SIGNALS TABLE SCHEMA ===\n")

# Get database connection
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    print("1. Checking current table schema...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'automated_signals'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    if columns:
        print("\nCurrent columns:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
    else:
        print("  Table does not exist yet")
    
    print("\n2. Adding missing columns...")
    
    # Add signal_date column if missing
    try:
        cursor.execute("""
            ALTER TABLE automated_signals 
            ADD COLUMN IF NOT EXISTS signal_date DATE
        """)
        print("  ✓ Added signal_date column")
    except Exception as e:
        print(f"  signal_date: {e}")
    
    # Add signal_time column if missing
    try:
        cursor.execute("""
            ALTER TABLE automated_signals 
            ADD COLUMN IF NOT EXISTS signal_time TIME
        """)
        print("  ✓ Added signal_time column")
    except Exception as e:
        print(f"  signal_time: {e}")
    
    # Add timestamp column if missing
    try:
        cursor.execute("""
            ALTER TABLE automated_signals 
            ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT NOW()
        """)
        print("  ✓ Added timestamp column")
    except Exception as e:
        print(f"  timestamp: {e}")
    
    conn.commit()
    
    print("\n3. Verifying updated schema...")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'automated_signals'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print("\nUpdated columns:")
    for col_name, col_type in columns:
        print(f"  - {col_name}: {col_type}")
    
    print("\n✓✓✓ SCHEMA FIX COMPLETE ✓✓✓")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

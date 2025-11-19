import os
import psycopg2

# Connect to Railway PostgreSQL database
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Execute read-only query
    query = """
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'automated_signals' 
    ORDER BY ordinal_position;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Print results
    print("\n" + "="*60)
    print("AUTOMATED_SIGNALS TABLE SCHEMA")
    print("="*60)
    print(f"{'Column Name':<30} {'Data Type':<30}")
    print("-"*60)
    
    for row in results:
        column_name, data_type = row
        print(f"{column_name:<30} {data_type:<30}")
    
    print("="*60)
    print(f"Total columns: {len(results)}\n")
    
    # Close connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

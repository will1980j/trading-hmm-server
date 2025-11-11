import os
import psycopg2
from datetime import datetime, timedelta

# Get Railway database URL
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    print("Please set it from Railway dashboard")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=== Checking Automated Signals Database ===\n")
    
    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'automated_signals'
        );
    """)
    table_exists = cur.fetchone()[0]
    print(f"1. Table 'automated_signals' exists: {table_exists}")
    
    if not table_exists:
        print("\n❌ TABLE DOES NOT EXIST - This is the problem!")
        print("   Need to create the automated_signals table")
    else:
        # Count total records
        cur.execute("SELECT COUNT(*) FROM automated_signals;")
        total = cur.fetchone()[0]
        print(f"   Total records: {total}")
        
        # Count by status
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM automated_signals 
            GROUP BY status;
        """)
        status_counts = cur.fetchall()
        print(f"\n2. Records by status:")
        for status, count in status_counts:
            print(f"   {status}: {count}")
        
        # Recent signals
        cur.execute("""
            SELECT id, signal_type, status, signal_time, created_at
            FROM automated_signals
            ORDER BY created_at DESC
            LIMIT 5;
        """)
        recent = cur.fetchall()
        print(f"\n3. Recent signals (last 5):")
        for row in recent:
            print(f"   ID {row[0]}: {row[1]} - {row[2]} - {row[3]}")
        
        # Check for signals in last 24 hours
        cur.execute("""
            SELECT COUNT(*) 
            FROM automated_signals 
            WHERE created_at > NOW() - INTERVAL '24 hours';
        """)
        last_24h = cur.fetchone()[0]
        print(f"\n4. Signals in last 24 hours: {last_24h}")
    
    # Also check live_signals table
    print("\n=== Checking live_signals table ===")
    cur.execute("""
        SELECT COUNT(*) 
        FROM live_signals 
        WHERE timestamp > NOW() - INTERVAL '24 hours';
    """)
    live_24h = cur.fetchone()[0]
    print(f"   Signals in last 24 hours: {live_24h}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")

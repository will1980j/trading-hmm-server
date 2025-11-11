"""
Add signal_date and signal_time columns to automated_signals table on Railway
Run this ONCE to migrate the existing database
"""

import os
import psycopg2

# Get Railway database URL
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    print("❌ DATABASE_URL environment variable not set")
    print("Set it in Railway dashboard or run: $env:DATABASE_URL='your_railway_url'")
    exit(1)

try:
    # Connect to Railway database
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    print("✅ Connected to Railway database")
    
    # Check if columns already exist
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'automated_signals' 
        AND column_name IN ('signal_date', 'signal_time')
    """)
    existing = [row[0] for row in cursor.fetchall()]
    
    if 'signal_date' in existing and 'signal_time' in existing:
        print("✅ Columns already exist - no migration needed")
    else:
        print("📝 Adding signal_date and signal_time columns...")
        
        # Add columns
        cursor.execute("""
            ALTER TABLE automated_signals 
            ADD COLUMN IF NOT EXISTS signal_date DATE,
            ADD COLUMN IF NOT EXISTS signal_time TIME
        """)
        
        conn.commit()
        print("✅ Columns added successfully!")
        print("")
        print("⚠️  NOTE: Existing signals will have NULL for these fields")
        print("   New signals from TradingView will have correct signal candle times")
    
    cursor.close()
    conn.close()
    
    print("")
    print("🎯 NEXT STEPS:")
    print("1. Deploy the updated code to Railway (GitHub push)")
    print("2. Send a new signal from TradingView")
    print("3. Check dashboard - new signal should show correct time!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

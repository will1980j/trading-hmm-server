#!/usr/bin/env python3

from database.railway_db import RailwayDB

try:
    db = RailwayDB()
    cursor = db.conn.cursor()
    
    # Check if column exists
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'signal_lab_trades' 
        AND column_name = 'target_r_score'
    """)
    
    result = cursor.fetchone()
    if result:
        print("✅ target_r_score column already exists")
    else:
        print("❌ target_r_score column missing - adding now...")
        
        # Add the column
        cursor.execute("""
            ALTER TABLE signal_lab_trades 
            ADD COLUMN target_r_score DECIMAL(5,2) DEFAULT NULL
        """)
        db.conn.commit()
        print("✅ target_r_score column added successfully")
    
    # Verify it's there
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'signal_lab_trades' 
        AND column_name = 'target_r_score'
    """)
    
    final_check = cursor.fetchone()
    if final_check:
        print(f"✅ CONFIRMED: target_r_score column exists as {final_check['data_type']}")
    else:
        print("❌ FAILED: Column still not found after creation attempt")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ ERROR: {e}")
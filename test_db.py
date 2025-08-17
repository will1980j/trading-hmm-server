#!/usr/bin/env python3
"""Test database connection and signal lab data"""

import os
from database.railway_db import RailwayDB

try:
    db = RailwayDB()
    print("✅ Database connected")
    
    cursor = db.conn.cursor()
    
    # Test basic query
    cursor.execute("SELECT COUNT(*) FROM signal_lab_trades")
    count = cursor.fetchone()[0]
    print(f"📊 Found {count} trades")
    
    # Test new schema
    cursor.execute("""
        SELECT id, mfe_none, be1_level, be1_hit, mfe1, be2_level, be2_hit, mfe2 
        FROM signal_lab_trades 
        LIMIT 3
    """)
    
    rows = cursor.fetchall()
    print(f"🔍 Sample data:")
    for row in rows:
        print(f"  ID {row[0]}: mfe_none={row[1]}, be1_level={row[2]}, be1_hit={row[3]}")
    
    cursor.close()
    print("✅ All tests passed")
    
except Exception as e:
    print(f"❌ Error: {e}")
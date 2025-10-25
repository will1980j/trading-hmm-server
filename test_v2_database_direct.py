#!/usr/bin/env python3

import os
import psycopg2
from datetime import datetime

def test_v2_database():
    """Test V2 database directly"""
    
    print("🔍 Testing V2 Database Direct Connection")
    print("=" * 50)
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Database connection successful")
        
        # Test 1: Check if V2 table exists
        print("\n1. Checking if signal_lab_v2_trades table exists...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'signal_lab_v2_trades'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print("   ✅ signal_lab_v2_trades table exists")
            
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'signal_lab_v2_trades'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"   📊 Table has {len(columns)} columns:")
            for col_name, col_type in columns[:5]:  # Show first 5
                print(f"      - {col_name}: {col_type}")
            if len(columns) > 5:
                print(f"      ... and {len(columns) - 5} more columns")
                
        else:
            print("   ❌ signal_lab_v2_trades table NOT found")
            return
        
        # Test 2: Check PostgreSQL functions
        print("\n2. Checking PostgreSQL functions...")
        functions_to_check = [
            'is_pivot_low',
            'is_pivot_high', 
            'calc_bullish_sl',
            'calc_bearish_sl'
        ]
        
        for func_name in functions_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_proc 
                    WHERE proname = %s
                );
            """, (func_name,))
            
            func_exists = cursor.fetchone()[0]
            status = "✅" if func_exists else "❌"
            print(f"   {status} {func_name}()")
        
        # Test 3: Try a simple insert
        print("\n3. Testing simple V2 insert...")
        try:
            cursor.execute("""
                INSERT INTO signal_lab_v2_trades (
                    trade_uuid, symbol, bias, session, 
                    date, time, entry_price, stop_loss_price, risk_distance,
                    target_1r_price, target_2r_price, target_3r_price,
                    target_5r_price, target_10r_price, target_20r_price,
                    current_mfe, trade_status, active_trade, auto_populated
                ) VALUES (
                    gen_random_uuid(), 'NQ1!', 'Bullish', 'NY AM',
                    CURRENT_DATE, CURRENT_TIME, NULL, NULL, NULL,
                    NULL, NULL, NULL, NULL, NULL, NULL,
                    0.00, 'pending_confirmation', false, true
                ) RETURNING id, trade_uuid;
            """)
            
            result = cursor.fetchone()
            if result:
                trade_id, trade_uuid = result
                print(f"   ✅ Insert successful - ID: {trade_id}, UUID: {trade_uuid}")
                
                # Clean up test record
                cursor.execute("DELETE FROM signal_lab_v2_trades WHERE id = %s", (trade_id,))
                print("   🧹 Test record cleaned up")
                
            conn.commit()
            
        except Exception as insert_error:
            print(f"   ❌ Insert failed: {insert_error}")
            conn.rollback()
        
        # Test 4: Count existing records
        print("\n4. Checking existing V2 records...")
        cursor.execute("SELECT COUNT(*) FROM signal_lab_v2_trades")
        count = cursor.fetchone()[0]
        print(f"   📊 Current V2 records: {count}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 50)
        print("🎯 DATABASE STATUS:")
        if table_exists:
            print("   ✅ V2 database schema is deployed")
            print("   ✅ Database operations should work")
            print("   🔧 The webhook error might be in the application logic")
        else:
            print("   ❌ V2 database schema missing")
            print("   🔧 Need to deploy V2 schema first")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_v2_database()
#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB

def check_railway_schema():
    """Check Railway database schema using the same connection as web server"""
    
    try:
        # Use the same connection method as web_server.py
        db = RailwayDB()
        
        if not db.conn:
            print('❌ No database connection available')
            return
            
        cursor = db.conn.cursor()
        
        print("🔍 CHECKING RAILWAY DATABASE SCHEMA")
        print("=" * 50)
        
        # Check if signal_lab_trades table exists and its columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'signal_lab_trades'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print('📋 SIGNAL_LAB_TRADES COLUMNS:')
        if columns:
            for row in columns:
                col = row['column_name'] if isinstance(row, dict) else row[0]
                dtype = row['data_type'] if isinstance(row, dict) else row[1]
                print(f'  ✅ {col}: {dtype}')
        else:
            print('  ❌ Table does not exist!')
            
        # Check table count if exists
        if columns:
            cursor.execute('SELECT COUNT(*) FROM signal_lab_trades')
            result = cursor.fetchone()
            count = result[0] if isinstance(result, tuple) else result['count']
            print(f'\n📊 Total trades: {count}')
        
        # Check for other expected tables
        expected_tables = [
            'live_signals',
            'signal_processing_log', 
            'prediction_accuracy_tracking',
            'signal_lab_trades_v2',
            'signal_targets_v2',
            'signal_prices_v2'
        ]
        
        print('\n🔍 CHECKING OTHER TABLES:')
        for table in expected_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            result = cursor.fetchone()
            exists = result[0] if isinstance(result, tuple) else result['exists']
            status = "✅" if exists else "❌"
            print(f'  {status} {table}: {"EXISTS" if exists else "MISSING"}')
        
        # Check for missing columns in signal_lab_trades
        if columns:
            print('\n🔍 CHECKING FOR MISSING COLUMNS:')
            expected_columns = ['updated_at', 'created_at']
            existing_cols = [row['column_name'] if isinstance(row, dict) else row[0] for row in columns]
            
            for col in expected_columns:
                if col in existing_cols:
                    print(f'  ✅ {col}: EXISTS')
                else:
                    print(f'  ❌ {col}: MISSING')
        
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f'❌ Database Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_railway_schema()
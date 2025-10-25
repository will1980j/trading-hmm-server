#!/usr/bin/env python3

import os
import psycopg2
from urllib.parse import urlparse

def check_database_schema():
    """Check current database schema"""
    
    # Get Railway database URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print('❌ No DATABASE_URL found')
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🔍 CHECKING DATABASE SCHEMA")
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
            for col, dtype in columns:
                print(f'  ✅ {col}: {dtype}')
        else:
            print('  ❌ Table does not exist!')
            
        # Check table count if exists
        if columns:
            cursor.execute('SELECT COUNT(*) FROM signal_lab_trades')
            count = cursor.fetchone()[0]
            print(f'\n📊 Total trades: {count}')
        
        # Check for other expected tables
        expected_tables = [
            'live_signals',
            'signal_processing_log',
            'prediction_accuracy_tracking'
        ]
        
        print('\n🔍 CHECKING OTHER TABLES:')
        for table in expected_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            exists = cursor.fetchone()[0]
            status = "✅" if exists else "❌"
            print(f'  {status} {table}: {"EXISTS" if exists else "MISSING"}')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Database Error: {e}')

if __name__ == "__main__":
    check_database_schema()
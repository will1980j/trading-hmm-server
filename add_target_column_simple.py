#!/usr/bin/env python3
"""
Simple script to add target_r_score column
"""

import os
import psycopg2
from urllib.parse import urlparse

def add_target_column():
    try:
        # Get DATABASE_URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("ERROR: DATABASE_URL environment variable not found")
            return False
        
        print("Connecting to database...")
        
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'signal_lab_trades' 
            AND column_name = 'target_r_score'
        """)
        
        if cursor.fetchone():
            print("SUCCESS: target_r_score column already exists")
            return True
        
        # Add the column
        print("Adding target_r_score column...")
        cursor.execute("""
            ALTER TABLE signal_lab_trades 
            ADD COLUMN target_r_score DECIMAL(5,2) DEFAULT NULL
        """)
        
        conn.commit()
        print("SUCCESS: Added target_r_score column to signal_lab_trades table")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'signal_lab_trades' 
            AND column_name = 'target_r_score'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"VERIFIED: {result[0]} ({result[1]}, nullable: {result[2]})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = add_target_column()
    if success:
        print("\nSUCCESS: Target column added successfully!")
        print("The Target field in Signal Lab should now save data properly.")
    else:
        print("\nFAILED: Could not add target column")
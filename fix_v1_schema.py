#!/usr/bin/env python3

import requests
import json

def fix_v1_schema():
    """Fix V1 schema by adding missing columns and tables"""
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # SQL to fix V1 schema issues
    fix_sql = """
-- Add missing columns to signal_lab_trades if they don't exist
DO $$ 
BEGIN
    -- Add updated_at column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'signal_lab_trades' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE signal_lab_trades ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
        UPDATE signal_lab_trades SET updated_at = created_at WHERE updated_at IS NULL;
    END IF;
    
    -- Add created_at column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'signal_lab_trades' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE signal_lab_trades ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
    END IF;
END $$;

-- Create signal_processing_log table if it doesn't exist
CREATE TABLE IF NOT EXISTS signal_processing_log (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER,
    bias VARCHAR(10),
    processed_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20),
    error_message TEXT
);

-- Create prediction_accuracy_tracking table if it doesn't exist  
CREATE TABLE IF NOT EXISTS prediction_accuracy_tracking (
    id SERIAL PRIMARY KEY,
    signal_id INTEGER,
    predicted_outcome DECIMAL(10,2),
    actual_outcome DECIMAL(10,2),
    confidence_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
"""
    
    print("🔧 FIXING V1 SCHEMA ISSUES")
    print("=" * 50)
    
    payload = {
        "schema_sql": fix_sql
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/deploy-signal-lab-v2",
            json=payload,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ V1 SCHEMA FIXES APPLIED!")
            print(f"📊 V1 Trade Count: {result.get('v1_trade_count', 'Unknown')}")
            print(f"📋 Tables Created: {result.get('tables_created', [])}")
            print(f"💬 Message: {result.get('message', 'No message')}")
        else:
            print(f"❌ SCHEMA FIX FAILED!")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    fix_v1_schema()
#!/usr/bin/env python3
"""
Test database connection and insert
"""

from database.supabase_client import SupabaseDB
from datetime import datetime

def test_database():
    try:
        print("Testing Supabase connection...")
        db = SupabaseDB()
        
        # Test market data insert
        print("Inserting test market data...")
        result = db.store_market_data('NQ1!', {
            'open': 15000,
            'high': 15050,
            'low': 14950,
            'close': 15025,
            'volume': 1000,
            'timeframe': '1m'
        })
        print(f"Market data result: {result}")
        
        # Test signal insert
        print("Inserting test signal...")
        signal_result = db.store_signal({
            'symbol': 'NQ1!',
            'type': 'LONG',
            'entry': 15000,
            'confidence': 0.8,
            'reason': 'Test signal'
        })
        print(f"Signal result: {signal_result}")
        
        # Test data retrieval
        print("Retrieving data...")
        data = db.get_recent_data('NQ1!', limit=5)
        print(f"Retrieved data: {data}")
        
        print("✅ Database test completed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_database()
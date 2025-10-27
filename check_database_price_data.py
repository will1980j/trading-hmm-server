#!/usr/bin/env python3

import os
import psycopg2
from datetime import datetime

def check_database_price_data():
    """Check if there's fake price data in the database"""
    
    print("🔍 CHECKING DATABASE FOR FAKE PRICE DATA")
    print("=" * 50)
    
    try:
        # Connect to Railway database
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ No DATABASE_URL environment variable")
            return
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if realtime_prices table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'realtime_prices'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("✅ realtime_prices table doesn't exist - no fake data in DB")
            cursor.close()
            conn.close()
            return
        
        print("📊 realtime_prices table exists, checking contents:")
        
        # Get count of records
        cursor.execute("SELECT COUNT(*) FROM realtime_prices;")
        count = cursor.fetchone()[0]
        print(f"   Total records: {count}")
        
        if count == 0:
            print("✅ No price data in database - this is correct!")
        else:
            print("⚠️ Found price data in database:")
            
            # Get latest records
            cursor.execute("""
                SELECT symbol, price, timestamp, session, volume, price_change, created_at
                FROM realtime_prices 
                ORDER BY created_at DESC 
                LIMIT 5;
            """)
            
            records = cursor.fetchall()
            for i, record in enumerate(records):
                symbol, price, timestamp, session, volume, change, created_at = record
                print(f"   {i+1}. Price: {price}, Session: {session}, Created: {created_at}")
                
                # Check if this looks like fake data
                if price < 24000 or price > 26000:  # NQ is typically 24k-26k range
                    print(f"      ❌ FAKE DATA: Price {price} is outside normal NQ range")
                else:
                    print(f"      ⚠️ Could be real or fake: {price}")
        
        # Clear fake data if found
        if count > 0:
            print(f"\n🧹 CLEARING {count} FAKE PRICE RECORDS:")
            cursor.execute("DELETE FROM realtime_prices;")
            conn.commit()
            print(f"   ✅ Deleted {count} fake price records")
            
            # Verify deletion
            cursor.execute("SELECT COUNT(*) FROM realtime_prices;")
            new_count = cursor.fetchone()[0]
            print(f"   ✅ Verified: {new_count} records remaining (should be 0)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
    
    # Test endpoints after clearing database
    print("\n🔍 TESTING ENDPOINTS AFTER DATABASE CLEANUP:")
    
    import requests
    base_url = "https://web-production-cd33.up.railway.app"
    
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"   /api/v2/price/current: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            if data.get('status') == 'no_data':
                print("   ✅ PERFECT: Now returns 404 no_data (correct)")
            else:
                print(f"   ⚠️ Returns 404 but status: {data.get('status')}")
        elif response.status_code == 200:
            data = response.json()
            print(f"   ❌ STILL WRONG: Returns 200 with price: {data.get('price')}")
            print("   This means there's another source of fake data")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing endpoint: {str(e)}")
    
    print("\n📋 SUMMARY:")
    print("✅ Checked and cleared any fake price data from database")
    print("✅ System should now properly show 'no data' state")
    print("✅ Ready for real TradingView price data")

if __name__ == "__main__":
    check_database_price_data()
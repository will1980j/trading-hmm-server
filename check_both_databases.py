"""
Check if DATABASE_URL and DATABASE_PUBLIC_URL point to different databases
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

trade_id = "20251213_140113000_BULLISH"

print("=" * 80)
print("DATABASE COMPARISON TEST")
print("=" * 80)
print()

# Check DATABASE_URL
print("1. Checking DATABASE_URL...")
db_url = os.getenv('DATABASE_URL')
print(f"   URL: {db_url[:60]}...")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT event_type FROM automated_signals
        WHERE trade_id = %s
        ORDER BY timestamp ASC
    """, (trade_id,))
    
    events = [row[0] for row in cur.fetchall()]
    print(f"   Events: {events}")
    print(f"   Has ENTRY: {'ENTRY' in events}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"   Error: {e}")

print()

# Check DATABASE_PUBLIC_URL
print("2. Checking DATABASE_PUBLIC_URL...")
db_public_url = os.getenv('DATABASE_PUBLIC_URL')

if db_public_url:
    print(f"   URL: {db_public_url[:60]}...")
    
    if db_public_url == db_url:
        print("   ✅ Same as DATABASE_URL")
    else:
        print("   ⚠️ DIFFERENT from DATABASE_URL!")
        
        try:
            conn = psycopg2.connect(db_public_url)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT event_type FROM automated_signals
                WHERE trade_id = %s
                ORDER BY timestamp ASC
            """, (trade_id,))
            
            events = [row[0] for row in cur.fetchall()]
            print(f"   Events: {events}")
            print(f"   Has ENTRY: {'ENTRY' in events}")
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"   Error: {e}")
else:
    print("   Not set (will use DATABASE_URL)")

print()
print("=" * 80)
print("CONCLUSION")
print("=" * 80)

if db_public_url and db_public_url != db_url:
    print("⚠️ DATABASE_PUBLIC_URL is different from DATABASE_URL")
    print("   This could explain why lifecycle enforcement doesn't find ENTRY")
    print("   Railway might be using DATABASE_PUBLIC_URL for lifecycle checks")
else:
    print("✅ Both URLs are the same (or PUBLIC not set)")
    print("   The issue must be something else")

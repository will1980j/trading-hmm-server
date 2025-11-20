import os
import psycopg2

# Railway DATABASE_URL - you need to set this in your environment
# For Railway deployment, this is automatically set
# For local testing, you need to get it from Railway dashboard

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("=" * 60)
    print("DATABASE_URL NOT SET")
    print("=" * 60)
    print("\nTo run this query, you need to set DATABASE_URL.")
    print("\nFor Railway deployment:")
    print("  - This is automatically available")
    print("\nFor local testing:")
    print("  1. Get DATABASE_URL from Railway dashboard")
    print("  2. Set it: $env:DATABASE_URL='your_url_here'")
    print("  3. Run this script again")
    print("=" * 60)
    exit(1)

try:
    # Connect directly to Railway PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Execute query
    cursor.execute("SELECT DISTINCT event_type FROM automated_signals ORDER BY event_type;")
    
    # Fetch results
    results = cursor.fetchall()
    
    # Print results
    print("\nDISTINCT EVENT TYPES IN automated_signals TABLE:")
    print("=" * 60)
    if results:
        for row in results:
            print(f"  - {row[0]}")
    else:
        print("  (No event types found)")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

import os
import sys
import psycopg2

# Add parent directory to path to import database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB

try:
    # Use existing database connection configuration
    db = RailwayDB()
    
    if not db.conn:
        print("ERROR: Could not establish database connection")
        exit(1)
    
    cursor = db.conn.cursor()
    
    # Execute query
    cursor.execute("SELECT DISTINCT event_type FROM automated_signals ORDER BY event_type;")
    
    # Fetch results
    results = cursor.fetchall()
    
    # Print results
    print("DISTINCT EVENT TYPES:")
    print("=" * 40)
    for row in results:
        print(row[0])
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

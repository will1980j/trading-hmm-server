"""
Query distinct event_type values from automated_signals table.
Uses the same connection method as automated_signals_state.py
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def query_event_types():
    """Query and display distinct event types from automated_signals table."""
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("=" * 60)
        print("ERROR: DATABASE_URL is not set")
        print("=" * 60)
        print("\nThis script requires DATABASE_URL environment variable.")
        print("On Railway, this is automatically set.")
        print("For local testing, set it from Railway dashboard.")
        print("=" * 60)
        return
    
    try:
        # Connect to Railway PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Execute query
        query = "SELECT DISTINCT event_type FROM automated_signals ORDER BY event_type;"
        cursor.execute(query)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Display results
        print("\n" + "=" * 60)
        print("DISTINCT EVENT TYPES IN automated_signals TABLE")
        print("=" * 60)
        
        if results:
            for row in results:
                print(row[0])
        else:
            print("(No event types found in table)")
        
        print("=" * 60)
        print(f"Total distinct event types: {len(results)}")
        print("=" * 60 + "\n")
        
        # Cleanup
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\nERROR querying database: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    query_event_types()

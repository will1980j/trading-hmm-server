"""
Clear Database for V2 Export
Removes all signals to start fresh with V2 export system
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("CLEAR DATABASE FOR V2 EXPORT")
print("=" * 80)
print()

database_url = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Count current signals
    cursor.execute("SELECT COUNT(*) FROM automated_signals")
    count = cursor.fetchone()[0]
    
    print(f"Current signals in database: {count}")
    print()
    print("This will DELETE all signals from automated_signals table.")
    print("The V2 export will repopulate with clean, complete data.")
    print()
    
    # Delete all signals
    cursor.execute("DELETE FROM automated_signals")
    conn.commit()
    
    print(f"✅ Deleted {count} signals")
    print()
    print("Database is now empty and ready for V2 export.")
    print()
    print("Next steps:")
    print("1. Deploy V2 indicator code")
    print("2. Enable 'Export Confirmed Signals' checkbox")
    print("3. Create export alert")
    print("4. Wait ~2.5 hours for export to complete")
    print("5. Run import script")
    print("6. Enable 'Export All Signals' checkbox")
    print("7. Wait for All Signals export")
    print("8. Dashboard will have complete data")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

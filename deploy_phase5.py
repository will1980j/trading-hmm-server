#!/usr/bin/env python3
"""
Deploy Phase 5: Backend Telemetry Upgrade
Executes database migration and updates webhook handler
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Execute database migration to add telemetry column"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Read migration SQL
        with open('database/phase5_add_telemetry_column.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Database migration completed")
        print("   - Added telemetry JSONB column")
        print("   - Created GIN index on telemetry")
        print("   - Created index on schema_version")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Deploying Phase 5: Backend Telemetry Upgrade")
    print("=" * 60)
    
    if run_migration():
        print("\n✅ Phase 5 deployment complete!")
        print("\n📋 Next steps:")
        print("   1. Integrate telemetry_webhook_handler.py into web_server.py")
        print("   2. Update automated_signals_state.py with telemetry support")
        print("   3. Test with sample telemetry payload")
        print("   4. Deploy to Railway")
    else:
        print("\n❌ Phase 5 deployment failed")

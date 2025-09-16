#!/usr/bin/env python3
"""
Create contract_settings table to fix contract manager
"""

from railway_db import RailwayDB
import json

def create_contract_table():
    """Create and initialize the contract_settings table"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        print("Creating contract_settings table...")
        
        # Create the table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contract_settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                contract_data JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Check if data exists
        cursor.execute("SELECT COUNT(*) as count FROM contract_settings")
        result = cursor.fetchone()
        count = result['count'] if result else 0
        
        if count == 0:
            # Insert default contract data
            default_contracts = {
                'NQ': 'NQ1!',
                'ES': 'ES1!',
                'YM': 'YM1!',
                'RTY': 'RTY1!'
            }
            
            cursor.execute("""
                INSERT INTO contract_settings (id, contract_data, updated_at)
                VALUES (1, %s, NOW())
            """, (json.dumps(default_contracts),))
            
            print(f"✅ Inserted default contracts: {default_contracts}")
        else:
            # Show existing data
            cursor.execute("SELECT contract_data FROM contract_settings WHERE id = 1")
            result = cursor.fetchone()
            if result:
                existing_data = result['contract_data']
                if isinstance(existing_data, str):
                    existing_data = json.loads(existing_data)
                print(f"✅ Existing contracts: {existing_data}")
        
        db.conn.commit()
        print("✅ Contract settings table ready")
        
        # Test the contract manager
        print("\nTesting contract manager...")
        from contract_manager import ContractManager
        contract_manager = ContractManager(db)
        
        active_nq = contract_manager.get_active_contract('NQ')
        print(f"Active NQ contract: {active_nq}")
        
        all_contracts = contract_manager.get_all_active_contracts()
        print(f"All active contracts: {all_contracts}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Contract Settings Table Setup")
    print("=" * 30)
    success = create_contract_table()
    
    if success:
        print("\n✅ Contract manager should now work correctly!")
        print("The Signal Lab auto-population issue should be resolved.")
    else:
        print("\n❌ Failed to set up contract table.")
        print("Manual intervention may be required.")
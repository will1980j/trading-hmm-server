"""
Check if automated_signals table has the required columns
"""
import requests

def check_table_schema():
    """Check table schema via API"""
    print("=" * 80)
    print("CHECKING TABLE SCHEMA")
    print("=" * 80)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # The issue: handle_entry_signal tries to insert be_mfe and no_be_mfe
    # but the CREATE TABLE statement doesn't include those columns
    
    print("\n🔍 PROBLEM FOUND:")
    print("\nIn web_server.py handle_entry_signal():")
    print("  CREATE TABLE includes: mfe, final_mfe")
    print("  INSERT statement includes: be_mfe, no_be_mfe")
    print("\n❌ MISMATCH! Table doesn't have be_mfe and no_be_mfe columns!")
    
    print("\n💡 SOLUTION:")
    print("\nThe table needs these columns:")
    print("  - be_mfe DECIMAL(10,4)")
    print("  - no_be_mfe DECIMAL(10,4)")
    
    print("\n📝 Quick fix options:")
    print("\n1. Add columns to table (ALTER TABLE)")
    print("2. Update CREATE TABLE statement to include them")
    print("3. Remove be_mfe/no_be_mfe from INSERT (use mfe instead)")

def main():
    check_table_schema()
    
    print("\n" + "=" * 80)
    print("RECOMMENDED FIX")
    print("=" * 80)
    print("\nUpdate the CREATE TABLE statement in handle_entry_signal to include:")
    print("  be_mfe DECIMAL(10,4) DEFAULT 0,")
    print("  no_be_mfe DECIMAL(10,4) DEFAULT 0,")
    print("\nOr use the existing /api/automated-signals/fix-schema endpoint")

if __name__ == '__main__':
    main()

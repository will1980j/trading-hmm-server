"""
Railway ML Health Check - Run this after deployment
"""
import os

def check_railway_ml():
    print("🔍 Railway ML Health Check")
    print("=" * 50)
    
    # Check environment
    print("\n📦 Environment:")
    print(f"   DATABASE_URL: {'✅ Set' if os.environ.get('DATABASE_URL') else '❌ Missing'}")
    
    # Check ML dependencies
    print("\n🧠 ML Dependencies:")
    try:
        import sklearn
        print(f"   ✅ scikit-learn: {sklearn.__version__}")
    except:
        print("   ❌ scikit-learn: Missing")
    
    try:
        import pandas
        print(f"   ✅ pandas: {pandas.__version__}")
    except:
        print("   ❌ pandas: Missing")
    
    try:
        import numpy
        print(f"   ✅ numpy: {numpy.__version__}")
    except:
        print("   ❌ numpy: Missing")
    
    # Check ML system
    print("\n🤖 ML System:")
    try:
        from unified_ml_intelligence import UnifiedMLIntelligence
        print("   ✅ Unified ML: Loaded")
    except Exception as e:
        print(f"   ❌ Unified ML: {e}")
    
    # Check database
    print("\n💾 Database:")
    try:
        from database.railway_db import RailwayDB
        db = RailwayDB()
        if db.conn:
            print("   ✅ Connected")
            cursor = db.conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
            result = cursor.fetchone()
            count = result['count'] if result else 0
            print(f"   ✅ Trades: {count}")
        else:
            print("   ❌ Not connected")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Health check complete!")

if __name__ == "__main__":
    check_railway_ml()

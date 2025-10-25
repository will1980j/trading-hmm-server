#!/usr/bin/env python3
"""
🔍 DIAGNOSE AUTO-TRAINING FAILURE
Find out why the ML models aren't auto-training!
"""

import sys
sys.path.append('.')

def check_auto_training():
    print("🔍 DIAGNOSING AUTO-TRAINING FAILURE")
    print("=" * 50)
    
    # 1. Check ML dependencies
    print("\n📦 Step 1: Checking ML Dependencies")
    try:
        import sklearn
        import pandas as pd
        import numpy as np
        import xgboost
        print("✅ All ML dependencies available")
        ml_available = True
    except ImportError as e:
        print(f"❌ ML dependencies missing: {e}")
        ml_available = False
        return
    
    # 2. Check database connection
    print("\n🗄️ Step 2: Checking Database Connection")
    try:
        from database.railway_db import RailwayDB
        db = RailwayDB()
        if db.connect():
            print("✅ Database connected successfully")
            db_enabled = True
        else:
            print("❌ Database connection failed")
            db_enabled = False
            return
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # 3. Check training data availability
    print("\n📊 Step 3: Checking Training Data")
    try:
        cursor = db.conn.cursor()
        
        # Check signal_lab_trades table
        cursor.execute("SELECT COUNT(*) FROM signal_lab_trades")
        total_trades = cursor.fetchone()[0]
        print(f"📈 Total trades in signal_lab_trades: {total_trades}")
        
        # Check trades with MFE data
        cursor.execute("""
            SELECT COUNT(*) FROM signal_lab_trades 
            WHERE COALESCE(mfe_none, mfe, 0) != 0
        """)
        trades_with_mfe = cursor.fetchone()[0]
        print(f"🎯 Trades with MFE data: {trades_with_mfe}")
        
        # Check recent trades
        cursor.execute("""
            SELECT date, time, bias, session, 
                   COALESCE(mfe_none, mfe, 0) as mfe
            FROM signal_lab_trades 
            ORDER BY date DESC, time DESC 
            LIMIT 5
        """)
        recent_trades = cursor.fetchall()
        print(f"📋 Recent trades:")
        for trade in recent_trades:
            print(f"   {trade[0]} {trade[1]} - {trade[2]} {trade[3]} - MFE: {trade[4]}")
            
    except Exception as e:
        print(f"❌ Error checking training data: {e}")
        return
    
    # 4. Test ML training directly
    print("\n🤖 Step 4: Testing ML Training Directly")
    try:
        from unified_ml_intelligence import get_unified_ml
        
        ml_engine = get_unified_ml(db)
        print(f"🔧 ML Engine created - Is trained: {ml_engine.is_trained}")
        
        # Try to train
        print("🎯 Attempting to train ML models...")
        result = ml_engine.train_on_all_data()
        
        if 'error' in result:
            print(f"❌ Training failed: {result['error']}")
        else:
            print(f"✅ Training successful!")
            print(f"   📊 Training samples: {result['training_samples']}")
            print(f"   🎯 Success accuracy: {result['success_accuracy']:.1f}%")
            print(f"   📈 MFE MAE: {result['mfe_mae']:.3f}R")
            
    except Exception as e:
        print(f"❌ ML training error: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Check startup conditions
    print(f"\n🚀 Step 5: Startup Conditions Check")
    print(f"   ml_available: {ml_available}")
    print(f"   db_enabled: {db_enabled}")
    print(f"   Should auto-train: {ml_available and db_enabled}")
    
    if ml_available and db_enabled:
        print("✅ All conditions met for auto-training!")
        print("🔍 Auto-training should have worked...")
        
        # Check if there are startup logs
        print("\n📝 Check your server logs for:")
        print("   🤖 Starting ML auto-train thread...")
        print("   ✅ ML auto-train thread started")
        print("   🤖 Auto-training ML on server startup...")
        print("   ✅ ML auto-trained: X samples, Y% accuracy")
        
    db.close()

if __name__ == "__main__":
    check_auto_training()
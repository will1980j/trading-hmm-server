"""
Check Auto-Optimizer Status
"""
import logging
from database.railway_db import RailwayDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_status():
    """Check current optimizer status"""
    try:
        db = RailwayDB()
        cursor = db.conn.cursor()
        
        # Check sample count
        cursor.execute("SELECT COUNT(*) as count FROM signal_lab_trades WHERE COALESCE(mfe_none, mfe, 0) != 0")
        sample_count = cursor.fetchone()['count']
        
        print(f"\n{'='*60}")
        print(f"HYPERPARAMETER OPTIMIZER STATUS")
        print(f"{'='*60}")
        print(f"📊 Training Samples Available: {sample_count}")
        print(f"✅ Minimum Required: 500 (for first run)")
        print(f"✅ Subsequent Runs: 200 new samples")
        
        if sample_count >= 500:
            print(f"\n✅ READY TO OPTIMIZE - {sample_count} samples available!")
        else:
            print(f"\n⏳ Need {500 - sample_count} more samples for first optimization")
        
        # Check if optimization has run before
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'hyperparameter_optimization_results'
            ) as exists
        """)
        table_exists = cursor.fetchone()['exists']
        
        if table_exists:
            cursor.execute("""
                SELECT COUNT(*) as count,
                       MAX(optimization_timestamp) as last_run
                FROM hyperparameter_optimization_results
            """)
            result = cursor.fetchone()
            opt_count = result['count']
            last_run = result['last_run']
            
            print(f"\n📈 Optimization History:")
            print(f"   Total Runs: {opt_count}")
            print(f"   Last Run: {last_run if last_run else 'Never'}")
            
            if opt_count > 0:
                cursor.execute("""
                    SELECT rf_params, gb_params, 
                           baseline_accuracy, optimized_accuracy, improvement_pct
                    FROM hyperparameter_optimization_results
                    ORDER BY optimization_timestamp DESC
                    LIMIT 1
                """)
                latest = cursor.fetchone()
                print(f"\n🎯 Latest Results:")
                print(f"   Baseline Accuracy: {latest['baseline_accuracy']:.2f}%")
                print(f"   Optimized Accuracy: {latest['optimized_accuracy']:.2f}%")
                print(f"   Improvement: +{latest['improvement_pct']:.2f}%")
        else:
            print(f"\n📈 Optimization History: Never run")
        
        print(f"\n{'='*60}")
        print(f"AUTO-OPTIMIZER CONFIGURATION:")
        print(f"{'='*60}")
        print(f"✅ Check Interval: Every 1 hour")
        print(f"✅ First Run Trigger: 500+ samples")
        print(f"✅ Subsequent Runs: 200+ new samples OR 30 days")
        print(f"✅ Runs on server startup if conditions met")
        
        print(f"\n{'='*60}\n")
        
        db.close()
        
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    check_status()

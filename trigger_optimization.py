"""
Manually trigger hyperparameter optimization
"""
from database.railway_db import RailwayDB
from ml_hyperparameter_optimizer import optimize_trading_models
import json

db = RailwayDB()

print("🚀 Starting manual hyperparameter optimization...")
results = optimize_trading_models(db)

if 'error' in results:
    print(f"❌ Error: {results['error']}")
else:
    print(f"✅ Optimization complete!")
    print(f"RF improvement: +{results['comparison']['rf_improvement']['accuracy']:.2f}%")
    print(f"GB improvement: +{results['comparison']['gb_improvement']['accuracy']:.2f}%")
    
    # Store in database
    cursor = db.conn.cursor()
    cursor.execute("""
        INSERT INTO hyperparameter_optimization_results 
        (rf_params, gb_params, baseline_accuracy, optimized_accuracy, 
         improvement_pct, optimization_duration_seconds)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        json.dumps(results['rf_optimization']['best_params']),
        json.dumps(results['gb_optimization']['best_params']),
        results['comparison']['baseline_rf']['accuracy'],
        results['comparison']['optimized_rf']['accuracy'],
        results['comparison']['rf_improvement']['accuracy'],
        0
    ))
    db.conn.commit()
    print("✅ Results stored in database")

db.close()

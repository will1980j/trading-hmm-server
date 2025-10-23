"""Test hyperparameter optimization integration"""
from database.railway_db import RailwayDB
from init_hyperparameter_table import init_hyperparameter_table
from hyperparameter_status import HyperparameterStatus

def test_integration():
    print("🧪 Testing Hyperparameter Optimization Integration...")
    
    try:
        # Connect to database
        db = RailwayDB()
        print("✅ Database connected")
        
        # Initialize table
        init_hyperparameter_table(db)
        print("✅ Table initialized")
        
        # Test status tracker
        tracker = HyperparameterStatus(db)
        status = tracker.get_optimization_status()
        print(f"✅ Status retrieved: {status['status']}")
        
        history = tracker.get_optimization_history()
        print(f"✅ History retrieved: {history['total_runs']} runs")
        
        print("\n🎉 Integration test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integration()

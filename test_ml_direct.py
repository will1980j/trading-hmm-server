"""Direct ML test - no web server"""
import sys
sys.path.insert(0, '.')

from database.railway_db import RailwayDB
from unified_ml_intelligence import get_unified_ml

db = RailwayDB()
ml = get_unified_ml(db)

print("Testing ML training...")
result = ml.train_on_all_data()
print(f"Result: {result}")

print("\nTesting insights...")
insights = ml.get_fundamental_insights()
print(f"Insights: {insights}")

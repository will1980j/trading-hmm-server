#!/usr/bin/env python3
"""
Print all Flask routes to verify registration.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask app the same way production does
from flask import Flask
from automated_signals_api_robust import register_automated_signals_api_robust

# Create minimal app
app = Flask(__name__)

# Mock db object (routes don't actually use it for registration)
class MockDB:
    pass

db = MockDB()

# Register routes
try:
    register_automated_signals_api_robust(app, db)
except Exception as e:
    import traceback
    print("❌ ROUTE REGISTRATION FAILED")
    print("=" * 80)
    traceback.print_exc()
    print("=" * 80)
    raise

# Print all routes
print("=" * 80)
print("FLASK ROUTES REGISTERED")
print("=" * 80)

routes = []
route_keys = []  # (methods, rule) tuples for duplicate detection

for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    routes.append((rule.rule, methods, rule.endpoint))
    
    # Track each method+rule combination
    for method in rule.methods - {'HEAD', 'OPTIONS'}:
        route_keys.append((method, rule.rule))

# Check for duplicates
from collections import Counter
route_counts = Counter(route_keys)
duplicates = [(k, v) for k, v in route_counts.items() if v > 1]

if duplicates:
    print("❌ DUPLICATES FOUND:")
    print("=" * 80)
    for (method, rule), count in duplicates:
        print(f"  {method:10} {rule:50} (registered {count} times)")
    print("=" * 80)
    print(f"TOTAL ROUTES: {len(routes)}")
    print(f"UNIQUE ROUTES: {len(route_counts)}")
    print(f"DUPLICATES: {len(duplicates)}")
    print("=" * 80)
    exit(1)

# Sort by rule
routes.sort(key=lambda x: x[0])

# Print
for rule, methods, endpoint in routes:
    print(f"{methods:10} {rule:60} -> {endpoint}")

print("=" * 80)
print(f"TOTAL ROUTES: {len(routes)}")
print(f"UNIQUE ROUTES: {len(route_counts)}")
print("=" * 80)

# Filter to indicator export routes
print("\nINDICATOR EXPORT ROUTES:")
print("-" * 80)
for rule, methods, endpoint in routes:
    if 'indicator-export' in rule or 'all-signals' in rule or 'data-quality' in rule:
        print(f"{methods:10} {rule:60} -> {endpoint}")

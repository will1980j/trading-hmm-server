"""
Test Data Quality System - Phase 1
Verify database tables and API endpoints are working
"""

import requests
import subprocess
import sys

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("DATA QUALITY SYSTEM - PHASE 1 TESTING")
print("=" * 80)
print()

# Step 1: Run database migration
print("Step 1: Running database migration...")
try:
    result = subprocess.run(
        [sys.executable, "database/run_data_quality_migration.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print("❌ Migration failed:")
        print(result.stderr)
        exit(1)
except Exception as e:
    print(f"❌ Migration error: {e}")
    exit(1)

print()

# Step 2: Test API endpoints
print("Step 2: Testing API endpoints...")
print()

endpoints = [
    ("/api/data-quality/overview", "Overview"),
    ("/api/data-quality/health", "Health Status"),
    ("/api/data-quality/conflicts?status=pending", "Conflicts List"),
    ("/api/data-quality/gaps", "Gap Analysis"),
    ("/api/data-quality/metrics?days=30", "Historical Metrics"),
    ("/api/data-quality/reconciliations?limit=10", "Reconciliation Log")
]

all_passed = True

for endpoint, name in endpoints:
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ {name}: Working")
            else:
                print(f"⚠️ {name}: Returned success=false")
                all_passed = False
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ {name}: {e}")
        all_passed = False

print()
print("=" * 80)

if all_passed:
    print("✅ PHASE 1 COMPLETE - All systems operational")
    print()
    print("Next steps:")
    print("1. Deploy to Railway (GitHub Desktop → Commit → Push)")
    print("2. Verify APIs work on production")
    print("3. Ready for Phase 2 (Backend Services)")
else:
    print("⚠️ PHASE 1 INCOMPLETE - Some tests failed")
    print("Review errors above and fix before proceeding")

print("=" * 80)

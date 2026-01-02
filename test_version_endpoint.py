"""Test /api/version endpoint"""

import requests

# Test local
print("=" * 70)
print("LOCAL VERSION ENDPOINT TEST")
print("=" * 70)

try:
    resp = requests.get("http://localhost:5000/api/version", timeout=5)
    data = resp.json()
    
    print(f"Status Code: {resp.status_code}")
    print(f"\nResponse Headers:")
    print(f"  X-App-Version: {resp.headers.get('X-App-Version', 'NOT SET')}")
    print(f"\nResponse Body:")
    print(f"  git_commit: {data.get('git_commit', 'N/A')}")
    print(f"  build_time: {data.get('build_time', 'N/A')}")
    print(f"  app_version: {data.get('app_version', 'N/A')}")
    print(f"  roadmap_version: {data.get('roadmap_version', 'N/A')}")
    print(f"  timestamp: {data.get('timestamp', 'N/A')}")
    
    print("\n✅ LOCAL TEST PASSED")
    
except requests.exceptions.ConnectionError:
    print("❌ Server not running at localhost:5000")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("PRODUCTION VERSION ENDPOINT TEST")
print("=" * 70)

try:
    resp = requests.get("https://web-production-f8c3.up.railway.app/api/version", timeout=10)
    data = resp.json()
    
    print(f"Status Code: {resp.status_code}")
    print(f"\nResponse Headers:")
    print(f"  X-App-Version: {resp.headers.get('X-App-Version', 'NOT SET')}")
    print(f"\nResponse Body:")
    print(f"  git_commit: {data.get('git_commit', 'N/A')}")
    print(f"  build_time: {data.get('build_time', 'N/A')}")
    print(f"  app_version: {data.get('app_version', 'N/A')}")
    print(f"  roadmap_version: {data.get('roadmap_version', 'N/A')}")
    
    # Check if this is the new version
    expected_version = "homepage-hardening-2025-01-02"
    if data.get('app_version') == expected_version:
        print(f"\n✅ PRODUCTION IS RUNNING NEW VERSION: {expected_version}")
    else:
        print(f"\n⚠️  PRODUCTION IS RUNNING OLD VERSION: {data.get('app_version')}")
        print(f"   Expected: {expected_version}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)

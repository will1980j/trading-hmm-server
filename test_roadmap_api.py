"""Test the /api/roadmap endpoint"""

import requests

url = "http://localhost:5000/api/roadmap"

try:
    resp = requests.get(url, timeout=5)
    data = resp.json()
    
    print("=" * 60)
    print("API ROADMAP ENDPOINT TEST")
    print("=" * 60)
    print(f"Status Code: {resp.status_code}")
    print(f"Version: {data.get('version', 'unknown')}")
    print(f"Phases: {len(data.get('phases', []))}")
    print(f"Current Focus: {data.get('overall', {}).get('active_phase_name', 'unknown')}")
    print()
    
    print("Phase Listing:")
    for phase in data.get('phases', []):
        print(f"  {phase['phase_id']:4} → {phase['name']:45} | {phase['status']}")
    
    print()
    print("Overall Progress:")
    overall = data.get('overall', {})
    print(f"  Phases: {overall.get('phases_done', 0)}/{overall.get('phases_total', 0)} ({overall.get('phase_percent', 0)}%)")
    print(f"  Modules: {overall.get('modules_done', 0)}/{overall.get('modules_total', 0)} ({overall.get('module_percent', 0)}%)")
    
    print()
    print("✅ API TEST PASSED")
    
except requests.exceptions.ConnectionError:
    print("❌ Server not running at localhost:5000")
except Exception as e:
    print(f"❌ Error: {e}")

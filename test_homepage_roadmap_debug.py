#!/usr/bin/env python3
"""Quick test to verify roadmap data generation for homepage."""

import sys
sys.path.insert(0, '.')

from roadmap_state import phase_progress_snapshot, ROADMAP

def test_roadmap_data():
    print("=" * 60)
    print("TESTING ROADMAP DATA GENERATION")
    print("=" * 60)
    
    # Test 1: Get raw snapshot
    print("\n1. Testing phase_progress_snapshot()...")
    try:
        snapshot = phase_progress_snapshot()
        print(f"   ✅ Got {len(snapshot)} phases")
        print(f"   Keys: {list(snapshot.keys())}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return False
    
    # Test 2: Build module lists (same as homepage route)
    print("\n2. Building roadmap_snapshot with module_list...")
    roadmap_snapshot = {}
    try:
        for phase_id, pdata in snapshot.items():
            raw_phase = ROADMAP.get(phase_id)
            raw_modules = getattr(raw_phase, "modules", {}) or {}
            module_list = []
            for key, status in raw_modules.items():
                done = getattr(status, "completed", status)
                title = key.replace("_", " ").title()
                desc = getattr(status, "description", "") or ""
                module_list.append({
                    "key": key,
                    "title": title,
                    "done": bool(done),
                    "description": desc
                })
            
            roadmap_snapshot[phase_id] = {
                **pdata,
                "module_list": module_list
            }
        
        print(f"   ✅ Built roadmap_snapshot with {len(roadmap_snapshot)} phases")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Show first phase details
    print("\n3. First phase details:")
    if roadmap_snapshot:
        first_key = sorted(roadmap_snapshot.keys())[0]
        first_phase = roadmap_snapshot[first_key]
        print(f"   Phase ID: {first_key}")
        print(f"   Name: {first_phase.get('name')}")
        print(f"   Description: {first_phase.get('description', '')[:80]}...")
        print(f"   Modules: {first_phase.get('modules')}")
        print(f"   Completed: {first_phase.get('completed')}")
        print(f"   Percent: {first_phase.get('percent')}%")
        print(f"   Module list count: {len(first_phase.get('module_list', []))}")
    
    # Test 4: Check for "Databento Foundation" phase
    print("\n4. Looking for 'Databento Foundation' phase...")
    found = False
    for pid, phase in roadmap_snapshot.items():
        if 'Databento' in phase.get('name', ''):
            print(f"   ✅ Found: Phase {pid} = '{phase.get('name')}'")
            found = True
            break
    if not found:
        print("   ⚠️ No phase with 'Databento' in name found")
        print("   Available phase names:")
        for pid, phase in sorted(roadmap_snapshot.items()):
            print(f"      {pid}: {phase.get('name')}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_roadmap_data()
    sys.exit(0 if success else 1)

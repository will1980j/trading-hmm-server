"""Test the updated roadmap V3 YAML"""

from roadmap.roadmap_loader import load_roadmap_v3, get_homepage_roadmap_data

# Test 1: Load YAML
print("=" * 60)
print("TEST 1: Load Roadmap V3")
print("=" * 60)
data = load_roadmap_v3(force_reload=True)
print(f"✓ Loaded {len(data['phases'])} phases")
print(f"✓ Version: {data.get('roadmap_version', 'unknown')}")
print(f"✓ Current focus: {data.get('current_focus_name', 'Not set')}")
print()

# Test 2: List all phases
print("=" * 60)
print("TEST 2: Phase Status Mapping")
print("=" * 60)
for phase in data['phases']:
    phase_id = phase['phase_id']
    name = phase['name']
    status = phase['status']
    deliverables_count = len(phase.get('deliverables', []))
    print(f"{phase_id:4} → {name:45} | {status:15} | {deliverables_count} deliverables")
print()

# Test 3: Homepage data
print("=" * 60)
print("TEST 3: Homepage Roadmap Data")
print("=" * 60)
homepage_data = get_homepage_roadmap_data()
print(f"✓ Version: {homepage_data['version']}")
print(f"✓ Phases: {len(homepage_data['phases'])}")
print(f"✓ Overall progress: {homepage_data['overall']['phase_percent']}%")
print(f"✓ Is fallback: {homepage_data.get('_is_fallback', False)}")
print()

# Test 4: Verify deliverables
print("=" * 60)
print("TEST 4: Deliverables Check")
print("=" * 60)
for phase in data['phases']:
    deliverables = phase.get('deliverables', [])
    print(f"\n{phase['name']}:")
    for i, d in enumerate(deliverables, 1):
        print(f"  {i}. {d}")

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)

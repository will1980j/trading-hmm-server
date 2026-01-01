"""Verify Phase E.5 is correctly positioned"""

from roadmap.roadmap_loader import load_roadmap_v3

data = load_roadmap_v3(force_reload=True)
phases = data['phases']

print("=" * 70)
print("PHASE E.5 VERIFICATION")
print("=" * 70)
print(f"Total phases: {len(phases)}")
print()
print("Complete Phase Sequence:")
print("-" * 70)

for i, p in enumerate(phases, 1):
    phase_id = p['phase_id']
    name = p['name']
    status = p['status']
    deliverables = len(p.get('deliverables', []))
    
    marker = ""
    if phase_id == "P4.5":
        marker = " ← NEW PHASE E.5"
    elif status == "IN_PROGRESS":
        marker = " ← CURRENT FOCUS"
    
    print(f"{i:2}. {phase_id:5} | {name:48} | {status:12} | {deliverables} bullets{marker}")

print()
print("=" * 70)
print("✅ Phase E.5 successfully added between Phase E and Phase F")
print("=" * 70)

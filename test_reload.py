import importlib
import sys
sys.path.insert(0, '.')
from roadmap import roadmap_loader
importlib.reload(roadmap_loader)
snapshot, err, path, exists, yaml_ok = roadmap_loader.build_v3_snapshot()
print(f'snapshot keys: {list(snapshot.keys()) if snapshot else None}')
print(f'overall: {snapshot.get("overall") if snapshot else None}')
if snapshot:
    for phase in snapshot.get('phases', [])[:2]:
        print(f'Phase {phase.get("phase_id")}: modules_done={phase.get("modules_done")}, modules_total={phase.get("modules_total")}')

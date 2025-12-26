#!/usr/bin/env python3
"""Display complete Unified Roadmap v3 with all phases and modules"""

import yaml
from pathlib import Path

# Load the roadmap
roadmap_path = Path("roadmap/unified_roadmap_v3.yaml")

with open(roadmap_path, 'r', encoding='utf-8') as f:
    roadmap = yaml.safe_load(f)

print("=" * 100)
print(f"UNIFIED ROADMAP V3 - VERSION {roadmap['roadmap_version']}")
print("=" * 100)
print(f"Created: {roadmap['created_date']}")
print(f"Last Updated: {roadmap['last_updated']}")
print()

# Display phases
phases = roadmap.get('phases', [])
print(f"Total Phases: {len(phases)}")
print()

for phase in phases:
    phase_id = phase.get('phase_id', '?')
    name = phase.get('name', 'Unnamed')
    objective = phase.get('objective', 'No objective')
    status = phase.get('status', 'UNKNOWN')
    modules = phase.get('modules', [])
    
    print("=" * 100)
    print(f"PHASE {phase_id}: {name}")
    print("=" * 100)
    print(f"Status: {status}")
    print(f"Objective: {objective}")
    print(f"Modules: {len(modules)}")
    print()
    
    for i, module in enumerate(modules, 1):
        module_id = module.get('module_id', '?')
        title = module.get('title', 'Untitled')
        description = module.get('description', 'No description')
        mod_status = module.get('status', 'UNKNOWN')
        dashboards = module.get('dashboards_affected', [])
        tasks = module.get('tasks', [])
        
        print(f"  {i}. [{module_id}] {title}")
        print(f"     Status: {mod_status}")
        print(f"     Description: {description}")
        print(f"     Dashboards: {', '.join(dashboards) if dashboards else 'None'}")
        print(f"     Tasks: {len(tasks)}")
        print()

print("=" * 100)
print("SUMMARY")
print("=" * 100)

# Count modules by status
total_modules = 0
complete_modules = 0
in_progress_modules = 0
planned_modules = 0

for phase in phases:
    for module in phase.get('modules', []):
        total_modules += 1
        status = module.get('status', 'UNKNOWN')
        if status == 'COMPLETE':
            complete_modules += 1
        elif status == 'IN_PROGRESS':
            in_progress_modules += 1
        elif status == 'PLANNED':
            planned_modules += 1

print(f"Total Modules: {total_modules}")
print(f"  Complete: {complete_modules}")
print(f"  In Progress: {in_progress_modules}")
print(f"  Planned: {planned_modules}")
print(f"  Completion: {(complete_modules / total_modules * 100):.1f}%")
print("=" * 100)

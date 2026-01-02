"""Add deliverables/rules/description to roadmap loader snapshot"""

with open('roadmap/roadmap_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the phases_out.append block
old_block = '''            phases_out.append({
                "phase_id": phase_id,
                "name": name,
                "objective": objective,
                "status": status,
                "is_complete": is_complete,'''

new_block = '''            phases_out.append({
                "phase_id": phase_id,
                "name": name,
                "objective": objective,
                "status": status,
                "description": phase.get("description", ""),
                "deliverables": phase.get("deliverables", []),
                "rules": phase.get("rules", []),
                "is_complete": is_complete,'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('roadmap/roadmap_loader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed roadmap_loader.py - added deliverables/rules/description")
else:
    print("❌ Pattern not found - file may already be fixed or has different format")

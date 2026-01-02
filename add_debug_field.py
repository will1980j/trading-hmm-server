"""Add _debug field to roadmap loader"""

with open('roadmap/roadmap_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add _debug field after rules
old = '"rules": phase.get("rules", []),'
new = '"rules": phase.get("rules", []),\n                "_debug": "deliverables_enabled",'

if old in content:
    content = content.replace(old, new)
    with open('roadmap/roadmap_loader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Added _debug field")
else:
    print("❌ Pattern not found")

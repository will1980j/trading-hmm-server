"""
Compare root and templates automated_signals_dashboard.html files
"""

# Read both files
with open('automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    root_content = f.read()

with open('templates/automated_signals_dashboard.html', 'r', encoding='utf-8') as f:
    templates_content = f.read()

print("=" * 80)
print("DASHBOARD FILE COMPARISON")
print("=" * 80)

print(f"\nRoot file size: {len(root_content)} characters")
print(f"Templates file size: {len(templates_content)} characters")
print(f"Difference: {len(templates_content) - len(root_content)} characters")

# Check for key features
features_to_check = [
    ("System Health Monitor", "SYSTEM HEALTH MONITOR"),
    ("Health API call", "/api/system-health"),
    ("Calendar functionality", "calendar"),
    ("WebSocket connection", "socket.io"),
    ("Activity Feed", "Activity Feed"),
    ("Delete button", "deleteSignal"),
    ("Stats display", "stats-grid"),
]

print("\n" + "=" * 80)
print("FEATURE COMPARISON")
print("=" * 80)

for feature_name, search_term in features_to_check:
    in_root = search_term in root_content
    in_templates = search_term in templates_content
    
    status = ""
    if in_root and in_templates:
        status = "✅ Both have it"
    elif in_templates and not in_root:
        status = "⚠️  ONLY in templates (MISSING from root)"
    elif in_root and not in_templates:
        status = "⚠️  ONLY in root (MISSING from templates)"
    else:
        status = "❌ Neither has it"
    
    print(f"\n{feature_name}:")
    print(f"  {status}")

# Find unique sections in templates
print("\n" + "=" * 80)
print("UNIQUE CONTENT IN TEMPLATES VERSION")
print("=" * 80)

# Check for health monitor section
if "SYSTEM HEALTH MONITOR" in templates_content and "SYSTEM HEALTH MONITOR" not in root_content:
    print("\n✅ Templates has System Health Monitor (NEW FEATURE)")
    print("   - Health status bar")
    print("   - 5 component checks (Database, Webhooks, Events, Data, API)")
    print("   - Auto-refresh every 60 seconds")
    print("   - Expandable details panel")

# Check for other differences
if "refreshHealth" in templates_content and "refreshHealth" not in root_content:
    print("\n✅ Templates has health refresh function")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)

if len(templates_content) > len(root_content):
    print("\n⚠️  Templates version is NEWER and has MORE features")
    print("   The templates version includes the System Health Monitor")
    print("   that was just built in this session.")
    print("\n   RECOMMENDED ACTION:")
    print("   1. Review both files to ensure no unique root features exist")
    print("   2. If root has nothing unique, copy templates → root")
    print("   3. If root has unique features, manually merge them")
else:
    print("\n✅ Root version appears to be current")

print("\n" + "=" * 80)

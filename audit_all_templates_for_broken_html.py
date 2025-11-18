"""
COMPREHENSIVE AUDIT: Find all broken HTML attributes in templates
"""
import os
import re

print("=" * 60)
print("COMPREHENSIVE TEMPLATE AUDIT")
print("=" * 60)

templates_dir = "templates"
issues_found = []

# Pattern to find tags with missing spaces between attributes
# Looks for: <tagname="value" or attribute="value"attribute2="value"
broken_patterns = [
    (r'<([a-z]+)([a-z]+)=', 'Missing space after tag name'),
    (r'="([^"]*)"([a-z]+)=', 'Missing space between attributes'),
    (r'([a-z]+)([a-z]+)=', 'Concatenated attributes'),
]

for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(templates_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📄 Checking: {filename}")
        
        # Check for specific known issues
        if '<videoid=' in content:
            issues_found.append(f"{filename}: <videoid= (should be <video id=)")
            print(f"  ❌ Found: <videoid=")
        
        if '<inputtype=' in content:
            issues_found.append(f"{filename}: <inputtype= (should be <input type=)")
            print(f"  ❌ Found: <inputtype=")
        
        # Check for attributes without spaces
        if re.search(r'="[^"]*"[a-z]+=', content):
            issues_found.append(f"{filename}: Attributes without spaces")
            print(f"  ❌ Found: Concatenated attributes")
            # Show examples
            matches = re.findall(r'="[^"]*"[a-z]+="[^"]*"', content)
            for match in matches[:3]:
                print(f"     Example: {match}")
        
        if not any(issue.startswith(filename) for issue in issues_found):
            print(f"  ✅ No issues found")

print("\n" + "=" * 60)
print("AUDIT SUMMARY")
print("=" * 60)

if issues_found:
    print(f"\n❌ Found {len(issues_found)} files with issues:\n")
    for issue in issues_found:
        print(f"  • {issue}")
else:
    print("\n✅ All templates are clean!")

print("\n" + "=" * 60)

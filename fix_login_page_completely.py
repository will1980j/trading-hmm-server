"""
Fix ALL broken HTML attributes in login page
"""
import re

print("=" * 60)
print("FIXING LOGIN PAGE HTML")
print("=" * 60)

with open('templates/login_video_background.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("\n🔧 Applying fixes...")

# Fix video tag
content = re.sub(
    r'<video([a-z]+)="([^"]*)"',
    r'<video \1="\2"',
    content
)

# Fix input tags - be very specific
content = content.replace(
    '<input type="text"name="username"',
    '<input type="text" name="username"'
)
content = content.replace(
    '<input type="password"name="password"',
    '<input type="password" name="password"'
)

# Fix all attribute concatenations
content = re.sub(
    r'="([^"]*)"([a-z]+)=',
    r'="\1" \2=',
    content
)

print("✅ Fixed video tag")
print("✅ Fixed input tags")
print("✅ Fixed attribute spacing")

with open('templates/login_video_background.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Login page fixed and saved")

# Verify the fix
with open('templates/login_video_background.html', 'r', encoding='utf-8') as f:
    verify = f.read()

issues = []
if '<videoid=' in verify:
    issues.append("<videoid= still present")
if '<inputtype=' in verify:
    issues.append("<inputtype= still present")
if re.search(r'="[^"]*"[a-z]+=', verify):
    issues.append("Concatenated attributes still present")

if issues:
    print("\n❌ VERIFICATION FAILED:")
    for issue in issues:
        print(f"  • {issue}")
else:
    print("\n✅ VERIFICATION PASSED - All issues fixed!")

print("\n" + "=" * 60)

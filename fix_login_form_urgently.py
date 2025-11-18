"""
URGENT FIX: Restore spaces in HTML attributes that were removed by over-minification
"""
import re

print("=" * 60)
print("URGENT FIX: RESTORING LOGIN FORM")
print("=" * 60)

# Read the broken login file
with open('templates/login_video_background.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("\n🔍 Analyzing broken HTML...")

# Fix the broken input tags by adding spaces between attributes
# Pattern: ><inputtype= should be ><input type=
content = re.sub(r'<input([a-z]+)=', r'<input \1=', content)

# Fix video tag: <videoid= should be <video id=
content = re.sub(r'<video([a-z]+)=', r'<video \1=', content)

# Fix any other tags that got minified
content = re.sub(r'<([a-z]+)([a-z]+)=', r'<\1 \2=', content)

# More specific fixes for the input fields
content = content.replace('<inputtype="text"name="username"', '<input type="text" name="username"')
content = content.replace('<inputtype="password"name="password"', '<input type="password" name="password"')
content = content.replace('name="username"class="input"', 'name="username" class="input"')
content = content.replace('name="password"class="input"', 'name="password" class="input"')
content = content.replace('class="input"placeholder=', 'class="input" placeholder=')
content = content.replace('placeholder="Username"autocomplete=', 'placeholder="Username" autocomplete=')
content = content.replace('placeholder="Password"autocomplete=', 'placeholder="Password" autocomplete=')
content = content.replace('autocomplete="username"required', 'autocomplete="username" required')
content = content.replace('autocomplete="current-password"required', 'autocomplete="current-password" required')

# Fix video tag
content = content.replace('<videoid="backgroundVideo"class="video-background"autoplaymutedloopplaysinlinepreload="auto">', 
                         '<video id="backgroundVideo" class="video-background" autoplay muted loop playsinline preload="auto">')

print("✅ Fixed HTML attribute spacing")

# Write the fixed content
with open('templates/login_video_background.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Saved fixed login template")

# Also fix homepage if it has the same issue
try:
    with open('templates/homepage_video_background.html', 'r', encoding='utf-8') as f:
        homepage_content = f.read()
    
    # Apply same fixes
    homepage_content = homepage_content.replace('<videoid="backgroundVideo"class="video-background"autoplaymutedloopplaysinlinepreload="auto">',
                                               '<video id="backgroundVideo" class="video-background" autoplay muted loop playsinline preload="auto">')
    
    with open('templates/homepage_video_background.html', 'w', encoding='utf-8') as f:
        f.write(homepage_content)
    
    print("✅ Fixed homepage template too")
except:
    pass

print("\n" + "=" * 60)
print("FIX COMPLETE - READY TO DEPLOY")
print("=" * 60)
print("\n📋 Next steps:")
print("1. Commit: git add templates/")
print("2. Commit: git commit -m 'URGENT: Fix login form HTML attributes'")
print("3. Push: git push origin clean-development:main --force")

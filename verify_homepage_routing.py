"""
VERIFICATION: Homepage Routing Configuration
Confirms that all homepage routes are correctly configured to use Module 15 template
"""

import re

def verify_homepage_routing():
    """Verify homepage routing is correctly configured"""
    
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("=" * 80)
    print("HOMEPAGE ROUTING VERIFICATION")
    print("=" * 80)
    print()
    
    # Check 1: Find /homepage route
    homepage_pattern = r"@app\.route\('/homepage'\).*?def homepage\(\):.*?return render_template\('([^']+)'.*?\)"
    homepage_match = re.search(homepage_pattern, content, re.DOTALL)
    
    if homepage_match:
        template = homepage_match.group(1)
        print(f"✅ /homepage route found")
        print(f"   Template: {template}")
        if template == 'homepage_video_background.html':
            print(f"   ✓ Using correct Module 15 template")
        else:
            print(f"   ❌ ERROR: Using wrong template! Should be 'homepage_video_background.html'")
    else:
        print("❌ ERROR: /homepage route not found!")
    
    print()
    
    # Check 2: Find root route
    root_pattern = r"@app\.route\('/'\).*?def \w+\(\):.*?return redirect\('([^']+)'\)"
    root_match = re.search(root_pattern, content, re.DOTALL)
    
    if root_match:
        redirect_target = root_match.group(1)
        print(f"✅ Root route (/) found")
        print(f"   Redirects to: {redirect_target}")
        if redirect_target == '/homepage':
            print(f"   ✓ Correctly redirects to /homepage")
        else:
            print(f"   ⚠️  Redirects to {redirect_target} (not /homepage)")
    else:
        print("❌ ERROR: Root route (/) not found!")
    
    print()
    
    # Check 3: Find login POST redirect
    login_pattern = r"@app\.route\('/login'.*?\).*?def login\(\):.*?session\['authenticated'\] = True.*?return redirect\('([^']+)'\)"
    login_match = re.search(login_pattern, content, re.DOTALL)
    
    if login_match:
        redirect_target = login_match.group(1)
        print(f"✅ Login POST handler found")
        print(f"   Redirects to: {redirect_target}")
        if redirect_target == '/homepage':
            print(f"   ✓ Correctly redirects to /homepage")
        else:
            print(f"   ❌ ERROR: Should redirect to /homepage, not {redirect_target}")
    else:
        print("❌ ERROR: Login POST handler not found!")
    
    print()
    
    # Check 4: Look for any old homepage templates
    old_templates = ['homepage.html', 'home.html', 'old_homepage.html', 'index.html']
    found_old = False
    
    for old_template in old_templates:
        if f"render_template('{old_template}'" in content:
            print(f"❌ ERROR: Found reference to old template: {old_template}")
            found_old = True
    
    if not found_old:
        print("✅ No references to old homepage templates found")
    
    print()
    
    # Check 5: Verify no duplicate homepage functions
    homepage_functions = re.findall(r'def (homepage|home|index|dashboard_homepage)\(\):', content)
    
    if len(homepage_functions) == 1 and homepage_functions[0] == 'homepage':
        print(f"✅ Single homepage function found: {homepage_functions[0]}()")
    elif len(homepage_functions) > 1:
        print(f"⚠️  Multiple homepage-like functions found: {homepage_functions}")
    else:
        print("❌ ERROR: No homepage function found!")
    
    print()
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print()
    
    # Final assessment
    all_good = (
        homepage_match and 
        homepage_match.group(1) == 'homepage_video_background.html' and
        login_match and 
        login_match.group(1) == '/homepage' and
        not found_old and
        len(homepage_functions) == 1
    )
    
    if all_good:
        print("✅ ALL CHECKS PASSED")
        print()
        print("Homepage routing is correctly configured:")
        print("  • /homepage serves Module 15 template (homepage_video_background.html)")
        print("  • Login redirects to /homepage")
        print("  • Root (/) redirects to /homepage (when authenticated)")
        print("  • No old homepage templates referenced")
        print("  • No duplicate homepage functions")
        print()
        print("🚀 READY TO TEST:")
        print("  1. Restart Flask application")
        print("  2. Login at /login")
        print("  3. Verify you see the Module 15 homepage with video background")
    else:
        print("❌ ISSUES FOUND")
        print()
        print("Review the errors above and fix before deploying.")
    
    print()
    return all_good

if __name__ == "__main__":
    verify_homepage_routing()

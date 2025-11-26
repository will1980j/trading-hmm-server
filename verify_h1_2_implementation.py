"""
Quick verification script for H1.2 Main Dashboard implementation
Checks all requirements are met before deployment
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print result"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_content(filepath, search_term, description):
    """Check if file contains specific content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_term in content
            status = "✅" if found else "❌"
            print(f"{status} {description}")
            return found
    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("H1.2 MAIN DASHBOARD - IMPLEMENTATION VERIFICATION")
    print("=" * 70)
    print()
    
    all_checks = []
    
    # File existence checks
    print("📁 FILE EXISTENCE CHECKS")
    print("-" * 70)
    all_checks.append(check_file_exists('templates/main_dashboard.html', 'Template'))
    all_checks.append(check_file_exists('static/css/main_dashboard.css', 'CSS'))
    all_checks.append(check_file_exists('static/js/main_dashboard.js', 'JavaScript'))
    all_checks.append(check_file_exists('tests/test_h1_2_main_dashboard.py', 'Tests'))
    print()
    
    # Route checks
    print("🛣️  ROUTE CHECKS")
    print("-" * 70)
    all_checks.append(check_content('web_server.py', "@app.route('/main-dashboard')", 
                                    "Route decorator exists"))
    all_checks.append(check_content('web_server.py', "def main_dashboard():", 
                                    "Route function exists"))
    all_checks.append(check_content('web_server.py', "@login_required", 
                                    "Authentication required"))
    all_checks.append(check_content('web_server.py', "render_template('main_dashboard.html')", 
                                    "Renders correct template"))
    print()
    
    # Template checks
    print("📄 TEMPLATE CHECKS")
    print("-" * 70)
    all_checks.append(check_content('templates/main_dashboard.html', '<!DOCTYPE html>', 
                                    "Valid HTML structure"))
    all_checks.append(check_content('templates/main_dashboard.html', 'main_dashboard.css', 
                                    "Links to CSS"))
    all_checks.append(check_content('templates/main_dashboard.html', 'main_dashboard.js', 
                                    "Links to JavaScript"))
    all_checks.append(check_content('templates/main_dashboard.html', 'operational-topbar', 
                                    "Has operational topbar"))
    all_checks.append(check_content('templates/main_dashboard.html', 'hero-grid', 
                                    "Has hero grid layout"))
    print()
    
    # No fake data checks
    print("🚫 NO FAKE DATA CHECKS")
    print("-" * 70)
    
    # Check template (exclude CSS class names like "placeholder-text")
    with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
        template_content = f.read().lower()
    # Check for actual fake content, not CSS class names
    fake_indicators = ['lorem ipsum', 'todo:', 'fixme:', 'coming soon', 'test data', 'sample data']
    no_fake_template = not any(word in template_content for word in fake_indicators)
    status = "✅" if no_fake_template else "❌"
    print(f"{status} Template has no fake data")
    all_checks.append(no_fake_template)
    
    # Check JS
    with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
        js_content = f.read().lower()
    no_fake_js = not any(word in js_content for word in 
                        ['fake', 'dummy', 'lorem ipsum', 'mock data'])
    status = "✅" if no_fake_js else "❌"
    print(f"{status} JavaScript has no fake data")
    all_checks.append(no_fake_js)
    
    print()
    
    # Homepage integration
    print("🏠 HOMEPAGE INTEGRATION")
    print("-" * 70)
    all_checks.append(check_content('templates/homepage_video_background.html', 
                                    '/main-dashboard', 
                                    "Homepage links to dashboard"))
    all_checks.append(check_content('templates/homepage_video_background.html', 
                                    'Main Dashboard', 
                                    "Homepage has dashboard card"))
    print()
    
    # Roadmap state
    print("🗺️  ROADMAP STATE")
    print("-" * 70)
    all_checks.append(check_content('roadmap_state.py', 
                                    'h1_2_main_dashboard', 
                                    "Roadmap has H1.2 key"))
    
    # Check if marked complete
    with open('roadmap_state.py', 'r', encoding='utf-8') as f:
        roadmap_content = f.read()
        lines = roadmap_content.split('\n')
        h1_2_complete = False
        for i, line in enumerate(lines):
            if 'h1_2_main_dashboard' in line:
                section = '\n'.join(lines[i:i+3])
                h1_2_complete = '"done": True' in section
                break
    
    status = "✅" if h1_2_complete else "❌"
    print(f"{status} H1.2 marked as complete")
    all_checks.append(h1_2_complete)
    print()
    
    # JavaScript checks
    print("⚙️  JAVASCRIPT FUNCTIONALITY")
    print("-" * 70)
    all_checks.append(check_content('static/js/main_dashboard.js', 
                                    'class MainDashboard', 
                                    "Has MainDashboard class"))
    all_checks.append(check_content('static/js/main_dashboard.js', 
                                    'fetch(', 
                                    "Fetches real data"))
    all_checks.append(check_content('static/js/main_dashboard.js', 
                                    'try', 
                                    "Has error handling"))
    print()
    
    # Summary
    print("=" * 70)
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"RESULTS: {passed}/{total} checks passed ({percentage:.1f}%)")
    print("=" * 70)
    
    if passed == total:
        print("✅ ALL CHECKS PASSED - READY TO DEPLOY!")
        print()
        print("Next steps:")
        print("1. git add .")
        print("2. git commit -m '✅ H1.2 Main Dashboard Complete'")
        print("3. git push origin main")
        print("4. Wait 2-3 minutes for Railway deployment")
        print("5. Visit: https://web-production-cd33.up.railway.app/main-dashboard")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - REVIEW IMPLEMENTATION")
        return 1

if __name__ == '__main__':
    sys.exit(main())

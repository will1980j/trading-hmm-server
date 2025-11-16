"""
Verify navigation consistency across all dashboard files
"""

import os
import re

DASHBOARD_FILES = [
    'homepage.html',
    'ml_feature_dashboard.html',
    'signal_lab_dashboard.html',
    'signal_analysis_lab.html',
    'automated_signals_dashboard.html',
    'time_analysis.html',
    'strategy_optimizer.html',
    'strategy_comparison.html',
    'ai_business_dashboard.html',
    'prop_firm_management.html',
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html',
]

# Expected navigation links in order
EXPECTED_LINKS = [
    '/ml-dashboard',
    '/signal-lab-dashboard',
    '/signal-analysis-lab',
    '/automated-signals',
    '/time-analysis',
    '/strategy-optimizer',
    '/strategy-comparison',
    '/ai-business-advisor',
    '/prop-portfolio',
    '/trade-manager',
    '/financial-summary',
    '/reporting-hub',
]

def check_file_navigation(file_path):
    """Check if file has correct navigation"""
    
    if not os.path.exists(file_path):
        return {
            'exists': False,
            'has_nav': False,
            'has_css': False,
            'links': [],
            'errors': [f"File not found: {file_path}"]
        }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for nav container
    has_nav = '<nav class="nav-container">' in content
    
    # Check for nav CSS
    has_css = '.nav-container' in content and '.nav-link' in content
    
    # Extract all navigation links
    link_pattern = r'<a href="([^"]+)" class="nav-link">'
    links = re.findall(link_pattern, content)
    
    # Check for errors
    errors = []
    if not has_nav:
        errors.append("Missing <nav class=\"nav-container\">")
    if not has_css:
        errors.append("Missing navigation CSS")
    
    # Check link order
    if links != EXPECTED_LINKS:
        if len(links) != len(EXPECTED_LINKS):
            errors.append(f"Wrong number of links: {len(links)} (expected {len(EXPECTED_LINKS)})")
        else:
            for i, (actual, expected) in enumerate(zip(links, EXPECTED_LINKS)):
                if actual != expected:
                    errors.append(f"Link {i+1} mismatch: '{actual}' (expected '{expected}')")
    
    return {
        'exists': True,
        'has_nav': has_nav,
        'has_css': has_css,
        'links': links,
        'errors': errors
    }

def main():
    """Verify all files"""
    print("🔍 NAVIGATION CONSISTENCY VERIFICATION")
    print("="*70)
    
    all_good = True
    results = {}
    
    for file_path in DASHBOARD_FILES:
        result = check_file_navigation(file_path)
        results[file_path] = result
        
        print(f"\n📄 {file_path}")
        print("-" * 70)
        
        if not result['exists']:
            print("❌ FILE NOT FOUND")
            all_good = False
            continue
        
        # Check navigation
        if result['has_nav']:
            print("✅ Navigation HTML present")
        else:
            print("❌ Navigation HTML missing")
            all_good = False
        
        # Check CSS
        if result['has_css']:
            print("✅ Navigation CSS present")
        else:
            print("❌ Navigation CSS missing")
            all_good = False
        
        # Check links
        if len(result['links']) == len(EXPECTED_LINKS):
            print(f"✅ All {len(EXPECTED_LINKS)} navigation links present")
        else:
            print(f"❌ Link count mismatch: {len(result['links'])}/{len(EXPECTED_LINKS)}")
            all_good = False
        
        # Show errors
        if result['errors']:
            print("\n⚠️  Issues found:")
            for error in result['errors']:
                print(f"   • {error}")
            all_good = False
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    total = len(DASHBOARD_FILES)
    with_nav = sum(1 for r in results.values() if r.get('has_nav', False))
    with_css = sum(1 for r in results.values() if r.get('has_css', False))
    correct_links = sum(1 for r in results.values() if r.get('links') == EXPECTED_LINKS)
    
    print(f"Total files: {total}")
    print(f"With navigation HTML: {with_nav}/{total}")
    print(f"With navigation CSS: {with_css}/{total}")
    print(f"With correct links: {correct_links}/{total}")
    
    if all_good:
        print("\n✅ ALL FILES HAVE CONSISTENT NAVIGATION!")
        print("\n🎯 Ready to deploy:")
        print("   1. Commit changes via GitHub Desktop")
        print("   2. Push to main branch")
        print("   3. Railway will auto-deploy")
        return True
    else:
        print("\n❌ ISSUES FOUND - Review errors above")
        print("\n🔧 Run standardize_navigation.py again to fix")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

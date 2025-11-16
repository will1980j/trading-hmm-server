"""
PROPER visual audit - check what navigation actually LOOKS like on each page
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

def extract_full_nav_section(content):
    """Extract the complete navigation section including all HTML and positioning"""
    
    # Find nav container
    nav_match = re.search(r'(<nav[^>]*class="nav-container"[^>]*>.*?</nav>)', content, re.DOTALL)
    if not nav_match:
        return None
    
    nav_html = nav_match.group(1)
    
    # Count links
    links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', nav_html)
    
    # Check if nav is inside any container
    before_nav = content[:nav_match.start()]
    parent_containers = re.findall(r'<(div|header|section)[^>]*class="([^"]*)"[^>]*>', before_nav[-500:])
    
    return {
        'html': nav_html,
        'link_count': len(links),
        'links': links,
        'parent_containers': parent_containers[-3:] if parent_containers else [],
        'has_wrapper': 'dashboard-container' in before_nav[-200:] or 'container' in before_nav[-200:]
    }

def extract_nav_css(content):
    """Extract navigation CSS"""
    
    # Find nav-container CSS
    nav_css_match = re.search(r'\.nav-container\s*{([^}]+)}', content, re.DOTALL)
    nav_link_css_match = re.search(r'\.nav-link\s*{([^}]+)}', content, re.DOTALL)
    nav_hover_css_match = re.search(r'\.nav-link:hover\s*{([^}]+)}', content, re.DOTALL)
    
    css_info = {}
    
    if nav_css_match:
        css_text = nav_css_match.group(1)
        # Extract key properties
        css_info['background'] = re.search(r'background:\s*([^;]+)', css_text)
        css_info['padding'] = re.search(r'padding:\s*([^;]+)', css_text)
        css_info['display'] = re.search(r'display:\s*([^;]+)', css_text)
        css_info['justify'] = re.search(r'justify-content:\s*([^;]+)', css_text)
        css_info['align'] = re.search(r'align-items:\s*([^;]+)', css_text)
        
        # Convert to strings
        for key in css_info:
            if css_info[key]:
                css_info[key] = css_info[key].group(1).strip()
    
    return css_info

def audit_file(file_path):
    """Audit a single file's navigation"""
    
    if not os.path.exists(file_path):
        return {'error': 'File not found'}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    nav_section = extract_full_nav_section(content)
    css_info = extract_nav_css(content)
    
    # Check for old navigation patterns
    old_nav_patterns = [
        ('navbar', '<nav class="navbar'),
        ('nav-pills', 'nav-pills'),
        ('nav-tabs', 'nav-tabs'),
        ('bootstrap nav', 'class="nav '),
        ('centered nav', 'justify-content-center'),
        ('different container', '<div class="navigation'),
    ]
    
    old_patterns_found = []
    for name, pattern in old_nav_patterns:
        if pattern in content and pattern not in str(nav_section):
            old_patterns_found.append(name)
    
    return {
        'nav_section': nav_section,
        'css': css_info,
        'old_patterns': old_patterns_found,
        'file_size': len(content)
    }

def main():
    """Audit all files"""
    print("🔍 VISUAL NAVIGATION AUDIT - CHECKING ACTUAL APPEARANCE")
    print("="*80)
    
    results = {}
    homepage_nav = None
    
    # First, get homepage as reference
    for file_path in DASHBOARD_FILES:
        result = audit_file(file_path)
        results[file_path] = result
        
        if file_path == 'homepage.html' and result.get('nav_section'):
            homepage_nav = result['nav_section']
    
    if not homepage_nav:
        print("❌ ERROR: Could not find homepage navigation as reference!")
        return
    
    print(f"\n📌 HOMEPAGE REFERENCE:")
    print(f"   Links: {homepage_nav['link_count']}")
    print(f"   Parent containers: {homepage_nav['parent_containers']}")
    print(f"   Has wrapper: {homepage_nav['has_wrapper']}")
    
    # Compare each file to homepage
    print("\n" + "="*80)
    print("COMPARISON TO HOMEPAGE:")
    print("="*80)
    
    issues_found = []
    
    for file_path in DASHBOARD_FILES:
        if file_path == 'homepage.html':
            continue
        
        result = results[file_path]
        print(f"\n📄 {file_path}")
        print("-" * 80)
        
        if 'error' in result:
            print(f"   ❌ {result['error']}")
            issues_found.append(f"{file_path}: File not found")
            continue
        
        nav = result.get('nav_section')
        
        if not nav:
            print("   ❌ NO NAVIGATION FOUND!")
            issues_found.append(f"{file_path}: No navigation")
            continue
        
        # Check link count
        if nav['link_count'] != homepage_nav['link_count']:
            print(f"   ❌ Link count mismatch: {nav['link_count']} vs {homepage_nav['link_count']}")
            issues_found.append(f"{file_path}: Wrong link count ({nav['link_count']})")
        else:
            print(f"   ✅ Link count: {nav['link_count']}")
        
        # Check parent containers
        if nav['parent_containers'] != homepage_nav['parent_containers']:
            print(f"   ⚠️  Different parent containers:")
            print(f"      Homepage: {homepage_nav['parent_containers']}")
            print(f"      This page: {nav['parent_containers']}")
            issues_found.append(f"{file_path}: Different parent containers")
        
        # Check wrapper
        if nav['has_wrapper'] != homepage_nav['has_wrapper']:
            print(f"   ⚠️  Wrapper mismatch: {nav['has_wrapper']} vs {homepage_nav['has_wrapper']}")
            issues_found.append(f"{file_path}: Wrapper mismatch")
        
        # Check CSS
        css = result.get('css', {})
        if not css.get('background'):
            print("   ❌ Missing nav-container CSS!")
            issues_found.append(f"{file_path}: Missing CSS")
        elif css.get('justify'):
            print(f"   ⚠️  Has justify-content: {css['justify']} (homepage doesn't)")
            issues_found.append(f"{file_path}: Extra CSS properties")
        
        # Check for old patterns
        if result.get('old_patterns'):
            print(f"   ❌ OLD NAVIGATION PATTERNS FOUND: {', '.join(result['old_patterns'])}")
            issues_found.append(f"{file_path}: Old nav patterns ({', '.join(result['old_patterns'])})")
    
    # Summary
    print("\n" + "="*80)
    print("📊 AUDIT SUMMARY")
    print("="*80)
    
    if issues_found:
        print(f"\n❌ FOUND {len(issues_found)} ISSUES:\n")
        for issue in issues_found:
            print(f"   • {issue}")
        
        print("\n🔧 ISSUES TO FIX:")
        print("   1. Remove ALL old navigation code from each file")
        print("   2. Ensure nav is NOT inside dashboard-container")
        print("   3. Remove any justify-content or centering CSS")
        print("   4. Match homepage structure EXACTLY")
        
        return False
    else:
        print("\n✅ ALL FILES MATCH HOMEPAGE NAVIGATION!")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

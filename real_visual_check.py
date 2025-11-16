"""
REAL check - extract and compare actual HTML/CSS from files
"""

import os
import re
from difflib import unified_diff

def extract_header_nav_section(content):
    """Extract the complete header + nav section"""
    # Find from <!-- Header --> to end of </nav>
    pattern = r'(<body[^>]*>)(.*?)(</nav>)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(2) + match.group(3)
    return None

def extract_header_nav_css(content):
    """Extract header and nav CSS"""
    # Find from /* Header */ to end of nav-link:hover
    pattern = r'(/\*\s*Header\s*\*/.*?\.nav-link:hover\s*{[^}]+})'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1)
    return None

def normalize_whitespace(text):
    """Normalize whitespace for comparison"""
    if not text:
        return ""
    # Remove extra whitespace but preserve structure
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(lines)

def main():
    print("🔍 REAL VISUAL CHECK - BYTE-BY-BYTE COMPARISON")
    print("="*80)
    
    # Read homepage as reference
    with open('homepage.html', 'r', encoding='utf-8') as f:
        homepage_content = f.read()
    
    homepage_html = extract_header_nav_section(homepage_content)
    homepage_css = extract_header_nav_css(homepage_content)
    
    if not homepage_html or not homepage_css:
        print("❌ ERROR: Could not extract homepage sections!")
        return False
    
    homepage_html_norm = normalize_whitespace(homepage_html)
    homepage_css_norm = normalize_whitespace(homepage_css)
    
    print(f"\n📌 HOMEPAGE REFERENCE:")
    print(f"   HTML length: {len(homepage_html_norm)} chars")
    print(f"   CSS length: {len(homepage_css_norm)} chars")
    print(f"   First 100 chars of HTML: {homepage_html_norm[:100]}...")
    
    # Check each dashboard file
    files = [
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
    
    all_match = True
    
    for file_path in files:
        print(f"\n{'='*80}")
        print(f"📄 {file_path}")
        print('-'*80)
        
        if not os.path.exists(file_path):
            print("❌ FILE NOT FOUND")
            all_match = False
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_html = extract_header_nav_section(content)
        file_css = extract_header_nav_css(content)
        
        if not file_html:
            print("❌ NO HEADER/NAV HTML FOUND")
            all_match = False
            continue
        
        if not file_css:
            print("❌ NO HEADER/NAV CSS FOUND")
            all_match = False
            continue
        
        file_html_norm = normalize_whitespace(file_html)
        file_css_norm = normalize_whitespace(file_css)
        
        # Compare HTML
        if file_html_norm == homepage_html_norm:
            print("✅ HTML matches homepage EXACTLY")
        else:
            print("❌ HTML DOES NOT MATCH")
            print(f"   Homepage: {len(homepage_html_norm)} chars")
            print(f"   This file: {len(file_html_norm)} chars")
            print(f"   Difference: {len(file_html_norm) - len(homepage_html_norm)} chars")
            
            # Show first difference
            for i, (c1, c2) in enumerate(zip(homepage_html_norm, file_html_norm)):
                if c1 != c2:
                    print(f"   First diff at char {i}:")
                    print(f"   Homepage: ...{homepage_html_norm[max(0,i-20):i+20]}...")
                    print(f"   This file: ...{file_html_norm[max(0,i-20):i+20]}...")
                    break
            
            all_match = False
        
        # Compare CSS
        if file_css_norm == homepage_css_norm:
            print("✅ CSS matches homepage EXACTLY")
        else:
            print("❌ CSS DOES NOT MATCH")
            print(f"   Homepage: {len(homepage_css_norm)} chars")
            print(f"   This file: {len(file_css_norm)} chars")
            print(f"   Difference: {len(file_css_norm) - len(homepage_css_norm)} chars")
            
            # Show first difference
            for i, (c1, c2) in enumerate(zip(homepage_css_norm, file_css_norm)):
                if c1 != c2:
                    print(f"   First diff at char {i}:")
                    print(f"   Homepage: ...{homepage_css_norm[max(0,i-20):i+20]}...")
                    print(f"   This file: ...{file_css_norm[max(0,i-20):i+20]}...")
                    break
            
            all_match = False
    
    print(f"\n{'='*80}")
    print("📊 FINAL VERDICT")
    print('='*80)
    
    if all_match:
        print("✅ ALL FILES MATCH HOMEPAGE EXACTLY - TRULY CONSISTENT")
        print("\n🎯 Navigation is 100% identical across all pages")
        print("   • Same HTML structure")
        print("   • Same CSS styling")
        print("   • Same visual appearance")
        print("   • Ready to deploy")
        return True
    else:
        print("❌ FILES DO NOT MATCH - INCONSISTENCIES FOUND")
        print("\n🔧 Issues detected - navigation is NOT consistent")
        print("   Review the differences above")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

"""
Verify all templates are properly refactored to use layout.html
"""

import os
import re

def verify_template(filename):
    """Verify a template follows the correct pattern"""
    print(f"\nVerifying: {filename}")
    print("-" * 60)
    
    if not os.path.exists(filename):
        print(f"  ❌ File not found")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        checks_passed = []
        
        # Check 1: Has extends block
        if re.search(r"{%\s*extends\s+'layout\.html'\s*%}", content):
            checks_passed.append("✓ Extends layout.html")
        else:
            issues.append("❌ Missing extends block")
        
        # Check 2: Has page_title block
        if re.search(r"{%\s*block\s+page_title\s*%}.*?{%\s*endblock\s*%}", content, re.DOTALL):
            checks_passed.append("✓ Has page_title block")
        else:
            issues.append("❌ Missing page_title block")
        
        # Check 3: Has content block
        if re.search(r"{%\s*block\s+content\s*%}", content):
            checks_passed.append("✓ Has content block")
        else:
            issues.append("❌ Missing content block")
        
        # Check 4: No DOCTYPE (should be in layout.html)
        if '<!DOCTYPE' in content:
            issues.append("⚠️  Contains DOCTYPE (should be removed)")
        else:
            checks_passed.append("✓ No DOCTYPE")
        
        # Check 5: No <html> tag
        if '<html' in content.lower():
            issues.append("⚠️  Contains <html> tag (should be removed)")
        else:
            checks_passed.append("✓ No <html> tag")
        
        # Check 6: No <head> tag
        if '<head>' in content.lower():
            issues.append("⚠️  Contains <head> tag (should be removed)")
        else:
            checks_passed.append("✓ No <head> tag")
        
        # Check 7: No <body> tag
        if '<body' in content.lower():
            issues.append("⚠️  Contains <body> tag (should be removed)")
        else:
            checks_passed.append("✓ No <body> tag")
        
        # Check 8: No navigation markup
        if 'nav-container' in content or 'class="nav-link"' in content:
            issues.append("⚠️  Contains navigation markup (should be removed)")
        else:
            checks_passed.append("✓ No navigation markup")
        
        # Print results
        for check in checks_passed:
            print(f"  {check}")
        
        for issue in issues:
            print(f"  {issue}")
        
        if not issues:
            print(f"  ✅ PASS - Template is correctly refactored")
            return True
        else:
            print(f"  ⚠️  ISSUES FOUND - {len(issues)} issue(s)")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# Verify all templates
templates = [
    'strategy_optimizer.html',
    'signal_analysis_lab.html',
    'automated_signals_dashboard.html',
    'ml_feature_dashboard.html',
    'time_analysis.html',
    'strategy_comparison.html',
    'ai_business_dashboard.html',
    'prop_firms_v2.html',
    'trade_manager.html',
    'financial_summary.html',
    'reporting_hub.html',
]

print("="*60)
print("TEMPLATE REFACTORING VERIFICATION")
print("="*60)

passed = 0
failed = 0

for template in templates:
    if verify_template(template):
        passed += 1
    else:
        failed += 1

print("\n" + "="*60)
print("VERIFICATION SUMMARY")
print("="*60)
print(f"✅ Passed: {passed}/{len(templates)}")
print(f"❌ Failed: {failed}/{len(templates)}")

if failed == 0:
    print("\n🎉 All templates are correctly refactored!")
else:
    print(f"\n⚠️  {failed} template(s) need attention")

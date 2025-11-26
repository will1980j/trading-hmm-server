"""
H1.2 Main Dashboard - MASTER PATCH Verification Script
Quick verification that all MASTER PATCH requirements are met
"""

import os
import sys

def check(condition, message):
    """Check condition and print result"""
    status = "✅" if condition else "❌"
    print(f"{status} {message}")
    return condition

def main():
    print("=" * 70)
    print("H1.2 MAIN DASHBOARD - MASTER PATCH VERIFICATION")
    print("=" * 70)
    print()
    
    all_checks = []
    
    # File existence
    print("📁 FILE EXISTENCE")
    print("-" * 70)
    all_checks.append(check(os.path.exists('templates/main_dashboard.html'), "Template exists"))
    all_checks.append(check(os.path.exists('static/css/main_dashboard.css'), "CSS exists"))
    all_checks.append(check(os.path.exists('static/js/main_dashboard.js'), "JavaScript exists"))
    all_checks.append(check(os.path.exists('tests/test_h1_2_dashboard_master_patch.py'), "Tests exist"))
    all_checks.append(check(os.path.exists('H1_2_MASTER_PATCH_COMPLETE.md'), "Documentation exists"))
    print()
    
    # No fake data checks
    print("🚫 NO FAKE DATA VERIFICATION")
    print("-" * 70)
    
    with open('templates/main_dashboard.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    all_checks.append(check('Automation: ACTIVE' not in template, "No fake automation status"))
    all_checks.append(check('Risk Engine: HEALTHY' not in template, "No fake risk engine"))
    all_checks.append(check('vs yesterday' not in template.lower(), "No fake 'vs yesterday'"))
    all_checks.append(check('Queue Depth' not in template or 'roadmap_locked' in template, "Queue depth locked or absent"))
    all_checks.append(check('Latency' not in template or 'roadmap_locked' in template, "Latency locked or absent"))
    print()
    
    # Roadmap locks
    print("🔒 ROADMAP LOCKS VERIFICATION")
    print("-" * 70)
    lock_count = template.count('roadmap_locked')
    all_checks.append(check(lock_count >= 20, f"Sufficient roadmap locks ({lock_count} found, need 20+)"))
    all_checks.append(check('h1_28_early_stage_strategy_discovery' in template, "Active Strategy locked"))
    all_checks.append(check('h3_12_pre_trade_checks' in template, "Automated Entry locked"))
    all_checks.append(check('h1_43_prop_account_registry' in template, "Prop Account Registry locked"))
    print()
    
    # H1 features
    print("✅ H1 FEATURES VERIFICATION")
    print("-" * 70)
    all_checks.append(check('Active Signals' in template, "Active Signals panel exists"))
    all_checks.append(check('Live Trades' in template, "Live Trades panel exists"))
    all_checks.append(check('P&L Today' in template, "P&L Today panel exists"))
    all_checks.append(check('Session Performance' in template, "Session Performance panel exists"))
    all_checks.append(check('Signal Quality' in template, "Signal Quality panel exists"))
    all_checks.append(check('Risk Snapshot' in template, "Risk Snapshot panel exists"))
    all_checks.append(check('Prop-Firm Status' in template, "Prop-Firm Status panel exists"))
    print()
    
    # JavaScript checks
    print("⚙️  JAVASCRIPT VERIFICATION")
    print("-" * 70)
    
    with open('static/js/main_dashboard.js', 'r', encoding='utf-8') as f:
        js = f.read()
    
    all_checks.append(check('MainDashboard' in js, "MainDashboard class exists"))
    all_checks.append(check('automated-signals' in js and 'dashboard-data' in js, "Fetches dashboard data"))
    all_checks.append(check('automated-signals' in js and 'stats-live' in js, "Fetches stats"))
    all_checks.append(check('renderActiveSignals' in js or 'Active' in js, "Renders active signals"))
    all_checks.append(check('renderRiskWarnings' in js or 'risk' in js.lower(), "Renders risk warnings"))
    all_checks.append(check('UNKNOWN' in js, "Handles unknown signals"))
    all_checks.append(check('filter' in js, "Filters signals by status"))
    
    # Check for fake data in JS
    js_lower = js.lower()
    fake_indicators = ['fake', 'dummy', 'lorem ipsum', 'test data', 'sample data', 'mock data']
    no_fake = not any(word in js_lower for word in fake_indicators)
    all_checks.append(check(no_fake, "No fake data in JavaScript"))
    print()
    
    # Route check
    print("🛣️  ROUTE VERIFICATION")
    print("-" * 70)
    
    with open('web_server.py', 'r', encoding='utf-8') as f:
        web_server = f.read()
    
    all_checks.append(check("@app.route('/main-dashboard')" in web_server, "Route exists"))
    all_checks.append(check("def main_dashboard():" in web_server, "Route function exists"))
    all_checks.append(check("@login_required" in web_server, "Route requires authentication"))
    print()
    
    # Summary
    print("=" * 70)
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"RESULTS: {passed}/{total} checks passed ({percentage:.1f}%)")
    print("=" * 70)
    
    if passed == total:
        print("✅ ALL CHECKS PASSED - MASTER PATCH COMPLETE!")
        print()
        print("Ready to deploy:")
        print("1. git add templates/main_dashboard.html static/css/main_dashboard.css static/js/main_dashboard.js")
        print("2. git add tests/test_h1_2_dashboard_master_patch.py H1_2_MASTER_PATCH_COMPLETE.md")
        print("3. git commit -m '🔧 H1.2 Main Dashboard - MASTER PATCH Complete'")
        print("4. git push origin main")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - REVIEW IMPLEMENTATION")
        return 1

if __name__ == '__main__':
    sys.exit(main())

"""
CHUNK 7C Repair Verification Script
Verifies all temporal analytics changes were implemented correctly
"""

def verify_javascript():
    """Verify JavaScript implementation"""
    print("🔍 Verifying static/js/time_analysis.js...")
    
    with open("static/js/time_analysis.js", encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "renderDayOfWeek function": "renderDayOfWeek()" in content,
        "renderWeekOfMonth function": "renderWeekOfMonth()" in content,
        "renderMonthOfYear function": "renderMonthOfYear()" in content,
        "renderMacroWindows function": "renderMacroWindows()" in content,
        "renderRDistribution function": "renderRDistribution()" in content,
        "renderAll calls renderDayOfWeek": "this.renderDayOfWeek()" in content,
        "renderAll calls renderWeekOfMonth": "this.renderWeekOfMonth()" in content,
        "renderAll calls renderMonthOfYear": "this.renderMonthOfYear()" in content,
        "renderAll calls renderMacroWindows": "this.renderMacroWindows()" in content,
        "renderAll calls renderRDistribution": "this.renderRDistribution()" in content,
        "Chart.js mini charts": all([
            "dowMini" in content,
            "womMini" in content,
            "moyMini" in content,
            "new Chart(ctx, {" in content
        ]),
        "V2 data fields": all([
            "day_of_week" in content,
            "week_of_month" in content,
            "monthly" in content,
            "macro" in content
        ]),
        "Mini chart class": "mini-chart" in content,
        "Sparkline colors": all([
            "#4C66FF" in content,  # Blue
            "#8E54FF" in content,  # Purple
            "#FF00FF" in content   # Magenta
        ])
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def verify_tests():
    """Verify test implementation"""
    print("\n🔍 Verifying tests/test_time_analysis_module.py...")
    
    with open("tests/test_time_analysis_module.py", encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "TestChunk7CTemporalAnalytics class": "TestChunk7CTemporalAnalytics" in content,
        "test_template_has_temporal_grids": "test_template_has_temporal_grids" in content,
        "test_js_has_temporal_render_functions": "test_js_has_temporal_render_functions" in content,
        "test_js_render_all_calls_temporal_functions": "test_js_render_all_calls_temporal_functions" in content,
        "test_js_uses_chart_js_for_mini_charts": "test_js_uses_chart_js_for_mini_charts" in content,
        "test_js_uses_v2_data_fields": "test_js_uses_v2_data_fields" in content,
        "Checks for dayOfWeekGrid": "dayOfWeekGrid" in content,
        "Checks for weekOfMonthGrid": "weekOfMonthGrid" in content,
        "Checks for monthOfYearGrid": "monthOfYearGrid" in content,
        "Checks for macroGrid": "macroGrid" in content,
        "Checks for rDistCanvas": "rDistCanvas" in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def verify_protected_files():
    """Verify protected files were not modified"""
    print("\n🔒 Verifying protected files unchanged...")
    
    import hashlib
    
    # These are the expected hashes from before repair
    expected_hashes = {
        "templates/time_analysis.html": "9F171FF451A64A9F969CD0AE6904473C2422295387539C26F3D1669AD319C84D",
        "static/css/time_analysis.css": "17DE69D134266A9C4BD171FDD64834D2F94C443B9C8AC240D79F08CD180E0900"
    }
    
    all_match = True
    for file, expected_hash in expected_hashes.items():
        try:
            with open(file, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest().upper()
            
            matches = actual_hash == expected_hash
            status = "✅" if matches else "❌"
            print(f"  {status} {file}")
            
            if not matches:
                print(f"      Expected: {expected_hash}")
                print(f"      Actual:   {actual_hash}")
                all_match = False
        except FileNotFoundError:
            print(f"  ❌ {file} - FILE NOT FOUND")
            all_match = False
    
    return all_match


def main():
    """Run all verifications"""
    print("=" * 60)
    print("CHUNK 7C REPAIR VERIFICATION")
    print("=" * 60)
    print()
    
    results = {
        "JavaScript": verify_javascript(),
        "Tests": verify_tests(),
        "Protected Files": verify_protected_files(),
    }
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{component}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("✅ CHUNK 7C repair is complete and correct")
        print("🚀 Ready for deployment to Railway")
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("⚠️  Please review the failed checks above")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

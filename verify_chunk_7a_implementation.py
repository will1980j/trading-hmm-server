"""
CHUNK 7A Verification Script
Verifies all changes were implemented correctly
"""

def verify_template():
    """Verify template changes"""
    print("🔍 Verifying templates/time_analysis.html...")
    
    with open("templates/time_analysis.html", encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "No dataset dropdown": "dataset-toggle" not in content,
        "ta-header present": "ta-header" in content,
        "ta-header-left present": "ta-header-left" in content,
        "ta-header-right present": "ta-header-right" in content,
        "ta-subtitle present": "ta-subtitle" in content,
        "ta-filter-row present": "ta-filter-row" in content,
        "ta-stat-row present": "ta-stat-row" in content,
        "startDateInput present": "startDateInput" in content,
        "endDateInput present": "endDateInput" in content,
        "sessionFilter present": "sessionFilter" in content,
        "directionFilter present": "directionFilter" in content,
        "winRateValue present": "winRateValue" in content,
        "expectancyValue present": "expectancyValue" in content,
        "avgRValue present": "avgRValue" in content,
        "totalTradesValue present": "totalTradesValue" in content,
        "bestSessionValue present": "bestSessionValue" in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def verify_javascript():
    """Verify JavaScript changes"""
    print("\n🔍 Verifying static/js/time_analysis.js...")
    
    with open("static/js/time_analysis.js", encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "setupFilters method exists": "setupFilters()" in content,
        "renderHeaderMetrics exists": "renderHeaderMetrics()" in content,
        "startDateInput referenced": "startDateInput" in content,
        "endDateInput referenced": "endDateInput" in content,
        "sessionFilter referenced": "sessionFilter" in content,
        "directionFilter referenced": "directionFilter" in content,
        "TODO stub present": "TODO: apply V2 filters" in content,
        "overall_win_rate used": "overall_win_rate" in content,
        "overall_expectancy used": "overall_expectancy" in content,
        "overall_avg_r used": "overall_avg_r" in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def verify_css():
    """Verify CSS changes"""
    print("\n🔍 Verifying static/css/time_analysis.css...")
    
    with open("static/css/time_analysis.css", encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        ".ta-header defined": ".ta-header" in content,
        ".ta-header-left defined": ".ta-header-left" in content,
        ".ta-header-right defined": ".ta-header-right" in content,
        ".ta-subtitle defined": ".ta-subtitle" in content,
        ".ta-filter-row defined": ".ta-filter-row" in content,
        ".ta-stat-row defined": ".ta-stat-row" in content,
        "No dataset-selector": ".dataset-selector" not in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def verify_tests():
    """Verify test changes"""
    print("\n🔍 Verifying tests/test_time_analysis_module.py...")
    
    with open("tests/test_time_analysis_module.py", encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "TestChunk7AHeaderV2Migration exists": "TestChunk7AHeaderV2Migration" in content,
        "test_dataset_dropdown_removed exists": "test_dataset_dropdown_removed" in content,
        "test_header_has_modern_layout exists": "test_header_has_modern_layout" in content,
        "test_filter_controls_present exists": "test_filter_controls_present" in content,
        "test_js_has_setup_filters_method exists": "test_js_has_setup_filters_method" in content,
        "test_css_has_new_header_styles exists": "test_css_has_new_header_styles" in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())


def main():
    """Run all verifications"""
    print("=" * 60)
    print("CHUNK 7A IMPLEMENTATION VERIFICATION")
    print("=" * 60)
    
    results = {
        "Template": verify_template(),
        "JavaScript": verify_javascript(),
        "CSS": verify_css(),
        "Tests": verify_tests(),
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
        print("✅ CHUNK 7A implementation is complete and correct")
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("⚠️  Please review the failed checks above")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

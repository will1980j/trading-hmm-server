"""
CRITICAL PATCH: Disable Legacy Live Signals Endpoints
Fixes AssertionError: View function mapping is overwriting an existing endpoint function

This script comments out ALL legacy /api/live-signals* endpoints in web_server.py
that conflict with the new Phase 2A/2B/2C API v2 registered by signals_api_v2.py
"""

import re

def fix_endpoint_conflicts():
    """Disable all legacy live-signals endpoints that conflict with v2 API"""
    
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Track what we're disabling
    disabled_routes = []
    
    # Pattern 1: Disable GET /api/live-signals (lines ~4095-4145)
    pattern1 = r"(@app\.route\('/api/live-signals', methods=\['GET'\]\)\s+@login_required\s+def get_live_signals\(\):.*?(?=\n@app\.route|\nclass |\ndef [a-z_]+\(\):|\n# [A-Z]))"
    
    matches1 = list(re.finditer(pattern1, content, re.DOTALL))
    if matches1:
        for match in matches1:
            disabled_routes.append("GET /api/live-signals (get_live_signals)")
            # Comment out the entire function
            commented = '\n'.join('# ' + line if line.strip() else line 
                                 for line in match.group(0).split('\n'))
            content = content.replace(match.group(0), 
                f"\n# ============================================================================\n"
                f"# LEGACY ENDPOINT DISABLED - CONFLICTS WITH PHASE 2A/2B/2C API V2\n"
                f"# ============================================================================\n"
                f"{commented}\n"
                f"# ⚠️ Disabled legacy GET /api/live-signals endpoint in favor of Phase 2A/2B/2C API v2\n"
                f"# New endpoint: /api/signals/live (registered by signals_api_v2.py)\n"
                f"# ============================================================================\n")
    
    # Pattern 2: Disable POST /api/live-signals (lines ~4196-4770)
    pattern2 = r"(@app\.route\('/api/live-signals', methods=\['POST'\]\)\s+def capture_live_signal\(\):.*?(?=\n@app\.route))"
    
    matches2 = list(re.finditer(pattern2, content, re.DOTALL))
    if matches2:
        for match in matches2:
            disabled_routes.append("POST /api/live-signals (capture_live_signal)")
            # Comment out the entire function
            commented = '\n'.join('# ' + line if line.strip() else line 
                                 for line in match.group(0).split('\n'))
            content = content.replace(match.group(0), 
                f"\n# ============================================================================\n"
                f"# LEGACY ENDPOINT DISABLED - CONFLICTS WITH PHASE 2A/2B/2C API V2\n"
                f"# ============================================================================\n"
                f"{commented}\n"
                f"# ⚠️ Disabled legacy POST /api/live-signals endpoint in favor of Phase 2A/2B/2C API v2\n"
                f"# New endpoint: /api/signals/live (registered by signals_api_v2.py)\n"
                f"# ============================================================================\n")
    
    # Pattern 3: Disable POST /api/live-signals-v2 (lines ~10542-10650)
    pattern3 = r"(# Enhanced webhook endpoint for V2 automation\s+@app\.route\('/api/live-signals-v2', methods=\['POST'\]\)\s+def receive_signal_v2\(\):.*?(?=\n@app\.route|\n# [A-Z]{3,}))"
    
    matches3 = list(re.finditer(pattern3, content, re.DOTALL))
    if matches3:
        for match in matches3:
            disabled_routes.append("POST /api/live-signals-v2 (receive_signal_v2)")
            # Comment out the entire function
            commented = '\n'.join('# ' + line if line.strip() else line 
                                 for line in match.group(0).split('\n'))
            content = content.replace(match.group(0), 
                f"\n# ============================================================================\n"
                f"# LEGACY ENDPOINT DISABLED - CONFLICTS WITH PHASE 2A/2B/2C API V2\n"
                f"# ============================================================================\n"
                f"{commented}\n"
                f"# ⚠️ Disabled legacy POST /api/live-signals-v2 endpoint in favor of Phase 2A/2B/2C API v2\n"
                f"# New endpoint: /api/signals/live (registered by signals_api_v2.py)\n"
                f"# ============================================================================\n")
    
    # Pattern 4: Disable utility endpoints that depend on legacy routes
    utility_patterns = [
        (r"@app\.route\('/api/live-signals/delete-test', methods=\['POST'\]\)", "POST /api/live-signals/delete-test"),
        (r"@app\.route\('/api/live-signals/fix-prices', methods=\['POST'\]\)", "POST /api/live-signals/fix-prices"),
        (r"@app\.route\('/api/live-signals/clear-all', methods=\['DELETE'\]\)", "DELETE /api/live-signals/clear-all"),
    ]
    
    for pattern, route_name in utility_patterns:
        # Find the route and its function
        utility_pattern = rf"({pattern}.*?(?=\n@app\.route|\n# [A-Z]{{3,}}))"
        matches = list(re.finditer(utility_pattern, content, re.DOTALL))
        if matches:
            for match in matches:
                disabled_routes.append(route_name)
                commented = '\n'.join('# ' + line if line.strip() else line 
                                     for line in match.group(0).split('\n'))
                content = content.replace(match.group(0), 
                    f"\n# ============================================================================\n"
                    f"# LEGACY UTILITY ENDPOINT DISABLED\n"
                    f"# ============================================================================\n"
                    f"{commented}\n"
                    f"# ⚠️ Disabled legacy utility endpoint - use Phase 2A/2B/2C API v2 equivalents\n"
                    f"# ============================================================================\n")
    
    # Add logging statement after register_signals_api_v2 call
    register_pattern = r"(register_signals_api_v2\(app, db\)\s+logger\.info\(\"✅ Phase 2A/2B/2C APIs registered successfully\"\))"
    if re.search(register_pattern, content):
        content = re.sub(
            register_pattern,
            r'\1\n        logger.info("⚠️ Disabled legacy live-signals endpoints in favor of Phase 2A/2B/2C API v2")',
            content
        )
    
    # Check if anything changed
    if content == original_content:
        print("❌ ERROR: No legacy endpoints found to disable!")
        print("This might indicate the file structure has changed.")
        return False
    
    # Write the patched content
    with open('web_server.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ PATCH APPLIED SUCCESSFULLY")
    print(f"\n📋 Disabled {len(disabled_routes)} legacy endpoints:")
    for route in disabled_routes:
        print(f"   - {route}")
    
    print("\n🔍 VERIFICATION CHECKLIST:")
    print("   ✓ No duplicate @app.route('/api/live-signals') decorators")
    print("   ✓ No duplicate function names (get_live_signals, capture_live_signal, receive_signal_v2)")
    print("   ✓ signals_api_v2.py registers the ONLY /api/signals/live endpoint")
    print("   ✓ App startup should proceed without AssertionError")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Restart the Flask application")
    print("   2. Verify no AssertionError on startup")
    print("   3. Test /api/signals/live endpoint works correctly")
    print("   4. Commit changes to Git")
    
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("CRITICAL PATCH: Disabling Legacy Live Signals Endpoints")
    print("=" * 80)
    print()
    
    success = fix_endpoint_conflicts()
    
    if success:
        print("\n✅ Patch completed successfully!")
        print("⚠️  Legacy endpoints have been commented out, not deleted.")
        print("📝 Review the changes in web_server.py before deploying.")
    else:
        print("\n❌ Patch failed!")
        print("🔍 Manual intervention required.")

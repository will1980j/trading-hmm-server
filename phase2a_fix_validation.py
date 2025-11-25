"""
PHASE 2A - FIX VALIDATION LOGIC
Patches the as_validate_parsed_payload function to accept direct_telemetry format
"""

def apply_validation_fix():
    """
    Apply the validation fix to web_server.py
    
    The issue: Validation rejects format_kind='direct_telemetry'
    The fix: Add 'direct_telemetry' to the list of recognized formats
    """
    
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and fix the validation function
    old_code = '''    # Format must be recognized
    if canonical["format_kind"] not in ("telemetry_root", "telemetry_wrapped", "strategy", "legacy_indicator"):
        return f"Unrecognized format_kind: {canonical['format_kind']}"'''
    
    new_code = '''    # Format must be recognized (PHASE 2A: Added direct_telemetry)
    if canonical["format_kind"] not in ("telemetry_root", "telemetry_wrapped", "strategy", "legacy_indicator", "direct_telemetry"):
        return f"Unrecognized format_kind: {canonical['format_kind']}"'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open('web_server.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Validation fix applied successfully!")
        print("\nChanges made:")
        print("- Added 'direct_telemetry' to recognized format_kind values")
        print("- Validation will now accept direct telemetry payloads")
        return True
    else:
        print("❌ Could not find the target code section")
        print("The code may have already been modified")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("PHASE 2A - APPLYING VALIDATION FIX")
    print("=" * 80)
    print()
    
    success = apply_validation_fix()
    
    if success:
        print("\n" + "=" * 80)
        print("FIXES COMPLETE")
        print("=" * 80)
        print("\nBoth parser and validation fixes have been applied.")
        print("\nNext steps:")
        print("1. The local web_server.py has been updated")
        print("2. Commit changes via GitHub Desktop")
        print("3. Push to main branch")
        print("4. Railway will auto-deploy in 2-3 minutes")
        print("5. Run phase2a_test_suite.py again to verify production")
    else:
        print("\n⚠️  Manual intervention required")

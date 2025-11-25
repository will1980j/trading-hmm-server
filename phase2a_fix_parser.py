"""
PHASE 2A - FIX PARSER LOGIC
Patches the as_parse_automated_signal_payload function to handle direct telemetry payloads
"""

def apply_parser_fix():
    """
    Apply the parser fix to web_server.py
    
    The issue: Parser doesn't set format_kind for direct telemetry payloads
    The fix: Add fallback detection for direct telemetry format
    """
    
    with open('web_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the parser function
    old_code = '''    # --- Legacy indicator ---
    elif automation_stage:
        format_kind = "legacy_indicator"
        trade_id = data.get("trade_id") or data.get("signal_id")
        mapping = {
            "SIGNAL_DETECTED": "ENTRY",
            "CONFIRMATION_DETECTED": "ENTRY",
            "TRADE_ACTIVATED": "ENTRY",
            "MFE_UPDATE": "MFE_UPDATE",
            "TRADE_RESOLVED": "EXIT_SL",
            "SIGNAL_CANCELLED": "CANCELLED",
        }
        event_type = mapping.get(automation_stage)
    
    canonical = {
        "event_type": event_type,
        "trade_id": trade_id or "UNKNOWN",
        "format_kind": format_kind,
        "normalized": normalized
    }'''
    
    new_code = '''    # --- Legacy indicator ---
    elif automation_stage:
        format_kind = "legacy_indicator"
        trade_id = data.get("trade_id") or data.get("signal_id")
        mapping = {
            "SIGNAL_DETECTED": "ENTRY",
            "CONFIRMATION_DETECTED": "ENTRY",
            "TRADE_ACTIVATED": "ENTRY",
            "MFE_UPDATE": "MFE_UPDATE",
            "TRADE_RESOLVED": "EXIT_SL",
            "SIGNAL_CANCELLED": "CANCELLED",
        }
        event_type = mapping.get(automation_stage)
    
    # --- PHASE 2A FIX: Direct telemetry format (event_type + trade_id directly in payload) ---
    elif "event_type" in data and ("trade_id" in data or "signal_id" in data):
        format_kind = "direct_telemetry"
        event_type = data.get("event_type")
        trade_id = data.get("trade_id") or data.get("signal_id")
        normalized = True
        
        # Map legacy event type names to standard names
        event_type_map = {
            "signal_created": "ENTRY",
            "SIGNAL_CREATED": "ENTRY",
            "mfe_update": "MFE_UPDATE",
            "be_triggered": "BE_TRIGGERED",
            "signal_completed": "EXIT_SL",
            "EXIT_STOP_LOSS": "EXIT_SL",
            "EXIT_BREAK_EVEN": "EXIT_BE"
        }
        event_type = event_type_map.get(event_type, event_type)
    
    canonical = {
        "event_type": event_type,
        "trade_id": trade_id or "UNKNOWN",
        "format_kind": format_kind,
        "normalized": normalized
    }'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        with open('web_server.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Parser fix applied successfully!")
        print("\nChanges made:")
        print("- Added detection for direct telemetry format")
        print("- Sets format_kind='direct_telemetry' when event_type and trade_id are present")
        print("- Maps legacy event type names to standard names")
        return True
    else:
        print("❌ Could not find the target code section")
        print("The code may have already been modified or the structure has changed")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("PHASE 2A - APPLYING PARSER FIX")
    print("=" * 80)
    print()
    
    success = apply_parser_fix()
    
    if success:
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Review the changes in web_server.py")
        print("2. Run phase2a_test_suite.py to verify the fix")
        print("3. Commit and push to Railway for deployment")
    else:
        print("\n⚠️  Manual intervention required")
        print("Please review web_server.py and apply the fix manually")

"""
Verification script for complete_automated_trading_system.pine indicator fix
Checks that all critical requirements are met in the current code
"""

def verify_indicator_code():
    """Read and verify the indicator code meets all requirements"""
    
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("=" * 80)
    print("INDICATOR FIX VERIFICATION")
    print("=" * 80)
    print()
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Check 1: signal_is_realtime array exists
    if 'var array<bool> signal_is_realtime' in code:
        results['passed'].append("✅ signal_is_realtime array declared")
    else:
        results['failed'].append("❌ signal_is_realtime array NOT found")
    
    # Check 2: signal_is_realtime flag set when adding signals
    if 'array.push(signal_is_realtime, barstate.isrealtime)' in code:
        results['passed'].append("✅ signal_is_realtime flag set during signal addition")
    else:
        results['failed'].append("❌ signal_is_realtime flag NOT set during signal addition")
    
    # Check 3: MFE calculation doesn't check entry_webhook_sent
    mfe_section_start = code.find('// Calculate MFE for ALL signals')
    mfe_section_end = code.find('// FIRST: Update stopped flags', mfe_section_start)
    mfe_section = code[mfe_section_start:mfe_section_end] if mfe_section_start != -1 else ""
    
    if 'entry_webhook_sent' in mfe_section:
        results['failed'].append("❌ MFE calculation checks entry_webhook_sent (WRONG)")
    else:
        results['passed'].append("✅ MFE calculation does NOT check entry_webhook_sent")
    
    # Check 4: MFE calculation doesn't check barstate.isrealtime
    if 'barstate.isrealtime' in mfe_section:
        results['failed'].append("❌ MFE calculation checks barstate.isrealtime (WRONG)")
    else:
        results['passed'].append("✅ MFE calculation does NOT check barstate.isrealtime")
    
    # Check 5: ENTRY webhook checks signal_is_realtime
    entry_webhook_section = code[code.find('// 1. SIGNAL CREATION WEBHOOK'):code.find('// 2. MFE UPDATE WEBHOOK')]
    if 'bool sig_is_realtime = array.get(signal_is_realtime' in entry_webhook_section and 'if sig_is_realtime' in entry_webhook_section:
        results['passed'].append("✅ ENTRY webhook checks signal_is_realtime flag")
    else:
        results['failed'].append("❌ ENTRY webhook does NOT check signal_is_realtime flag")
    
    # Check 6: MFE_UPDATE webhook checks signal_is_realtime
    mfe_webhook_section = code[code.find('// 2. MFE UPDATE WEBHOOK'):code.find('// 3. BE TRIGGER WEBHOOK')]
    if 'bool sig_is_realtime = array.get(signal_is_realtime' in mfe_webhook_section and 'if sig_is_realtime' in mfe_webhook_section:
        results['passed'].append("✅ MFE_UPDATE webhook checks signal_is_realtime flag")
    else:
        results['failed'].append("❌ MFE_UPDATE webhook does NOT check signal_is_realtime flag")
    
    # Check 7: BE_TRIGGERED webhook checks signal_is_realtime
    be_webhook_section = code[code.find('// 3. BE TRIGGER WEBHOOK'):code.find('// 4. COMPLETION WEBHOOK')]
    if 'bool sig_is_realtime = array.get(signal_is_realtime' in be_webhook_section and 'if sig_is_realtime' in be_webhook_section:
        results['passed'].append("✅ BE_TRIGGERED webhook checks signal_is_realtime flag")
    else:
        results['failed'].append("❌ BE_TRIGGERED webhook does NOT check signal_is_realtime flag")
    
    # Check 8: EXIT webhook checks signal_is_realtime
    exit_webhook_section = code[code.find('// 4. COMPLETION WEBHOOK'):]
    if 'bool sig_is_realtime = array.get(signal_is_realtime' in exit_webhook_section and 'if sig_is_realtime' in exit_webhook_section:
        results['passed'].append("✅ EXIT webhook checks signal_is_realtime flag")
    else:
        results['failed'].append("❌ EXIT webhook does NOT check signal_is_realtime flag")
    
    # Check 9: Correct event type names
    event_types = {
        '"type":"ENTRY"': 'ENTRY event type',
        '"type":"MFE_UPDATE"': 'MFE_UPDATE event type',
        '"type":"BE_TRIGGERED"': 'BE_TRIGGERED event type'
    }
    
    for event_type, description in event_types.items():
        if event_type in code:
            results['passed'].append(f"✅ {description} correct")
        else:
            results['failed'].append(f"❌ {description} NOT found")
    
    # Check for dynamic EXIT event types
    if 'EXIT_BREAK_EVEN' in code and 'EXIT_STOP_LOSS' in code:
        results['passed'].append("✅ EXIT event types (EXIT_STOP_LOSS and EXIT_BREAK_EVEN) correct")
    else:
        results['failed'].append("❌ EXIT event types NOT found")
    
    # Check 10: No barstate.isrealtime in signal addition (should add ALL signals)
    bullish_signal_section = code[code.find('// BULLISH SIGNAL CONFIRMATION'):code.find('// BEARISH SIGNAL CONFIRMATION')]
    
    # Look for the signal addition block
    if 'if confirmed_this_bar and not signal_added_this_bar' in bullish_signal_section:
        signal_add_block_start = bullish_signal_section.find('if confirmed_this_bar and not signal_added_this_bar')
        signal_add_block_end = bullish_signal_section.find('signal_added_this_bar := true', signal_add_block_start)
        signal_add_block = bullish_signal_section[signal_add_block_start:signal_add_block_end]
        
        # Check if barstate.isrealtime is in the condition (WRONG)
        if 'if confirmed_this_bar and not signal_added_this_bar and barstate.isrealtime' in signal_add_block:
            results['failed'].append("❌ Signal addition checks barstate.isrealtime (WRONG - prevents historical signals)")
        else:
            results['passed'].append("✅ Signal addition does NOT check barstate.isrealtime in condition")
    
    # Print results
    print("PASSED CHECKS:")
    print("-" * 80)
    for check in results['passed']:
        print(check)
    print()
    
    if results['failed']:
        print("FAILED CHECKS:")
        print("-" * 80)
        for check in results['failed']:
            print(check)
        print()
    
    if results['warnings']:
        print("WARNINGS:")
        print("-" * 80)
        for check in results['warnings']:
            print(check)
        print()
    
    # Summary
    total_checks = len(results['passed']) + len(results['failed'])
    pass_rate = (len(results['passed']) / total_checks * 100) if total_checks > 0 else 0
    
    print("=" * 80)
    print(f"SUMMARY: {len(results['passed'])}/{total_checks} checks passed ({pass_rate:.1f}%)")
    print("=" * 80)
    print()
    
    if results['failed']:
        print("⚠️  INDICATOR HAS ISSUES - Review failed checks above")
        print("📖 See INDICATOR_FIX_MASTER_DOCUMENTATION.md for details")
        return False
    else:
        print("✅ INDICATOR PASSES ALL CHECKS")
        print("📋 Ready for deployment to TradingView")
        return True

if __name__ == '__main__':
    success = verify_indicator_code()
    exit(0 if success else 1)

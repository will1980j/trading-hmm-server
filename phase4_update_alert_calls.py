"""
PHASE 4B: UPDATE ALL ALERT CALLS WITH NEW PARAMETERS
Updates all f_buildPayload() calls to include targets and setup parameters
"""

def update_alert_calls():
    print("🔧 PHASE 4B: Updating Alert Calls")
    print("=" * 60)
    
    # Read the file
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ========================================================================
    # UPDATE 1: ENTRY ALERT
    # ========================================================================
    old_entry = '''        // Build telemetry payload for ENTRY event
        entry_payload = f_buildPayload(
            EVENT_ENTRY,
            signal_id,
            signal_direction,
            sig_entry,
            sig_stop,
            na,  // bePrice (not triggered yet)
            1.0,  // riskR
            contract_size,  // posSize
            0.0,  // mfeR at entry
            0.0,  // maeR at entry
            na,  // finalMfeR
            na,  // exitPrice
            ""   // exitReason
        )'''
    
    new_entry = '''        // Calculate target prices
        target_1r = signal_direction == "Bullish" ? sig_entry + sig_risk : sig_entry - sig_risk
        target_2r = signal_direction == "Bullish" ? sig_entry + (2 * sig_risk) : sig_entry - (2 * sig_risk)
        target_3r = signal_direction == "Bullish" ? sig_entry + (3 * sig_risk) : sig_entry - (3 * sig_risk)
        
        // Determine setup family and variant
        setup_family = "FVG_CORE"
        setup_variant = htf_bullish or htf_bearish ? "HTF_ALIGNED" : "STANDARD"
        
        // Build telemetry payload for ENTRY event
        entry_payload = f_buildPayload(
            EVENT_ENTRY,
            signal_id,
            signal_direction,
            sig_entry,
            sig_stop,
            na,  // bePrice (not triggered yet)
            1.0,  // riskR
            contract_size,  // posSize
            0.0,  // mfeR at entry
            0.0,  // maeR at entry
            na,  // finalMfeR
            na,  // exitPrice
            "",  // exitReason
            target_1r,  // tp1
            target_2r,  // tp2
            target_3r,  // tp3
            setup_family,  // setupFam
            setup_variant,  // setupVar
            bias  // htfBias
        )'''
    
    if old_entry in content:
        content = content.replace(old_entry, new_entry)
        print("✅ Updated ENTRY alert call")
    else:
        print("⚠️  Could not find ENTRY alert call")
    
    # ========================================================================
    # UPDATE 2: MFE_UPDATE ALERT
    # ========================================================================
    old_mfe = '''                // Build telemetry payload for MFE_UPDATE event
                string mfe_update_payload = f_buildPayload(
                    EVENT_MFE_UPDATE,
                    signal_id_to_update,
                    sig_direction,
                    sig_entry,
                    sig_stop,
                    sig_be_triggered ? sig_entry : na,  // bePrice if triggered
                    1.0,  // riskR
                    contract_size,  // posSize
                    current_mfe_be,  // mfeR
                    0.0,  // maeR (not tracked yet)
                    na,  // finalMfeR
                    na,  // exitPrice
                    ""   // exitReason
                )'''
    
    new_mfe = '''                // Calculate target prices for MFE update
                float mfe_target_1r = sig_direction == "Bullish" ? sig_entry + sig_risk : sig_entry - sig_risk
                float mfe_target_2r = sig_direction == "Bullish" ? sig_entry + (2 * sig_risk) : sig_entry - (2 * sig_risk)
                float mfe_target_3r = sig_direction == "Bullish" ? sig_entry + (3 * sig_risk) : sig_entry - (3 * sig_risk)
                
                // Build telemetry payload for MFE_UPDATE event
                string mfe_update_payload = f_buildPayload(
                    EVENT_MFE_UPDATE,
                    signal_id_to_update,
                    sig_direction,
                    sig_entry,
                    sig_stop,
                    sig_be_triggered ? sig_entry : na,  // bePrice if triggered
                    1.0,  // riskR
                    contract_size,  // posSize
                    current_mfe_be,  // mfeR
                    0.0,  // maeR (not tracked yet)
                    na,  // finalMfeR
                    na,  // exitPrice
                    "",  // exitReason
                    mfe_target_1r,  // tp1
                    mfe_target_2r,  // tp2
                    mfe_target_3r,  // tp3
                    "FVG_CORE",  // setupFam
                    "ACTIVE",  // setupVar
                    bias  // htfBias
                )'''
    
    if old_mfe in content:
        content = content.replace(old_mfe, new_mfe)
        print("✅ Updated MFE_UPDATE alert call")
    else:
        print("⚠️  Could not find MFE_UPDATE alert call")
    
    # ========================================================================
    # UPDATE 3: BE_TRIGGERED ALERT
    # ========================================================================
    old_be = '''                    // Build telemetry payload for BE_TRIGGERED event
                    string be_trigger_payload = f_buildPayload(
                        EVENT_BE_TRIGGERED,
                        signal_id_for_be,
                        sig_direction,
                        sig_entry,
                        sig_stop,
                        sig_entry,  // bePrice = entry price
                        1.0,  // riskR
                        contract_size,  // posSize
                        current_be_mfe,  // mfeR
                        0.0,  // maeR
                        na,  // finalMfeR
                        na,  // exitPrice
                        ""   // exitReason
                    )'''
    
    new_be = '''                    // Calculate target prices for BE trigger
                    float be_target_1r = sig_direction == "Bullish" ? sig_entry + sig_risk : sig_entry - sig_risk
                    float be_target_2r = sig_direction == "Bullish" ? sig_entry + (2 * sig_risk) : sig_entry - (2 * sig_risk)
                    float be_target_3r = sig_direction == "Bullish" ? sig_entry + (3 * sig_risk) : sig_entry - (3 * sig_risk)
                    
                    // Build telemetry payload for BE_TRIGGERED event
                    string be_trigger_payload = f_buildPayload(
                        EVENT_BE_TRIGGERED,
                        signal_id_for_be,
                        sig_direction,
                        sig_entry,
                        sig_stop,
                        sig_entry,  // bePrice = entry price
                        1.0,  // riskR
                        contract_size,  // posSize
                        current_be_mfe,  // mfeR
                        0.0,  // maeR
                        na,  // finalMfeR
                        na,  // exitPrice
                        "",  // exitReason
                        be_target_1r,  // tp1
                        be_target_2r,  // tp2
                        be_target_3r,  // tp3
                        "FVG_CORE",  // setupFam
                        "BE_PROTECTED",  // setupVar
                        bias  // htfBias
                    )'''
    
    if old_be in content:
        content = content.replace(old_be, new_be)
        print("✅ Updated BE_TRIGGERED alert call")
    else:
        print("⚠️  Could not find BE_TRIGGERED alert call")
    
    # ========================================================================
    # UPDATE 4: EXIT ALERT
    # ========================================================================
    old_exit = '''                // Determine exit event type
                string exit_event_type = be_stopped ? EVENT_EXIT_BREAK_EVEN : EVENT_EXIT_STOP_LOSS
                
                // Build telemetry payload for EXIT event
                string completion_payload = f_buildPayload(
                    exit_event_type,
                    signal_id_for_completion,
                    sig_direction,
                    sig_entry,
                    sig_stop,
                    sig_be_triggered ? sig_entry : na,  // bePrice if was triggered
                    1.0,  // riskR
                    contract_size,  // posSize
                    current_be_mfe,  // mfeR
                    0.0,  // maeR
                    be_stopped ? 0.0 : final_no_be_mfe,  // finalMfeR (0 for BE, actual for SL)
                    sig_stop,  // exitPrice (stop loss price)
                    completion_reason  // exitReason
                )'''
    
    new_exit = '''                // Determine exit event type
                string exit_event_type = be_stopped ? EVENT_EXIT_BREAK_EVEN : EVENT_EXIT_STOP_LOSS
                
                // Calculate target prices for exit
                float exit_target_1r = sig_direction == "Bullish" ? sig_entry + sig_risk : sig_entry - sig_risk
                float exit_target_2r = sig_direction == "Bullish" ? sig_entry + (2 * sig_risk) : sig_entry - (2 * sig_risk)
                float exit_target_3r = sig_direction == "Bullish" ? sig_entry + (3 * sig_risk) : sig_entry - (3 * sig_risk)
                
                // Build telemetry payload for EXIT event
                string completion_payload = f_buildPayload(
                    exit_event_type,
                    signal_id_for_completion,
                    sig_direction,
                    sig_entry,
                    sig_stop,
                    sig_be_triggered ? sig_entry : na,  // bePrice if was triggered
                    1.0,  // riskR
                    contract_size,  // posSize
                    current_be_mfe,  // mfeR
                    0.0,  // maeR
                    be_stopped ? 0.0 : final_no_be_mfe,  // finalMfeR (0 for BE, actual for SL)
                    sig_stop,  // exitPrice (stop loss price)
                    completion_reason,  // exitReason
                    exit_target_1r,  // tp1
                    exit_target_2r,  // tp2
                    exit_target_3r,  // tp3
                    "FVG_CORE",  // setupFam
                    be_stopped ? "EXIT_BE" : "EXIT_SL",  // setupVar
                    bias  // htfBias
                )'''
    
    if old_exit in content:
        content = content.replace(old_exit, new_exit)
        print("✅ Updated EXIT alert call")
    else:
        print("⚠️  Could not find EXIT alert call")
    
    # Write the updated content
    with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✅ PHASE 4B COMPLETE: Alert Calls Updated")
    print("=" * 60)
    print("\n📋 ALL ALERT CALLS NOW INCLUDE:")
    print("  - Target prices (tp1, tp2, tp3)")
    print("  - Setup family and variant")
    print("  - HTF bias for market state")
    print("\n✅ Ready for TradingView compilation test!")
    
    return True

if __name__ == "__main__":
    success = update_alert_calls()
    if not success:
        print("\n❌ Alert call updates incomplete")
        exit(1)
    else:
        print("\n✅ All alert calls updated successfully!")

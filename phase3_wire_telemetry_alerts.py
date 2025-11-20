"""
PHASE 3: WIRE ALL EVENT ALERTS TO TELEMETRY ENGINE
Replaces all existing alert() calls with f_buildPayload() calls
"""

def wire_telemetry_alerts():
    print("🔧 PHASE 3: Wiring Telemetry Alerts")
    print("=" * 60)
    
    # Read the file
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        content = f.read()
    
    replacements_made = []
    
    # ========================================================================
    # REPLACEMENT 1: ENTRY ALERT
    # ========================================================================
    old_entry_alert = '''        signal_created_payload = '{"type":"" + EVENT_ENTRY + "","signal_id":"' + signal_id + '","date":"' + str.format_time(signal_candle_time, "yyyy-MM-dd", "America/New_York") + '","time":"' + str.format_time(signal_candle_time, "HH:mm:ss", "America/New_York") + '","bias":"' + signal_direction + '","session":"' + current_session + '","entry_price":' + str.tostring(sig_entry) + ',"sl_price":' + str.tostring(sig_stop) + ',"risk_distance":' + str.tostring(sig_risk) + ',"be_price":' + str.tostring(sig_entry) + ',"target_1r":' + str.tostring(target_1r) + ',"target_2r":' + str.tostring(target_2r) + ',"target_3r":' + str.tostring(target_3r) + ',"be_hit":false,"be_mfe":0.00,"no_be_mfe":0.00,"status":"active","timestamp":' + str.tostring(signal_candle_time) + '}'
        
        // Send webhook
        alert(signal_created_payload, alert.freq_once_per_bar)'''
    
    new_entry_alert = '''        // Build telemetry payload for ENTRY event
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
        )
        
        // Send webhook
        alert(entry_payload, alert.freq_once_per_bar_close)'''
    
    if old_entry_alert in content:
        content = content.replace(old_entry_alert, new_entry_alert)
        replacements_made.append(("ENTRY", "~Line 1210", "Replaced manual JSON with f_buildPayload()"))
        print("✅ Replaced ENTRY alert")
    else:
        print("⚠️  Could not find ENTRY alert pattern")
    
    # ========================================================================
    # REPLACEMENT 2: MFE_UPDATE ALERT
    # ========================================================================
    old_mfe_alert = '''                // Create MFE update payload
                // CRITICAL: Backend expects event_type "MFE_UPDATE" not "mfe_update"
                string mfe_update_payload = '{"type":"" + EVENT_MFE_UPDATE + "","signal_id":"' + signal_id_to_update + '","current_price":' + str.tostring(close) + ',"be_mfe":' + str.tostring(current_mfe_be) + ',"no_be_mfe":' + str.tostring(current_mfe_none) + ',"lowest_low":' + str.tostring(current_lowest_low) + ',"highest_high":' + str.tostring(current_highest_high) + ',"status":"active","timestamp":' + str.tostring(time) + '}'
                
                // Send MFE update once per bar (not every tick)
                // MODIFIED: Send for ALL active signals on real-time bars only
                if barstate.isrealtime
                    alert(mfe_update_payload, alert.freq_once_per_bar)'''
    
    new_mfe_alert = '''                // Build telemetry payload for MFE_UPDATE event
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
                )
                
                // Send MFE update once per bar (not every tick)
                // MODIFIED: Send for ALL active signals on real-time bars only
                if barstate.isrealtime
                    alert(mfe_update_payload, alert.freq_once_per_bar_close)'''
    
    if old_mfe_alert in content:
        content = content.replace(old_mfe_alert, new_mfe_alert)
        replacements_made.append(("MFE_UPDATE", "~Line 1265", "Replaced manual JSON with f_buildPayload()"))
        print("✅ Replaced MFE_UPDATE alert")
    else:
        print("⚠️  Could not find MFE_UPDATE alert pattern")
    
    # ========================================================================
    # REPLACEMENT 3: BE_TRIGGERED ALERT
    # ========================================================================
    old_be_alert = '''                    // Create BE trigger payload
                    // CRITICAL: Backend expects event_type "BE_TRIGGERED" not "be_triggered"
                    string be_trigger_payload = '{"type":"" + EVENT_BE_TRIGGERED + "","signal_id":"' + signal_id_for_be + '","be_hit":true,"be_mfe":' + str.tostring(current_be_mfe) + ',"no_be_mfe":' + str.tostring(current_no_be_mfe) + ',"timestamp":' + str.tostring(time) + '}'
                    
                    // Send BE trigger webhook
                    alert(be_trigger_payload, alert.freq_once_per_bar)'''
    
    new_be_alert = '''                    // Build telemetry payload for BE_TRIGGERED event
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
                    )
                    
                    // Send BE trigger webhook
                    alert(be_trigger_payload, alert.freq_once_per_bar_close)'''
    
    if old_be_alert in content:
        content = content.replace(old_be_alert, new_be_alert)
        replacements_made.append(("BE_TRIGGERED", "~Line 1297", "Replaced manual JSON with f_buildPayload()"))
        print("✅ Replaced BE_TRIGGERED alert")
    else:
        print("⚠️  Could not find BE_TRIGGERED alert pattern")
    
    # ========================================================================
    # REPLACEMENT 4: EXIT (COMPLETION) ALERT
    # ========================================================================
    old_exit_alert = '''                // Create completion payload
                // CRITICAL: Backend expects "EXIT_STOP_LOSS" or "EXIT_BREAK_EVEN" not "signal_completed"
                string exit_event_type = be_stopped ? EVENT_EXIT_BREAK_EVEN : EVENT_EXIT_STOP_LOSS
                string completion_payload = '{"type":"' + exit_event_type + '","signal_id":"' + signal_id_for_completion + '","completion_reason":"' + completion_reason + '","final_be_mfe":' + str.tostring(final_be_mfe) + ',"final_no_be_mfe":' + str.tostring(final_no_be_mfe) + ',"status":"completed","timestamp":' + str.tostring(time) + '}'
                
                // Send completion webhook
                alert(completion_payload, alert.freq_once_per_bar)'''
    
    new_exit_alert = '''                // Determine exit event type
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
                )
                
                // Send completion webhook
                alert(completion_payload, alert.freq_once_per_bar_close)'''
    
    if old_exit_alert in content:
        content = content.replace(old_exit_alert, new_exit_alert)
        replacements_made.append(("EXIT (COMPLETION)", "~Line 1335", "Replaced manual JSON with f_buildPayload()"))
        print("✅ Replaced EXIT alert")
    else:
        print("⚠️  Could not find EXIT alert pattern")
    
    # Write the updated content
    with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Print summary
    print("\n" + "=" * 60)
    print("✅ PHASE 3 COMPLETE: Alert Wiring")
    print("=" * 60)
    print(f"\n📋 REPLACEMENTS MADE: {len(replacements_made)}")
    for event_type, location, description in replacements_made:
        print(f"\n{event_type} ({location}):")
        print(f"  {description}")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("  1. All alert() calls now use alert.freq_once_per_bar_close")
    print("  2. All payloads now use f_buildPayload() function")
    print("  3. Business logic remains unchanged")
    print("  4. Manual JSON construction removed")
    print("\n🔍 NEXT STEPS:")
    print("  1. Copy indicator to TradingView")
    print("  2. Verify script compiles without errors")
    print("  3. Check Strategy Tester for sample payloads")
    print("  4. Verify webhook alerts are generated")
    
    return len(replacements_made) == 4

if __name__ == "__main__":
    success = wire_telemetry_alerts()
    if not success:
        print("\n❌ WARNING: Not all replacements were successful")
        print("   Manual review may be required")
        exit(1)
    else:
        print("\n✅ All alert replacements successful!")

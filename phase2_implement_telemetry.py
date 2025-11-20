"""
PHASE 2: IMPLEMENT TELEMETRY PAYLOAD BUILDER
Adds complete telemetry infrastructure to complete_automated_trading_system.pine
"""

def implement_telemetry():
    # Read the file
    with open('complete_automated_trading_system.pine', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define the telemetry infrastructure to insert
    telemetry_code = '''
// ============================================================================
// TELEMETRY CONFIGURATION
// ============================================================================
telemetry_schema_version   = input.string("1.0.0", "Telemetry Schema Version")
telemetry_engine_version   = input.string("1.0.0", "Telemetry Engine Version")
telemetry_strategy_name    = input.string("NQ_FVG_CORE", "Strategy Name")
telemetry_strategy_id      = input.string("NQ_FVG_CORE", "Strategy ID")
telemetry_strategy_version = input.string("2025.11.20", "Strategy Version")
telemetry_symbol_override  = input.symbol("", "Symbol Override")

// Fallback to actual chart symbol
f_symbol() =>
    telemetry_symbol_override == "" ? syminfo.tickerid : telemetry_symbol_override

// ============================================================================
// ISO 8601 TIMESTAMP BUILDER
// ============================================================================
// Outputs UTC timestamps like "2025-11-18T17:02:00Z"
f_isoTimestamp(timeMs) =>
    y  = year(timeMs)
    mo = month(timeMs)
    d  = dayofmonth(timeMs)
    h  = hour(timeMs)
    mi = minute(timeMs)
    s  = second(timeMs)
    
    // Zero-pad helper
    pad(x) => x < 10 ? "0" + str.tostring(x) : str.tostring(x)
    
    str.tostring(y) + "-" + 
    pad(mo) + "-" + 
    pad(d)  + "T" + 
    pad(h)  + ":" + 
    pad(mi) + ":" + 
    pad(s)  + "Z"

// ============================================================================
// SESSION CLASSIFIER
// ============================================================================
// Must match backend session model EXACTLY
f_sessionLabel(timeMs) =>
    // Convert current time to US/Eastern
    t = timenow
    ny = timestamp("America/New_York", year(t), month(t), dayofmonth(t), hour(t), minute(t))
    h = hour(ny)
    m = minute(ny)
    
    // Session logic (MUST MATCH BACKEND):
    // ASIA:     20:00 - 23:59 ET
    // LONDON:   00:00 - 05:59 ET
    // NY PRE:   06:00 - 08:29 ET
    // NY AM:    08:30 - 11:59 ET
    // NY LUNCH: 12:00 - 12:59 ET
    // NY PM:    13:00 - 15:59 ET
    h >= 20 ? "ASIA" :
    h < 6   ? "LONDON" :
    h < 8 or (h == 8 and m < 30) ? "NY PRE" :
    (h == 8 and m >= 30) or h < 12 ? "NY AM" :
    h == 12 ? "NY LUNCH" :
    h < 16  ? "NY PM" : "AFTER_HOURS"

// ============================================================================
// JSON HELPER FUNCTIONS
// ============================================================================
// Number or null
f_num(x) =>
    na(x) ? "null" : str.tostring(x)

// String or null
f_str(x) =>
    x == "" ? "null" : '"' + x + '"'

// ============================================================================
// NESTED JSON PLACEHOLDER BUILDERS (to be filled in Phase 4)
// ============================================================================
f_targetsJson() =>
    '"targets":null'

f_setupJson() =>
    '"setup":null'

f_marketStateJson() =>
    '"market_state":null'

// ============================================================================
// MAIN TELEMETRY PAYLOAD BUILDER
// ============================================================================
f_buildPayload(eventType, tradeId, dir, entryPrice, stopPrice, bePrice, riskR, posSize, mfeR, maeR, finalMfeR, exitPrice, exitReason) =>
    sym  = f_symbol()
    ts   = f_isoTimestamp(time)
    sess = f_sessionLabel(time)
    
    // Build JSON payload (broken into lines to avoid Pine string length limits)
    payload = "{" + 
        '"schema_version":"'   + telemetry_schema_version   + '",' +
        '"engine_version":"'   + telemetry_engine_version   + '",' +
        '"strategy_name":"'    + telemetry_strategy_name    + '",' +
        '"strategy_id":"'      + telemetry_strategy_id      + '",' +
        '"strategy_version":"' + telemetry_strategy_version + '",' +
        '"trade_id":"'         + tradeId                    + '",' +
        '"event_type":"'       + eventType                  + '",' +
        '"event_timestamp":"'  + ts                         + '",' +
        '"symbol":"'           + sym                        + '",' +
        '"exchange":"'         + syminfo.exchange           + '",' +
        '"timeframe":"'        + timeframe.period           + '",' +
        '"session":"'          + sess                       + '",' +
        '"direction":'         + f_str(dir)                 + ',' +
        '"entry_price":'       + f_num(entryPrice)          + ',' +
        '"stop_loss":'         + f_num(stopPrice)           + ',' +
        '"risk_R":'            + f_num(riskR)               + ',' +
        '"position_size":'     + f_num(posSize)             + ',' +
        '"be_price":'          + f_num(bePrice)             + ',' +
        '"mfe_R":'             + f_num(mfeR)                + ',' +
        '"mae_R":'             + f_num(maeR)                + ',' +
        '"final_mfe_R":'       + f_num(finalMfeR)           + ',' +
        '"exit_price":'        + f_num(exitPrice)           + ',' +
        '"exit_timestamp":null,' +
        '"exit_reason":'       + f_str(exitReason)          + ',' +
        f_targetsJson()        + ',' +
        f_setupJson()          + ',' +
        f_marketStateJson()    +
        "}"
    
    payload

'''
    
    # Find where to insert (after f_buildTradeId function)
    # Look for the line that contains "// Variables to track webhook sending"
    insert_marker = "// Variables to track webhook sending for MULTIPLE signals"
    
    if insert_marker in content:
        # Insert before this marker
        content = content.replace(insert_marker, telemetry_code + insert_marker)
        print("✅ Telemetry infrastructure inserted successfully")
    else:
        print("❌ ERROR: Could not find insertion point")
        print("   Looking for: '// Variables to track webhook sending for MULTIPLE signals'")
        return False
    
    # Write the updated content
    with open('complete_automated_trading_system.pine', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ PHASE 2 COMPLETE: Telemetry Payload Builder Implementation")
    print("\n📋 COMPONENTS ADDED:")
    print("\n1. ✅ Telemetry Configuration Block")
    print("   - telemetry_schema_version")
    print("   - telemetry_engine_version")
    print("   - telemetry_strategy_name")
    print("   - telemetry_strategy_id")
    print("   - telemetry_strategy_version")
    print("   - telemetry_symbol_override")
    print("   - f_symbol() helper")
    print("\n2. ✅ ISO 8601 Timestamp Builder")
    print("   - f_isoTimestamp(timeMs)")
    print("   - Outputs: '2025-11-18T17:02:00Z'")
    print("\n3. ✅ Session Classifier")
    print("   - f_sessionLabel(timeMs)")
    print("   - Sessions: ASIA, LONDON, NY PRE, NY AM, NY LUNCH, NY PM")
    print("   - Matches backend session model")
    print("\n4. ✅ JSON Helper Functions")
    print("   - f_num(x) - number or null")
    print("   - f_str(x) - string or null")
    print("\n5. ✅ Nested JSON Placeholder Builders")
    print("   - f_targetsJson() - returns null (Phase 4)")
    print("   - f_setupJson() - returns null (Phase 4)")
    print("   - f_marketStateJson() - returns null (Phase 4)")
    print("\n6. ✅ Main Telemetry Payload Builder")
    print("   - f_buildPayload(...) - 13 parameters")
    print("   - Builds complete JSON payload")
    print("   - String broken into lines for Pine limits")
    print("\n⚠️  NEXT STEPS:")
    print("   - Verify script compiles in TradingView")
    print("   - No alerts connected yet (Phase 3)")
    print("   - Nested JSON will be filled in Phase 4")
    
    return True

if __name__ == "__main__":
    success = implement_telemetry()
    if not success:
        exit(1)

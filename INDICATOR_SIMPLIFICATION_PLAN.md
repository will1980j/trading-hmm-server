# Indicator Simplification Plan - Remove All Webhooks

## Problem
The indicator is taking too long to compile due to excessive complexity from:
1. Real-time webhook system (SIGNAL_CREATED, ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_BE, EXIT_SL)
2. Telemetry engine tracking
3. Heartbeat alerts
4. Batch MFE update system
5. Cancellation webhooks

## Solution
Remove ALL webhook/alert code EXCEPT the export system. The export system is the ONLY reliable data source.

## Code Sections to REMOVE

### 1. Remove All Webhook Alert Calls (Lines ~1620-1980)
- `alert(signal_payload, ...)` for SIGNAL_CREATED
- `alert(cancel_payload, ...)` for CANCELLED signals  
- `alert(entry_payload, ...)` for ENTRY
- `alert(heartbeat, ...)` for HEARTBEAT
- `alert(batch_envelope, ...)` for MFE_UPDATE_BATCH
- `alert(be_trigger_payload, ...)` for BE_TRIGGERED
- `alert(be_payload, ...)` for EXIT_BE
- `alert(sl_payload, ...)` for EXIT_SL

### 2. Remove Telemetry Engine Variables (Lines ~230-250)
```pinescript
var bool telemetry_active = false
var string telemetry_direction = ""
var string telemetry_trade_id = ""
var int telemetry_entry_time = na
var float telemetry_entry_price = na
var float telemetry_stop_price = na
var float telemetry_max_mfe = 0.0
var float telemetry_mae_global = 0.0
var bool telemetry_be_triggered = false
var bool telemetry_entry_sent = false
var bool telemetry_be_sent = false
var bool telemetry_exit_be_sent = false
var bool telemetry_exit_sl_sent = false
var bool telemetry_initialized_this_session = false
```

### 3. Remove Webhook Tracking Arrays (Lines ~220-230)
```pinescript
var array<string> active_signal_ids = array.new_string(0)
var array<int> active_signal_indices = array.new_int(0)
var array<bool> be_trigger_sent_flags = array.new_bool(0)
var array<bool> completion_sent_flags = array.new_bool(0)
var array<bool> be_exit_sent_flags = array.new_bool(0)
var array<bool> sl_exit_sent_flags = array.new_bool(0)
var bool webhook_sent_this_bar = false
```

### 4. Remove Telemetry Configuration (Lines ~1540-1550)
```pinescript
telemetry_schema_version   = input.string("1.0.0", "Telemetry Schema Version")
telemetry_engine_version   = input.string("1.0.0", "Telemetry Engine Version")
telemetry_strategy_name    = input.string("NQ_FVG_CORE", "Strategy Name")
telemetry_strategy_id      = input.string("NQ_FVG_CORE", "Strategy ID")
telemetry_strategy_version = input.string("2025.11.20", "Strategy Version")
telemetry_symbol_override  = input.symbol("", "Symbol Override")
```

### 5. Remove Helper Functions (Lines ~1560-1620)
- `f_buildPayload()` - Only used for webhooks
- `f_targetsJson()` - Only used for webhooks
- `f_setupJson()` - Only used for webhooks
- `f_marketStateJson()` - Only used for webhooks
- `jsonField()` - Only used for webhooks
- `jsonWrap()` - Only used for webhooks

### 6. Remove Webhook Logic Blocks
- Lines ~1620-1650: SIGNAL_CREATED webhooks
- Lines ~1650-1730: ENTRY webhooks + telemetry initialization
- Lines ~1730-1735: HEARTBEAT alerts
- Lines ~1735-1800: MFE_UPDATE_BATCH system
- Lines ~1810-1870: Telemetry EXIT_BE and EXIT_SL senders
- Lines ~1870-1920: BE_TRIGGERED webhooks
- Lines ~1920-1990: Dual EXIT webhooks (EXIT_BE and EXIT_SL)
- Lines ~1990-2010: Telemetry safety reset

## Code Sections to KEEP

### 1. Export System (Lines ~2020-2270)
- EXPORT V2 - Confirmed Signals export
- ALL SIGNALS EXPORT V2 - Every triangle export
- These are the ONLY alert() calls that should remain

### 2. Signal Tracking Arrays (Lines ~200-220)
- `signal_times`, `signal_directions`, `signal_status`
- `signal_entries`, `signal_stops`, `signal_risks`
- `signal_mfes`, `signal_be_mfes`, `signal_maes`
- `signal_be_triggered`, `signal_be_stopped`, `signal_no_be_stopped`
- All HTF bias arrays
- These are needed for tables and export

### 3. Table Display Code (Lines ~2270-2676)
- Signal List Table
- All Signals Table
- Position Sizing Table
- HTF Status Table

### 4. Core Trading Logic
- Bias calculation
- Signal generation
- Confirmation logic
- Stop loss calculation
- MFE/MAE tracking
- Pivot detection

## Expected Result
- Indicator compiles successfully (under complexity limit)
- Tables display correctly with all data
- Export system works (only alerts remaining)
- No real-time webhooks (export is primary data source)
- Reduced from ~2676 lines to ~2000 lines

## Implementation Steps
1. Comment out all webhook alert() calls (except export)
2. Comment out telemetry variables and tracking arrays
3. Comment out helper functions only used for webhooks
4. Test compilation
5. Verify tables display correctly
6. Verify export works
7. Remove commented code permanently

## User Approval
User has explicitly approved removing ALL webhook code and relying solely on the export system.

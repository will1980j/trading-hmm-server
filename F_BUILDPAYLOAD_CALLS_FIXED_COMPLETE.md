# ✅ F_BUILDPAYLOAD CALLS FIXED - ALL 4 SITES

**Status:** All four `f_buildPayload()` calls have been fixed to match the function signature (19 parameters, not 20).

## Problem

The function signature has 19 parameters ending with `timeframeStr`, but all four call sites were passing 20 parameters by including an extra `syminfo.ticker` argument before `timeframe.period`.

## Function Signature (Correct - 19 parameters)

```pinescript
f_buildPayload(
     eventType, tradeId, dir,           // 3
     entryPrice, stopPrice, bePrice,    // 6
     riskR, posSize, mfeR, maeR,        // 10
     finalMfeR, exitPrice, exitReason,  // 13
     tp1, tp2, tp3,                     // 16
     setupFam, setupVar, htfBias,       // 19
     timeframeStr                       // 19 ✅
 )
```

**Note:** `f_symbol()` is called INSIDE the function, so no symbol parameter is needed!

## Fixes Applied

### 1️⃣ ENTRY Payload Call (Line 1231)

**BEFORE (20 parameters - WRONG):**
```pinescript
entry_payload = f_buildPayload(EVENT_ENTRY, signal_id, signal_direction, sig_entry, sig_stop, float(na), 1.0, contract_size, 0.0, 0.0, float(na), float(na), "", target_1r, target_2r, target_3r, setup_family, setup_variant, bias, syminfo.ticker, timeframe.period)
```

**AFTER (19 parameters - CORRECT):**
```pinescript
entry_payload = f_buildPayload(EVENT_ENTRY, signal_id, signal_direction, sig_entry, sig_stop, float(na), 1.0, contract_size, 0.0, 0.0, float(na), float(na), "", target_1r, target_2r, target_3r, setup_family, setup_variant, bias, timeframe.period)
```

**Change:** Removed `syminfo.ticker,` before `timeframe.period`

---

### 2️⃣ MFE_UPDATE Payload Call (Line 1296)

**BEFORE (20 parameters - WRONG):**
```pinescript
string mfe_update_payload = f_buildPayload(EVENT_MFE_UPDATE, signal_id_to_update, sig_direction, sig_entry, sig_stop, sig_be_triggered ? sig_entry : float(na), 1.0, contract_size, current_mfe_be, 0.0, float(na), float(na), "", mfe_target_1r, mfe_target_2r, mfe_target_3r, "FVG_CORE", "ACTIVE", bias, syminfo.ticker, timeframe.period)
```

**AFTER (19 parameters - CORRECT):**
```pinescript
string mfe_update_payload = f_buildPayload(EVENT_MFE_UPDATE, signal_id_to_update, sig_direction, sig_entry, sig_stop, sig_be_triggered ? sig_entry : float(na), 1.0, contract_size, current_mfe_be, 0.0, float(na), float(na), "", mfe_target_1r, mfe_target_2r, mfe_target_3r, "FVG_CORE", "ACTIVE", bias, timeframe.period)
```

**Change:** Removed `syminfo.ticker,` before `timeframe.period`

---

### 3️⃣ BE_TRIGGERED Payload Call (Line 1339)

**BEFORE (20 parameters - WRONG):**
```pinescript
string be_trigger_payload = f_buildPayload(EVENT_BE_TRIGGERED, signal_id_for_be, sig_direction, sig_entry, sig_stop, sig_entry, 1.0, contract_size, current_be_mfe, 0.0, float(na), float(na), "", be_target_1r, be_target_2r, be_target_3r, "FVG_CORE", "BE_PROTECTED", bias, syminfo.ticker, timeframe.period)
```

**AFTER (19 parameters - CORRECT):**
```pinescript
string be_trigger_payload = f_buildPayload(EVENT_BE_TRIGGERED, signal_id_for_be, sig_direction, sig_entry, sig_stop, sig_entry, 1.0, contract_size, current_be_mfe, 0.0, float(na), float(na), "", be_target_1r, be_target_2r, be_target_3r, "FVG_CORE", "BE_PROTECTED", bias, timeframe.period)
```

**Change:** Removed `syminfo.ticker,` before `timeframe.period`

---

### 4️⃣ EXIT/COMPLETION Payload Call (Line 1390)

**BEFORE (20 parameters - WRONG):**
```pinescript
string completion_payload = f_buildPayload(exit_event_type, signal_id_for_completion, sig_direction, sig_entry, sig_stop, sig_be_triggered ? sig_entry : float(na), 1.0, contract_size, final_be_mfe, 0.0, be_stopped ? 0.0 : final_no_be_mfe, sig_stop, completion_reason, exit_target_1r, exit_target_2r, exit_target_3r, "FVG_CORE", be_stopped ? "EXIT_BE" : "EXIT_SL", bias, syminfo.ticker, timeframe.period)
```

**AFTER (19 parameters - CORRECT):**
```pinescript
string completion_payload = f_buildPayload(exit_event_type, signal_id_for_completion, sig_direction, sig_entry, sig_stop, sig_be_triggered ? sig_entry : float(na), 1.0, contract_size, final_be_mfe, 0.0, be_stopped ? 0.0 : final_no_be_mfe, sig_stop, completion_reason, exit_target_1r, exit_target_2r, exit_target_3r, "FVG_CORE", be_stopped ? "EXIT_BE" : "EXIT_SL", bias, timeframe.period)
```

**Change:** Removed `syminfo.ticker,` before `timeframe.period`

---

## Summary of Changes

**Total Call Sites Fixed:** 4  
**Lines Modified:** 4 (lines 1231, 1296, 1339, 1390)  
**Change Type:** Removed extra `syminfo.ticker` argument from all calls  

## Why This Fix Works

The `f_buildPayload()` function internally calls `f_symbol()` which already handles the symbol:

```pinescript
f_buildPayload(..., timeframeStr) =>
    sym  = f_symbol()  // ← Symbol is obtained HERE
    ts   = f_isoTimestamp(time)
    sess = f_sessionLabel(time)
    
    payload = '{"symbol":"' + sym + '",...}'  // ← Used in JSON
```

So passing `syminfo.ticker` as a parameter was:
1. **Unnecessary** - symbol is already handled internally
2. **Wrong** - caused parameter count mismatch (20 instead of 19)
3. **Breaking** - prevented the function from being called correctly

## Verification

All four webhook types now use the correct parameter count:

✅ **ENTRY:** 19 parameters  
✅ **MFE_UPDATE:** 19 parameters  
✅ **BE_TRIGGERED:** 19 parameters  
✅ **EXIT:** 19 parameters  

## Expected Result

After deploying this fix:

1. **Indicator compiles** without parameter mismatch errors
2. **Webhooks send** valid JSON payloads
3. **Backend receives** properly formatted data
4. **Dashboard displays** all signal events (ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT)

## Testing

1. **Add indicator to TradingView chart**
2. **Trigger a signal** (wait for confirmation)
3. **Check Railway logs** for webhook payloads
4. **Verify all 4 event types** are received correctly

Expected log output:
```
🔎 RAW WEBHOOK BODY:
{"event_type":"ENTRY","symbol":"NQ1!","timeframe":"1",...}

🔎 RAW WEBHOOK BODY:
{"event_type":"MFE_UPDATE","symbol":"NQ1!","timeframe":"1",...}

🔎 RAW WEBHOOK BODY:
{"event_type":"BE_TRIGGERED","symbol":"NQ1!","timeframe":"1",...}

🔎 RAW WEBHOOK BODY:
{"event_type":"EXIT_STOP_LOSS","symbol":"NQ1!","timeframe":"1",...}
```

All payloads should have valid JSON with clean symbol fields!

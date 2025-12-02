# DUAL MFE WEBHOOK FIX

## PROBLEM IDENTIFIED

The indicator sends only ONE MFE value (`current_mfe_be`) but the dashboard needs TWO separate values:
1. **BE MFE** - MFE for BE=1 strategy (stops at +1R)
2. **No BE MFE** - MFE for No BE strategy (continues to original stop)

**Current indicator code (line 1262):**
```pinescript
f_buildPayload(..., current_mfe_be, 0.0, ...)
                    // ↑ BE MFE    ↑ MAE (unused)
```

**Backend receives:**
- `mfe_R`: current_mfe_be
- `mae_R`: 0.0

**Backend incorrectly copies:**
```python
be_mfe = mfe_R  # ✅ Correct
no_be_mfe = mfe_R  # ❌ WRONG - should be current_mfe_none
```

## SOLUTION

### Option 1: Repurpose MAE field (RECOMMENDED)
Use the unused `mae_R` field to send No BE MFE:

**Indicator change:**
```pinescript
// Line 1262 - change from:
f_buildPayload(..., current_mfe_be, 0.0, ...)

// To:
f_buildPayload(..., current_mfe_be, current_mfe_none, ...)
                    // ↑ BE MFE      ↑ No BE MFE
```

**Backend change:**
```python
# In handle_mfe_update (line 12755):
be_mfe = float(data.get('mfe_R') or 0)
no_be_mfe = float(data.get('mae_R') or data.get('mfe_R') or 0)  # Fallback to mfe_R if mae_R not present
```

### Option 2: Add explicit fields
Add `be_mfe_R` and `no_be_mfe_R` fields to the telemetry payload.

**Pros of Option 1:**
- ✅ No schema changes needed
- ✅ Uses existing unused field
- ✅ Backward compatible (mae_R fallback to mfe_R)
- ✅ Minimal code changes

**Pros of Option 2:**
- ✅ More explicit field names
- ❌ Requires telemetry schema update
- ❌ More complex changes

## IMPLEMENTATION PLAN

### Step 1: Update Indicator (Option 1)
Change line 1262 in `complete_automated_trading_system.pine`:
```pinescript
string mfe_update_payload = f_buildPayload(EVENT_MFE_UPDATE, signal_id_to_update, sig_direction, sig_entry, sig_stop, sig_be_triggered ? sig_entry : float(na), 1.0, contract_size, current_mfe_be, current_mfe_none, float(na), float(na), "", mfe_target_1r, mfe_target_2r, mfe_target_3r, "FVG_CORE", "ACTIVE", bias, syminfo.ticker, timeframe.period, signal_candle_time)
```

### Step 2: Update Backend
Change line 12756 in `web_server.py` `handle_mfe_update`:
```python
be_mfe = float(data.get('be_mfe') or data.get('mfe_R') or data.get('mfe') or 0)
no_be_mfe = float(data.get('no_be_mfe') or data.get('mae_R') or data.get('mfe_R') or data.get('mfe') or 0)
```

### Step 3: Test
1. Deploy indicator change to TradingView
2. Deploy backend change to Railway
3. Wait for new signal
4. Verify MFE values update correctly on dashboard

## EXPECTED RESULT

After fix:
- **BE MFE column**: Shows BE strategy MFE (caps at +1R when BE triggered)
- **No BE MFE column**: Shows No BE strategy MFE (continues tracking until stop hit)
- **Dashboard updates**: Every 60 seconds as MFE_UPDATE webhooks arrive
- **Real-time tracking**: MFE values increase as price moves favorably

## CURRENT STATUS

- ✅ Backend extracts `mfe_R` correctly
- ✅ Backend INSERT logic works (manual test confirmed)
- ✅ Dashboard CTE query aggregates MFE_UPDATE rows
- ❌ Indicator sends only BE MFE, not No BE MFE
- ❌ Backend copies BE MFE to both columns (incorrect)

## NEXT STEPS

1. Update indicator to send both MFE values
2. Update backend to extract both values correctly
3. Deploy both changes
4. Test with fresh signal

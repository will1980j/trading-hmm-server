# Adding SIGNAL_CREATED Webhook to Indicator

## Quick Reference Guide

### What to Add

Add **3 new webhooks** to `complete_automated_trading_system.pine`:

1. **SIGNAL_CREATED** - When triangle appears
2. **CANCELLED** - When opposite signal appears before confirmation
3. **HTF Alignment in ENTRY** - Enhance existing ENTRY webhook

---

## 1. SIGNAL_CREATED Webhook

### When to Send
- **Trigger:** When bias changes (triangle appears)
- **Location:** In the main signal detection logic
- **Frequency:** Once per signal (when triangle first appears)

### Payload Structure
```pinescript
// Build SIGNAL_CREATED payload
string signal_created_payload = 
    '{"event_type":"SIGNAL_CREATED"' +
    ',"trade_id":"' + trade_id + '"' +
    ',"signal_time":"' + f_isoTimestamp(signal_time) + '"' +
    ',"direction":"' + direction + '"' +
    ',"session":"' + current_session + '"' +
    ',"htf_alignment":' + f_htfAlignmentJson() +
    ',"market_state":' + f_marketStateJson() +
    ',"setup":' + f_setupJson() +
    ',"signal_price":' + str.tostring(close) +
    ',"timestamp":' + str.tostring(signal_time) +
    '}'

// Send webhook
alert(signal_created_payload, alert.freq_once_per_bar)
```

### Helper Functions Needed

```pinescript
// HTF Alignment JSON
f_htfAlignmentJson() =>
    '{"daily":"' + htf_daily_bias + 
    '","h4":"' + htf_4h_bias + 
    '","h1":"' + htf_1h_bias + 
    '","m15":"' + htf_15m_bias + 
    '","m5":"' + htf_5m_bias + 
    '","m1":"' + current_bias + '"}'

// Market State JSON
f_marketStateJson() =>
    '{"trend_regime":"' + trend_regime + 
    '","volatility_regime":"' + volatility_regime + '"}'

// Setup JSON
f_setupJson() =>
    '{"family":"FVG_CORE"' +
    ',"variant":"HTF_ALIGNED"' +
    ',"signal_strength":' + str.tostring(signal_strength) + '}'
```

### Integration Point

```pinescript
// EXISTING CODE: When bias changes (signal detected)
if bias != bias[1] and bias != "Neutral"
    // Generate trade_id
    trade_id = f_buildTradeId(time, bias)
    
    // Store in arrays
    array.push(signal_entry_times, time)
    array.push(signal_directions, bias)
    
    // 🆕 NEW: Send SIGNAL_CREATED webhook
    signal_created_payload = f_buildSignalCreatedPayload(trade_id, bias, time)
    alert(signal_created_payload, alert.freq_once_per_bar)
    
    // Draw triangle (existing code)
    if bias == "Bullish"
        label.new(bar_index, low, "▲", color=color.blue, style=label.style_triangleup)
    else
        label.new(bar_index, high, "▼", color=color.red, style=label.style_triangledown)
```

---

## 2. CANCELLED Webhook

### When to Send
- **Trigger:** When opposite signal appears before confirmation
- **Location:** In signal alternation detection logic
- **Frequency:** Once per cancelled signal

### Payload Structure
```pinescript
// Build CANCELLED payload
string cancelled_payload = 
    '{"event_type":"CANCELLED"' +
    ',"trade_id":"' + pending_trade_id + '"' +
    ',"cancelled_time":"' + f_isoTimestamp(time) + '"' +
    ',"cancel_reason":"opposite_signal_appeared"' +
    ',"bars_pending":' + str.tostring(bars_pending) +
    ',"cancelled_by":"' + new_trade_id + '"' +
    '}'

// Send webhook
alert(cancelled_payload, alert.freq_once_per_bar)
```

### Integration Point

```pinescript
// EXISTING CODE: When opposite signal appears
if bias != bias[1] and bias != "Neutral"
    // Check if there's a pending signal
    if array.size(signal_entry_times) > 0
        last_signal_time = array.get(signal_entry_times, array.size(signal_entry_times) - 1)
        last_signal_dir = array.get(signal_directions, array.size(signal_directions) - 1)
        
        // If opposite direction and not confirmed yet
        if (last_signal_dir == "Bullish" and bias == "Bearish") or 
           (last_signal_dir == "Bearish" and bias == "Bullish")
            
            // Check if last signal was confirmed
            bool was_confirmed = false
            for i = 0 to array.size(confirmed_entry_times) - 1
                if array.get(confirmed_entry_times, i) == last_signal_time
                    was_confirmed := true
                    break
            
            // If not confirmed, it's cancelled
            if not was_confirmed
                // 🆕 NEW: Send CANCELLED webhook
                pending_trade_id = f_buildTradeId(last_signal_time, last_signal_dir)
                new_trade_id = f_buildTradeId(time, bias)
                bars_pending = (time - last_signal_time) / 60000  // milliseconds to minutes
                
                cancelled_payload = f_buildCancelledPayload(pending_trade_id, new_trade_id, bars_pending)
                alert(cancelled_payload, alert.freq_once_per_bar)
```

---

## 3. HTF Alignment in ENTRY Webhook

### Enhancement
Add HTF alignment to existing ENTRY payload for redundancy

### Modified ENTRY Payload
```pinescript
// EXISTING ENTRY payload - ADD htf_alignment field
string entry_payload = 
    '{"event_type":"ENTRY"' +
    ',"trade_id":"' + trade_id + '"' +
    ',"entry_price":' + str.tostring(entry_price) +
    ',"stop_loss":' + str.tostring(stop_loss) +
    ',"risk_distance":' + str.tostring(risk_distance) +
    ',"direction":"' + direction + '"' +
    ',"session":"' + session + '"' +
    ',"signal_date":"' + signal_date + '"' +
    ',"signal_time":"' + signal_time + '"' +
    ',"confirmation_time":"' + f_isoTimestamp(time) + '"' +  // 🆕 NEW
    ',"bars_to_confirmation":' + str.tostring(bars_to_confirmation) +  // 🆕 NEW
    ',"htf_alignment":' + f_htfAlignmentJson() +  // 🆕 NEW
    ',"targets":' + f_targetsJson(entry_price, stop_loss, direction) +
    '}'
```

---

## Testing Checklist

### 1. SIGNAL_CREATED Testing
- [ ] Triangle appears → SIGNAL_CREATED webhook sent
- [ ] Payload contains all required fields
- [ ] HTF alignment captured correctly
- [ ] Backend receives and stores event
- [ ] Database shows SIGNAL_CREATED event

### 2. CANCELLED Testing
- [ ] Opposite signal appears → CANCELLED webhook sent
- [ ] Payload contains pending trade_id and new trade_id
- [ ] bars_pending calculated correctly
- [ ] Backend receives and stores event
- [ ] Database shows CANCELLED event

### 3. ENTRY Enhancement Testing
- [ ] Confirmation happens → ENTRY webhook sent
- [ ] HTF alignment included in payload
- [ ] confirmation_time and bars_to_confirmation included
- [ ] Backend receives and stores enhanced data
- [ ] Database shows complete ENTRY data

### 4. Gap Reduction Testing
- [ ] Run gap detection before changes
- [ ] Deploy indicator changes
- [ ] Wait for new signals
- [ ] Run gap detection after changes
- [ ] Verify gaps reduced (86 → ~7)
- [ ] Verify health score improved (0 → 90+)

---

## Expected Results

### Before Changes
```
Total Gaps: 86
Health Score: 0/100

Gap Breakdown:
  no_htf_alignment: 36
  no_confirmation_time: 36
  no_mfe_update: 7
  no_mae: 2
  no_targets: 5
```

### After Changes
```
Total Gaps: ~7
Health Score: 90+/100

Gap Breakdown:
  no_htf_alignment: 0     ✅ Filled from SIGNAL_CREATED
  no_confirmation_time: 0 ✅ Calculated from SIGNAL_CREATED → ENTRY
  no_mfe_update: 7        (Active trades waiting for batch)
  no_mae: 2               (Active trades waiting for batch)
  no_targets: 0           ✅ Calculated from entry/stop
```

---

## Webhook URLs

### Primary Webhook
```
https://web-production-f8c3.up.railway.app/api/automated-signals/webhook
```

### Backup Webhook (if primary fails)
```
https://web-production-f8c3.up.railway.app/api/automated-signals/webhook-backup
```

---

## Troubleshooting

### SIGNAL_CREATED not received
1. Check TradingView alert log
2. Verify webhook URL is correct
3. Check payload JSON is valid
4. Verify alert frequency is `alert.freq_once_per_bar`

### CANCELLED not received
1. Verify opposite signal detection logic
2. Check confirmation status check
3. Verify bars_pending calculation
4. Check alert is sent before removing from arrays

### HTF Alignment missing
1. Verify HTF variables are populated
2. Check JSON formatting
3. Verify helper function returns valid JSON
4. Check for null/na values

---

## Support

If you encounter issues:
1. Check Railway logs: `https://railway.app/project/[project-id]/logs`
2. Run gap detection: `python test_hybrid_sync_status.py`
3. Check SIGNAL_CREATED data: `python check_signal_created_data.py`
4. Review audit log: `SELECT * FROM sync_audit_log ORDER BY action_timestamp DESC LIMIT 50`

---

**Once these webhooks are added, the Hybrid Signal Synchronization System will be complete and operational at 100% capacity.**

# FIX: Historical Webhook Spam

## Root Cause:

When the indicator loads on the chart, it processes ALL historical bars and finds completed trades from the past. It then sends ALL webhook events (ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT) for those historical trades simultaneously, causing:

1. Trades appear as COMPLETED immediately
2. MFE stuck at historical final value (2.95R)
3. All 4 events sent within milliseconds
4. Dashboard flooded with old data

## Evidence:

```
Trade: 2,025001112_154100_BULLISH
MFE_UPDATE    → 21:42:01.553525
ENTRY         → 21:42:01.553689  (0.16ms later)
BE_TRIGGERED  → 21:42:01.555119  (1.6ms later)
EXIT_BREAK_EVEN → 21:42:01.562624 (9ms later)
```

All 4 events sent in 9 milliseconds = historical replay, not real-time trading.

## The Fix:

Add `barstate.isrealtime` check to ALL webhook sending logic to prevent historical replay:

```pinescript
// 1. ENTRY WEBHOOK - Only send on real-time bars
if confirmed_this_bar and not webhook_sent_this_bar and barstate.isconfirmed and barstate.isrealtime and array.size(signal_entries) > 0

// 2. MFE UPDATE WEBHOOK - Only send on real-time bars
if barstate.isconfirmed and barstate.isrealtime and array.size(signal_entries) > 0 and array.size(active_signal_ids) > 0

// 3. BE TRIGGER WEBHOOK - Only send on real-time bars
if barstate.isconfirmed and barstate.isrealtime and array.size(signal_be_triggered) > 0 and array.size(active_signal_ids) > 0

// 4. COMPLETION WEBHOOK - Only send on real-time bars
if barstate.isconfirmed and barstate.isrealtime and array.size(signal_be_stopped) > 0 and array.size(signal_no_be_stopped) > 0 and array.size(active_signal_ids) > 0
```

## What This Does:

- `barstate.isrealtime` = true only when processing live market data
- `barstate.isrealtime` = false when processing historical bars on indicator load
- Webhooks only fire for actual real-time trading events
- Historical data still tracked internally for chart display
- No webhook spam on indicator reload

## Implementation:

Add `and barstate.isrealtime` to lines:
- Line ~982 (ENTRY webhook)
- Line ~1018 (MFE UPDATE webhook)
- Line ~1038 (BE TRIGGER webhook)
- Line ~1060 (COMPLETION webhook)

## Expected Result:

After fix:
- Only NEW signals generate ENTRY webhooks
- MFE updates sent once per bar in real-time
- BE triggers sent when actually hit
- Exits sent when stops actually hit
- No historical replay spam
- Dashboard shows accurate real-time data

## Deploy:

1. Update indicator code
2. Save indicator in TradingView
3. Reload chart (triggers historical processing without webhooks)
4. Wait for next real-time signal
5. Verify only ENTRY webhook sent initially
6. Verify MFE updates come bar-by-bar
7. Verify completion only when stop actually hit

# Position Sizing System Status

## What Works ✅
- FVG signal detection (blue/red triangles)
- HTF bias filtering
- Confirmation monitoring (waits for close above/below signal)
- Entry price calculation (confirmation close)
- Position sizing table display
- Contract size calculation
- Real-time updates

## What Needs Fixing ❌
- **Stop loss calculation is incorrect**
- Currently placing SL too far from entry
- Should be finding pivot 2 candles before signal candle
- Logic exists but pivot detection failing

## The Issue
In your screenshot:
- Blue triangle = signal candle
- Green line = entry (correct)
- Red line = my SL calculation (wrong - too far)
- Yellow line = correct SL (at pivot 2 candles before signal)

## The Fix Needed
When signal candle is lowest point and NOT a pivot:
- Search left 5 candles for pivot
- Should find pivot at `bars_since_signal + 2`
- Use that pivot low - 25pts as stop loss

## Current File
`complete_automated_trading_system.pine` - lines 220-280 (bullish SL calc)

The pivot detection logic at lines 260-270 should be finding this but isn't working correctly.

## Next Steps
1. Fix pivot detection in the "search left 5 candles" section
2. Verify it finds the pivot 2 candles before signal
3. Test on your chart to confirm yellow line matches red line

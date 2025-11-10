# Deploy Strategy Webhook Support

## Changes Made

Updated `web_server.py` to support BOTH webhook formats:

### 1. Dual Format Detection
- **Strategy format**: Uses `"type"` field (signal_created, mfe_update, be_triggered, signal_completed)
- **Indicator format**: Uses `"automation_stage"` field (SIGNAL_DETECTED, MFE_UPDATE, etc.)

### 2. Updated Handlers
- **handle_entry_signal**: Accepts both `signal_id`/`bias`/`sl_price` (strategy) and `trade_id`/`direction`/`stop_loss` (indicator)
- **handle_mfe_update**: Accepts both `be_mfe`/`no_be_mfe` (strategy) and `mfe` (indicator)
- **handle_be_trigger**: NEW - Handles break-even trigger events from strategy
- **handle_exit_signal**: Accepts both `final_be_mfe`/`final_no_be_mfe` (strategy) and `final_mfe` (indicator)

### 3. Field Mapping
Strategy → Database:
- `signal_id` → `trade_id`
- `bias` (Bullish/Bearish) → `direction` (LONG/SHORT)
- `sl_price` → `stop_loss`
- `no_be_mfe` → `mfe` (primary MFE value)

## Deployment Steps

### Using GitHub Desktop:

1. **Open GitHub Desktop**
2. **Review changes** in web_server.py
3. **Commit** with message: "Add strategy webhook format support"
4. **Push to main** branch
5. **Wait 2-3 minutes** for Railway auto-deploy
6. **Test** with your TradingView alert

### Manual Git (if needed):
```bash
git add web_server.py
git commit -m "Add strategy webhook format support"
git push origin main
```

## Testing After Deployment

Run the test script:
```bash
python test_strategy_webhook.py
```

All 4 tests should return status 200 with success messages.

## What This Fixes

✅ Strategy alerts now work with `/api/automated-signals`
✅ No need to change TradingView alert message
✅ Strategy sends its own JSON automatically
✅ Dashboard will show signals in real-time
✅ MFE tracking works with BE=1 and No BE strategies

## Next Steps

1. Deploy these changes
2. Wait for strategy to generate a signal
3. Check Automated Signals Dashboard
4. Signals should appear automatically!

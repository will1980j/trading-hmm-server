# 🔄 Automated Contract Rollover System

## Overview
This system automatically detects and handles futures contract rollovers (like NQ1! → NQZ24) without manual intervention.

## Key Features

### 1. **Automatic Detection** 🔍
- Monitors incoming signals for new contract symbols
- Detects when TradingView switches from generic (NQ1!) to specific (NQZ24) contracts
- Handles all major futures: NQ, ES, YM, RTY

### 2. **Seamless Auto-Population** 🎯
- Signal Lab auto-population now works with ANY active NQ contract
- No more missed signals due to contract changes
- Automatically updates the active contract when rollover detected

### 3. **Smart Contract Management** 🧠
- Tracks active contracts in database
- Compares contract expiry dates to determine newer contracts
- Updates historical data with new contract symbols

### 4. **Manual Override** ⚙️
- Contract Manager dashboard at `/contract-manager`
- Force manual rollovers if needed
- Monitor rollover history and recent signals

## How It Works

### Automatic Process:
1. **Signal Received**: TradingView sends signal with new contract (e.g., NQZ24)
2. **Detection**: System detects this differs from current active contract (NQ1!)
3. **Validation**: Confirms NQZ24 is a valid, newer contract
4. **Rollover**: Updates active contract from NQ1! → NQZ24
5. **Auto-Population**: Signal Lab now auto-populates NQZ24 signals
6. **Logging**: Records rollover event for audit trail

### Manual Process:
1. Visit `/contract-manager` dashboard
2. View current active contracts and recent signals
3. Force rollover if needed using manual controls
4. Monitor rollover history

## API Endpoints

- `GET /api/contracts/status` - Get current contract status
- `POST /api/contracts/force-rollover` - Manually force rollover
- `POST /api/contracts/detect-rollover` - Detect potential rollovers

## Files Added/Modified

### New Files:
- `contract_manager.py` - Core rollover logic
- `contract_manager.html` - Management dashboard
- `test_contract_rollover.py` - Test script

### Modified Files:
- `web_server.py` - Integrated contract manager into webhook handler
- Auto-population logic now uses dynamic active contracts

## Database Tables Created

### `contract_settings`
- Stores current active contracts
- JSON format: `{"NQ": "NQZ24", "ES": "ESU24", ...}`

### `contract_rollover_log`
- Audit trail of all rollovers
- Tracks old → new contract changes with timestamps

## Benefits

1. **Zero Downtime** - No missed signals during contract rollovers
2. **Fully Automated** - No manual intervention required
3. **Audit Trail** - Complete history of all contract changes
4. **Manual Override** - Can force rollovers if needed
5. **Multi-Symbol** - Handles NQ, ES, YM, RTY automatically

## Usage

### Normal Operation:
- System runs automatically
- No action required during contract rollovers
- Signal Lab continues auto-populating seamlessly

### Manual Monitoring:
1. Visit `/contract-manager` dashboard
2. Check active contracts and recent signals
3. View rollover history
4. Force manual rollover if needed

### Troubleshooting:
- Check `/api/contracts/status` for current state
- Use `/api/contracts/detect-rollover` to check for pending rollovers
- Monitor server logs for rollover events

## Example Rollover Event

```
🔄 CONTRACT ROLLOVER: NQ1! → NQZ24
📊 Webhook received: NQZ24 Bullish at 15,234.50
🎯 Auto-population check: Symbol=NQZ24, Active NQ=NQZ24, HTF=true, Should populate=true
✅ NQZ24 HTF ALIGNED: Bullish - Auto-populating Signal Lab
```

The system is now fully automated and will handle all future contract rollovers without any manual intervention required!
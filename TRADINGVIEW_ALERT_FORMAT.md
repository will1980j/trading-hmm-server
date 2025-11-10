# TradingView Alert Format for Automated Signals

## Webhook URL
```
https://web-production-cd33.up.railway.app/api/automated-signals
```

## Required Format

The webhook expects JSON with specific event types. Your TradingView indicator must send alerts in this exact format:

### ENTRY Signal (When Trade Starts)

```json
{
  "event_type": "ENTRY",
  "trade_id": "TRADE_{{time}}",
  "direction": "LONG",
  "entry_price": {{close}},
  "stop_loss": 16000.00,
  "session": "NY AM",
  "bias": "Bullish"
}
```

**Required Fields:**
- `event_type`: Must be "ENTRY"
- `trade_id`: Unique identifier (use timestamp or counter)
- `direction`: "LONG" or "SHORT"
- `entry_price`: Entry price (number)
- `stop_loss`: Stop loss price (number)
- `session`: Trading session (e.g., "NY AM", "LONDON", "ASIA")
- `bias`: Market bias (e.g., "Bullish", "Bearish")

### MFE_UPDATE Signal (During Trade)

```json
{
  "event_type": "MFE_UPDATE",
  "trade_id": "TRADE_12345",
  "current_price": {{close}},
  "mfe": 2.5
}
```

**Required Fields:**
- `event_type`: Must be "MFE_UPDATE"
- `trade_id`: Same ID from ENTRY signal
- `current_price`: Current market price
- `mfe`: Maximum Favorable Excursion in R-multiples

### EXIT_SL Signal (Stop Loss Hit)

```json
{
  "event_type": "EXIT_SL",
  "trade_id": "TRADE_12345",
  "exit_price": {{close}},
  "final_mfe": 0.5
}
```

**Required Fields:**
- `event_type`: Must be "EXIT_SL"
- `trade_id`: Same ID from ENTRY signal
- `exit_price`: Exit price where stopped out
- `final_mfe`: Final MFE achieved before stop

### EXIT_BE Signal (Break Even Hit)

```json
{
  "event_type": "EXIT_BE",
  "trade_id": "TRADE_12345",
  "exit_price": {{close}},
  "final_mfe": 1.8
}
```

**Required Fields:**
- `event_type`: Must be "EXIT_BE"
- `trade_id`: Same ID from ENTRY signal
- `exit_price`: Exit price at break even
- `final_mfe`: Final MFE achieved before BE

## TradingView Alert Setup

### Step 1: Create Alert Condition
In your indicator, use `alertcondition()` or `alert()` to trigger on signals.

### Step 2: Alert Message Format
Use this format in your alert message field:

```
{
  "event_type": "ENTRY",
  "trade_id": "TRADE_{{timenow}}",
  "direction": "{{strategy.position_size > 0 ? 'LONG' : 'SHORT'}}",
  "entry_price": {{close}},
  "stop_loss": {{plot_0}},
  "session": "{{session_name}}",
  "bias": "{{bias_value}}"
}
```

### Step 3: Webhook Configuration
- Check "Webhook URL"
- Enter: `https://web-production-cd33.up.railway.app/api/automated-signals`
- Set "Webhook" as notification method

## Example: Complete Trade Lifecycle

### 1. Signal Appears (Blue Triangle)
```json
{
  "event_type": "ENTRY",
  "trade_id": "TRADE_1699876543",
  "direction": "LONG",
  "entry_price": 16100.00,
  "stop_loss": 16050.00,
  "session": "NY AM",
  "bias": "Bullish"
}
```

### 2. Price Moves Favorably
```json
{
  "event_type": "MFE_UPDATE",
  "trade_id": "TRADE_1699876543",
  "current_price": 16150.00,
  "mfe": 1.0
}
```

### 3. Trade Exits
```json
{
  "event_type": "EXIT_BE",
  "trade_id": "TRADE_1699876543",
  "exit_price": 16100.00,
  "final_mfe": 2.5
}
```

## What Happens on Backend

1. **ENTRY**: Creates new trade record, calculates R-targets (1R, 2R, 3R, 5R, 10R, 20R)
2. **MFE_UPDATE**: Updates current MFE for active trade
3. **EXIT_SL/EXIT_BE**: Marks trade as resolved with final MFE

## Dashboard Display

Once signals are received, they appear on:
- `/automated-signals` dashboard
- Calendar view with trade counts
- Real-time stats (Total Signals, Pending, Confirmed, Avg MFE)
- WebSocket live updates

## Testing

Send a test signal:
```bash
curl -X POST https://web-production-cd33.up.railway.app/api/automated-signals \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "ENTRY",
    "trade_id": "TEST_001",
    "direction": "LONG",
    "entry_price": 16100.00,
    "stop_loss": 16050.00,
    "session": "NY AM",
    "bias": "Bullish"
  }'
```

## Common Issues

1. **Missing event_type**: Returns 400 error
2. **Invalid prices**: Returns 400 error "Invalid price data"
3. **Zero risk distance**: Returns 400 error "Risk distance cannot be zero"
4. **Wrong trade_id**: MFE_UPDATE/EXIT won't find the trade

## Your Indicator Must:

1. Generate unique `trade_id` for each signal
2. Send ENTRY when signal appears
3. Send MFE_UPDATE periodically while trade is active
4. Send EXIT_SL or EXIT_BE when trade closes
5. Use consistent trade_id across all events for same trade

This is a complete automation system - not a simple signal logger!

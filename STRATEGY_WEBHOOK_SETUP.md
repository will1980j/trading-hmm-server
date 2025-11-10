# Strategy Webhook Setup Guide

## ✅ GOOD NEWS: Your strategy already sends webhooks!

The `complete_automated_trading_system.pine` strategy already has webhook alerts built-in at lines 900-981.

## 📋 How to Set Up the Alert in TradingView

### Step 1: Add the Strategy to Your Chart
1. Open your NASDAQ chart in TradingView
2. Click "Indicators" and search for "Complete Automated Trading System"
3. Add it to your chart

### Step 2: Create the Alert
1. Click the **Alert** button (clock icon) in TradingView
2. Set **Condition** to: `Complete Automated Trading System - FVG + Position Sizing`
3. Set **Alert name** to: `Automated Signals Webhook`
4. Set **Frequency** to: `All`

### Step 3: Configure the Webhook
1. Check the **Webhook URL** box
2. Enter: `https://web-production-cd33.up.railway.app/api/automated-signals`
3. **CRITICAL:** Leave the **Message** field EMPTY
   - The strategy sends its own JSON messages
   - Don't add any custom message text

### Step 4: Save the Alert
1. Click **Create**
2. The alert will now send 4 types of webhooks:
   - **Signal Created** - When entry conditions are met
   - **MFE Update** - Every bar while signal is active
   - **BE Triggered** - When price reaches +1R
   - **Signal Completed** - When stop loss is hit

## 🎯 What the Strategy Sends

### 1. Signal Created (Entry Conditions Met)
```json
{
  "type": "signal_created",
  "signal_id": "20241110_143025_BULLISH",
  "date": "2024-11-10",
  "time": "14:30:25",
  "bias": "Bullish",
  "session": "NY PM",
  "entry_price": 4156.25,
  "sl_price": 4153.75,
  "risk_distance": 2.50,
  "be_price": 4156.25,
  "target_1r": 4158.75,
  "target_2r": 4161.25,
  "target_3r": 4163.75,
  "be_hit": false,
  "be_mfe": 0.00,
  "no_be_mfe": 0.00,
  "status": "active",
  "timestamp": 1699632625000
}
```

### 2. MFE Update (Every Bar)
```json
{
  "type": "mfe_update",
  "signal_id": "20241110_143025_BULLISH",
  "current_price": 4157.50,
  "be_mfe": 0.50,
  "no_be_mfe": 0.50,
  "lowest_low": 4155.00,
  "highest_high": 4157.50,
  "status": "active",
  "timestamp": 1699632685000
}
```

### 3. BE Triggered (When +1R Reached)
```json
{
  "type": "be_triggered",
  "signal_id": "20241110_143025_BULLISH",
  "be_hit": true,
  "be_mfe": 1.00,
  "no_be_mfe": 1.00,
  "timestamp": 1699632745000
}
```

### 4. Signal Completed (Stop Loss Hit)
```json
{
  "type": "signal_completed",
  "signal_id": "20241110_143025_BULLISH",
  "completion_reason": "be_stop_loss_hit",
  "final_be_mfe": 2.50,
  "final_no_be_mfe": 3.25,
  "status": "completed",
  "timestamp": 1699633805000
}
```

## ⚠️ Important Notes

1. **Use the STRATEGY, not the indicator** - The strategy has position sizing and webhook logic
2. **Leave Message field EMPTY** - The strategy generates its own JSON
3. **Set Frequency to "All"** - This allows MFE updates every bar
4. **The strategy must be running on your chart** - Alerts only work when the strategy is active

## 🔍 Troubleshooting

### No signals appearing on dashboard?
1. Check that the alert is active in TradingView (green checkmark)
2. Verify the webhook URL is correct
3. Check that the strategy is generating signals (blue/red triangles on chart)
4. Look at the TradingView alert log to see if webhooks are being sent

### Wrong data format?
- Make sure you didn't add any custom message text
- The strategy sends JSON automatically
- The webhook endpoint expects the exact JSON format shown above

## ✅ Ready to Test

Once you've set up the alert:
1. Wait for the strategy to generate a signal (blue or red triangle)
2. Check the Automated Signals Dashboard
3. You should see the signal appear with all details
4. MFE will update in real-time as price moves

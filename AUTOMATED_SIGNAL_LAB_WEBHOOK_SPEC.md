# Automated Signal Lab Webhook System Specification

## Overview
Automate Signal Lab data entry using TradingView webhooks from the complete_automated_trading_system indicator. The indicator will send all required data to populate Signal Lab entries automatically, eliminating manual data entry.

## Signal Lab Manual Entry Fields (Current)

From `signal_analysis_lab.html`:
1. **Date** - Signal date
2. **Time** - Entry time (24hr format)
3. **Bias** - Bullish/Bearish
4. **Session** - Auto-assigned based on time
5. **BE=1 Hit** - Checkbox (was break-even achieved?)
6. **BE=1 MFE** - MFE value for BE=1 strategy
7. **BE=None MFE** - MFE value for No BE strategy

## Webhook Data Flow

### 1. Signal Creation Webhook
**Sent when:** Trade is ready (entry conditions met)

**Payload:**
```json
{
  "type": "signal_created",
  "signal_id": "20250108_143052_BULLISH",
  "date": "2025-01-08",
  "time": "14:30:52",
  "bias": "Bullish",
  "session": "NY PM",
  "entry_price": 4156.25,
  "sl_price": 4145.50,
  "risk_distance": 10.75,
  "be_price": 4156.25,
  "target_1r": 4167.00,
  "target_2r": 4177.75,
  "target_3r": 4188.50,
  "be_hit": false,
  "be_mfe": 0.00,
  "no_be_mfe": 0.00,
  "status": "active",
  "timestamp": 1704729052000
}
```

### 2. MFE Update Webhook
**Sent when:** Every bar close while trade is active

**Payload:**
```json
{
  "type": "mfe_update",
  "signal_id": "20250108_143052_BULLISH",
  "current_price": 4162.00,
  "be_hit": false,
  "be_mfe": 0.54,
  "no_be_mfe": 0.54,
  "lowest_low": 4148.25,
  "highest_high": 4162.00,
  "status": "active",
  "timestamp": 1704729112000
}
```

### 3. BE Trigger Webhook
**Sent when:** Price reaches +1R (BE trigger point)

**Payload:**
```json
{
  "type": "be_triggered",
  "signal_id": "20250108_143052_BULLISH",
  "be_hit": true,
  "be_mfe": 1.02,
  "no_be_mfe": 1.02,
  "timestamp": 1704729172000
}
```

### 4. Completion Webhook
**Sent when:** Stop loss is hit (trade completes)

**Payload:**
```json
{
  "type": "signal_completed",
  "signal_id": "20250108_143052_BULLISH",
  "completion_reason": "stop_loss_hit",
  "be_hit": true,
  "final_be_mfe": 1.19,
  "final_no_be_mfe": 2.53,
  "status": "completed",
  "timestamp": 1704729232000
}
```

## Platform Backend Processing

### Database Schema (Signal Lab V2 Automated)
```sql
CREATE TABLE signal_lab_automated (
    id SERIAL PRIMARY KEY,
    signal_id VARCHAR(50) UNIQUE NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    bias VARCHAR(10) NOT NULL,  -- 'Bullish' or 'Bearish'
    session VARCHAR(20) NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    sl_price DECIMAL(10,2) NOT NULL,
    risk_distance DECIMAL(10,2) NOT NULL,
    be_price DECIMAL(10,2) NOT NULL,
    target_1r DECIMAL(10,2),
    target_2r DECIMAL(10,2),
    target_3r DECIMAL(10,2),
    be_hit BOOLEAN DEFAULT FALSE,
    be_mfe DECIMAL(10,2) DEFAULT 0.00,
    no_be_mfe DECIMAL(10,2) DEFAULT 0.00,
    lowest_low DECIMAL(10,2),
    highest_high DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active',  -- 'active' or 'completed'
    completion_reason VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Webhook Endpoint
**URL:** `https://web-production-cd33.up.railway.app/api/signal-lab-automated`
**Method:** POST
**Authentication:** None (TradingView webhooks)

### Backend Logic

**On signal_created:**
1. Create new record in `signal_lab_automated`
2. Initialize all fields from payload
3. Set status = 'active'

**On mfe_update:**
1. Find record by `signal_id`
2. Update `be_mfe`, `no_be_mfe`, `lowest_low`, `highest_high`
3. Update `updated_at` timestamp

**On be_triggered:**
1. Find record by `signal_id`
2. Set `be_hit` = true
3. Update `be_mfe` to value at trigger

**On signal_completed:**
1. Find record by `signal_id`
2. Update `final_be_mfe`, `final_no_be_mfe`
3. Set `status` = 'completed'
4. Set `completion_reason`

## Pine Script Implementation

### Webhook Alert Configuration
```pinescript
// Webhook URL
webhook_url = "https://web-production-cd33.up.railway.app/api/signal-lab-automated"

// Signal Creation Alert
if trade_ready and not confirmed_this_bar
    signal_id = str.format("{0}_{1}_{2}", 
        str.format_time(time, "yyyyMMdd"), 
        str.format_time(time, "HHmmss"),
        active_signal)
    
    alert_message = str.format('{"type":"signal_created","signal_id":"{0}","date":"{1}","time":"{2}","bias":"{3}","session":"{4}","entry_price":{5},"sl_price":{6},"risk_distance":{7},"be_price":{8},"target_1r":{9},"target_2r":{10},"target_3r":{11},"be_hit":false,"be_mfe":0.00,"no_be_mfe":0.00,"status":"active","timestamp":{12}}',
        signal_id, 
        str.format_time(time, "yyyy-MM-dd"),
        str.format_time(time, "HH:mm:ss"),
        active_signal,
        current_session,
        entry_price,
        stop_loss_price,
        risk_distance,
        entry_price,
        entry_price + risk_distance,
        entry_price + (2 * risk_distance),
        entry_price + (3 * risk_distance),
        time)
    
    alert(alert_message, alert.freq_once_per_bar)

// MFE Update Alert (every bar for active signals)
// BE Trigger Alert
// Completion Alert
```

## Dashboard Integration

### Signal Lab V2 Automated Dashboard
**URL:** `/signal-lab-v2-automated`

**Features:**
- Display all automated signals in table format
- Real-time updates via WebSocket
- Filter by date, bias, session, status
- Export to CSV
- Compare with manual Signal Lab entries
- Show BE=1 vs No BE MFE side-by-side

**Table Columns:**
1. Date
2. Time
3. Bias
4. Session
5. Entry Price
6. SL Price
7. BE Hit (✓/✗)
8. BE=1 MFE
9. No BE MFE
10. Status (Active/Complete)
11. Actions (View Details)

## Strategy Integration

All existing strategies that use Signal Lab data will automatically work with automated data:
- Strategy Optimizer
- Strategy Comparison
- Time Analysis
- ML Dashboard
- Financial Summary
- Reports

## Benefits

1. **Zero Manual Entry** - Completely automated data collection
2. **Real-Time Updates** - MFE values update live
3. **100% Accuracy** - No human error in data entry
4. **Complete History** - Every signal captured automatically
5. **Dual MFE Tracking** - BE=1 vs No BE comparison built-in
6. **Strategy Validation** - Immediate data for backtesting
7. **Scalable** - Handle unlimited signals without manual work

## Implementation Plan

1. **Phase 1:** Create database schema and webhook endpoint
2. **Phase 2:** Implement Pine Script webhook alerts
3. **Phase 3:** Build automated Signal Lab dashboard
4. **Phase 4:** Integrate with existing strategy tools
5. **Phase 5:** Add real-time WebSocket updates
6. **Phase 6:** Create comparison view (manual vs automated)

## Next Steps

1. Create `signal_lab_automated` table in Railway PostgreSQL
2. Build `/api/signal-lab-automated` webhook endpoint
3. Add webhook alert logic to `complete_automated_trading_system.pine`
4. Create Signal Lab V2 Automated dashboard
5. Test with live TradingView data
6. Deploy to production

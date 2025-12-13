# Complete Signal Data Specification

**All data points tracked for each signal in the Automated Signals system**

---

## 📊 Signal Lifecycle Events

Each signal goes through multiple events, each capturing different data:

1. **SIGNAL_CREATED** - Triangle appears (before confirmation)
2. **ENTRY** - Signal confirmed and entered
3. **MFE_UPDATE** - Continuous tracking (every minute)
4. **BE_TRIGGERED** - Break even achieved (+1R)
5. **EXIT_SL** - Stopped out at original stop
6. **EXIT_BE** - Stopped out at break even
7. **CANCELLED** - Signal cancelled before confirmation

---

## 🔵 SIGNAL_CREATED Event Data

**When:** Triangle first appears on chart (before confirmation)

### Core Identity
- `trade_id` - Unique identifier (YYYYMMDD_HHMMSS000_DIRECTION)
- `event_type` - "SIGNAL_CREATED"
- `timestamp` - When triangle appeared (UTC)
- `signal_date` - Date in NY timezone (YYYY-MM-DD)
- `signal_time` - Time in NY timezone (HH:MM:SS)

### Signal Details
- `direction` - "Bullish" or "Bearish"
- `session` - Trading session (ASIA, LONDON, NY PRE, NY AM, NY LUNCH, NY PM)
- `signal_price` - Price when triangle appeared

### HTF Alignment (at signal moment)
- `htf_alignment` - JSON object:
  ```json
  {
    "daily": "Bullish",
    "h4": "Neutral",
    "h1": "Bullish",
    "m15": "Bullish",
    "m5": "Bullish",
    "m1": "Bullish"
  }
  ```

### Market Context
- `market_state` - JSON object:
  ```json
  {
    "trend_regime": "Bullish",
    "volatility_regime": "NORMAL"
  }
  ```

### Setup Details
- `setup` - JSON object:
  ```json
  {
    "family": "FVG_CORE",
    "variant": "HTF_ALIGNED",
    "signal_strength": 75
  }
  ```

### Metadata
- `data_source` - "indicator_realtime"
- `confidence_score` - 1.0 (perfect)
- `raw_payload` - Complete JSON payload

---

## 🟢 ENTRY Event Data

**When:** Signal confirmed (bullish candle closes above signal high, or bearish below signal low)

### Core Identity
- `trade_id` - Same as SIGNAL_CREATED
- `event_type` - "ENTRY"
- `timestamp` - When confirmation happened (UTC)

### Entry Details
- `entry_price` - Calculated entry price (open of bar after confirmation)
- `stop_loss` - Calculated stop loss price
- `risk_distance` - Distance from entry to stop (in points)
- `direction` - "LONG" or "SHORT"

### Timing
- `signal_date` - Original signal date
- `signal_time` - Original signal time
- `confirmation_time` - When confirmation happened
- `bars_to_confirmation` - Number of bars from signal to confirmation

### Session & Context
- `session` - Trading session
- `htf_alignment` - HTF alignment at confirmation (should match SIGNAL_CREATED)

### Targets (Extended)
- `targets_extended` - JSON object with 1R through 20R targets:
  ```json
  {
    "1R": 25722.00,
    "2R": 25760.50,
    "3R": 25799.00,
    "5R": 25876.00,
    "10R": 26068.50,
    "15R": 26261.00,
    "20R": 26453.50
  }
  ```

### Initial MFE/MAE
- `be_mfe` - 0.0 (at entry)
- `no_be_mfe` - 0.0 (at entry)
- `mae_global_r` - 0.0 (at entry)

### Metadata
- `data_source` - "indicator_realtime" or "reconciled"
- `confidence_score` - 1.0 or calculated
- `raw_payload` - Complete JSON payload

---

## 🔄 MFE_UPDATE Event Data

**When:** Every minute while trade is active

### Core Identity
- `trade_id` - Same as ENTRY
- `event_type` - "MFE_UPDATE"
- `timestamp` - Update time (UTC)

### Current State
- `current_price` - Current market price
- `signal_age_seconds` - Time since entry (in seconds)

### MFE Tracking (Dual Strategy)
- `be_mfe` - MFE for BE=1 strategy (caps at 1.0 after BE triggered)
- `no_be_mfe` - MFE for No-BE strategy (continues to track)
- `mae_global_r` - Maximum adverse excursion (worst drawdown)

### Price Context
- `entry_price` - Reference entry price
- `stop_loss` - Reference stop loss
- `risk_distance` - Reference risk distance

### Session
- `session` - Current trading session
- `direction` - Trade direction

### Metadata
- `data_source` - "indicator_realtime" or "backend_calculated"
- `confidence_score` - 1.0 or 0.8 (if calculated)
- `raw_payload` - Complete JSON payload

---

## ⚡ BE_TRIGGERED Event Data

**When:** Price reaches +1R (break even trigger point)

### Core Identity
- `trade_id` - Same as ENTRY
- `event_type` - "BE_TRIGGERED"
- `timestamp` - When +1R was achieved (UTC)

### State at Trigger
- `current_price` - Price when +1R hit
- `be_mfe` - 1.0 (by definition)
- `no_be_mfe` - 1.0 (at this moment, both are same)

### Context
- `entry_price` - Reference
- `stop_loss` - Original stop (about to move to entry)
- `direction` - Trade direction
- `session` - Trading session

### Metadata
- `data_source` - "indicator_realtime"
- `confidence_score` - 1.0
- `raw_payload` - Complete JSON payload

---

## 🔴 EXIT_SL Event Data

**When:** Price hits original stop loss

### Core Identity
- `trade_id` - Same as ENTRY
- `event_type` - "EXIT_SL"
- `timestamp` - When stop was hit (UTC)

### Exit Details
- `exit_price` - Stop loss price
- `exit_reason` - "stop_loss_hit"

### Final MFE/MAE
- `be_mfe` - Final MFE for BE strategy
- `no_be_mfe` - Final MFE for No-BE strategy
- `mae_global_r` - Final MAE (worst drawdown)

### Trade Duration
- `signal_age_seconds` - Total trade duration
- Entry to exit time

### Context
- `entry_price` - Reference
- `stop_loss` - Reference
- `direction` - Trade direction
- `session` - Exit session

### Metadata
- `data_source` - "indicator_realtime"
- `confidence_score` - 1.0
- `raw_payload` - Complete JSON payload

---

## 🟡 EXIT_BE Event Data

**When:** Price returns to entry after BE was triggered

### Core Identity
- `trade_id` - Same as ENTRY
- `event_type` - "EXIT_BE"
- `timestamp` - When BE stop was hit (UTC)

### Exit Details
- `exit_price` - Entry price (break even)
- `exit_reason` - "break_even_stop"

### Final MFE/MAE
- `be_mfe` - Final MFE for BE strategy (typically 1.0)
- `no_be_mfe` - Final MFE for No-BE strategy (continues tracking)
- `mae_global_r` - Final MAE

### Trade Duration
- `signal_age_seconds` - Total trade duration

### Context
- `entry_price` - Reference
- `stop_loss` - Original stop
- `direction` - Trade direction
- `session` - Exit session

### Metadata
- `data_source` - "indicator_realtime"
- `confidence_score` - 1.0
- `raw_payload` - Complete JSON payload

---

## 🚫 CANCELLED Event Data

**When:** Opposite signal appears before confirmation

### Core Identity
- `trade_id` - Same as SIGNAL_CREATED
- `event_type` - "CANCELLED"
- `timestamp` - When cancellation occurred (UTC)

### Cancellation Details
- `cancel_reason` - "opposite_signal_appeared"
- `bars_pending` - How many bars signal was pending
- `cancelled_by` - Trade ID of opposite signal

### Context
- `direction` - Original signal direction
- `session` - Session when cancelled
- `signal_date` - Original signal date
- `signal_time` - Original signal time

### Metadata
- `data_source` - "indicator_realtime" or "backend_inferred"
- `confidence_score` - 1.0 or 0.95
- `raw_payload` - Complete JSON payload

---

## 📊 Complete Signal Data Model

### All Fields in Database

```sql
CREATE TABLE automated_signals (
    -- Core Identity
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(100),
    event_type VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW(),
    
    -- Signal Timing
    signal_date DATE,
    signal_time TIME,
    confirmation_time TIMESTAMP,
    bars_to_confirmation INTEGER,
    
    -- Trade Details
    direction VARCHAR(10),
    entry_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    risk_distance DECIMAL(10,2),
    current_price DECIMAL(10,2),
    exit_price DECIMAL(10,2),
    
    -- Session & Context
    session VARCHAR(20),
    bias VARCHAR(20),
    
    -- MFE/MAE Tracking
    mfe DECIMAL(10,4),              -- Legacy
    be_mfe DECIMAL(10,4),           -- BE=1 strategy MFE
    no_be_mfe DECIMAL(10,4),        -- No-BE strategy MFE
    mae_global_r DECIMAL(10,4),     -- Maximum adverse excursion
    final_mfe DECIMAL(10,4),        -- Final MFE at exit
    
    -- Targets
    targets JSONB,                  -- Basic targets
    targets_extended JSONB,         -- 1R through 20R
    
    -- HTF Alignment
    htf_alignment JSONB,            -- All timeframe biases
    
    -- Data Quality
    data_source VARCHAR(50),        -- indicator_realtime, reconciled, backend_calculated
    confidence_score DECIMAL(3,2),  -- 0.0 to 1.0
    reconciliation_timestamp TIMESTAMP,
    reconciliation_reason TEXT,
    payload_checksum VARCHAR(64),
    sequence_number BIGINT,
    
    -- Complete Payload
    raw_payload JSONB               -- Full webhook payload
);
```

---

## 🎯 Data Points by Category

### Timing Data (8 fields)
1. `timestamp` - Event timestamp (UTC)
2. `signal_date` - Signal date (NY timezone)
3. `signal_time` - Signal time (NY timezone)
4. `confirmation_time` - When confirmed
5. `bars_to_confirmation` - Bars from signal to confirmation
6. `signal_age_seconds` - Trade duration
7. `session` - Trading session
8. `event_type` - Lifecycle stage

### Price Data (6 fields)
1. `entry_price` - Entry execution price
2. `stop_loss` - Stop loss price
3. `risk_distance` - Entry to stop distance
4. `current_price` - Current market price
5. `exit_price` - Exit execution price
6. `signal_price` - Price when triangle appeared

### Performance Data (5 fields)
1. `be_mfe` - BE strategy MFE
2. `no_be_mfe` - No-BE strategy MFE
3. `mae_global_r` - Maximum adverse excursion
4. `final_mfe` - Final MFE at exit
5. `mfe` - Legacy MFE field

### Direction & Strategy (3 fields)
1. `direction` - LONG/SHORT or Bullish/Bearish
2. `bias` - HTF bias
3. `targets` / `targets_extended` - R-multiple targets

### HTF Alignment (6 timeframes)
1. Daily bias
2. 4-hour bias
3. 1-hour bias
4. 15-minute bias
5. 5-minute bias
6. 1-minute bias

### Market Context (2 fields)
1. `trend_regime` - Bullish/Bearish/Neutral
2. `volatility_regime` - HIGH/NORMAL/LOW

### Setup Quality (3 fields)
1. `setup.family` - FVG_CORE, IFVG, etc.
2. `setup.variant` - HTF_ALIGNED, ENGULFING, etc.
3. `setup.signal_strength` - 0-100 score

### Data Quality (5 fields)
1. `data_source` - Where data came from
2. `confidence_score` - Data reliability (0.0-1.0)
3. `reconciliation_timestamp` - When gap was filled
4. `reconciliation_reason` - Why gap was filled
5. `payload_checksum` - Data integrity check

### Complete Payload
- `raw_payload` - Full JSON with ALL data

---

## 📈 Data Accumulation Over Time

### At SIGNAL_CREATED (Triangle Appears)
**Data Points:** ~15
- Trade ID, timestamp, direction
- Signal date/time
- Session
- HTF alignment (6 timeframes)
- Market state (2 fields)
- Setup details (3 fields)

### At ENTRY (Confirmation)
**Data Points:** ~25
- All SIGNAL_CREATED data +
- Entry price, stop loss, risk distance
- Confirmation time, bars to confirmation
- Extended targets (20 targets)
- Initial MFE/MAE (0.0)

### During MFE_UPDATE (Every Minute)
**Data Points:** ~15 per update
- Current price
- BE MFE, No-BE MFE
- MAE
- Signal age
- Session
- Entry/stop reference

**Over 2-3 weeks:**
- Market hours: ~6.5 hours/day
- Updates: 390 minutes/day
- Total: 390 × 15 days = 5,850 MFE updates
- Data points: 5,850 × 15 = 87,750 data points!

### At EXIT (Trade Completes)
**Data Points:** ~20
- Exit price, exit reason
- Final BE MFE, final No-BE MFE
- Final MAE
- Total trade duration
- Session at exit

---

## 🎯 Complete Signal Data Summary

### Total Unique Fields: ~40

**Core Fields (10):**
1. trade_id
2. event_type
3. timestamp
4. signal_date
5. signal_time
6. direction
7. session
8. entry_price
9. stop_loss
10. risk_distance

**Performance Fields (5):**
11. be_mfe
12. no_be_mfe
13. mae_global_r
14. current_price
15. exit_price

**Timing Fields (3):**
16. confirmation_time
17. bars_to_confirmation
18. signal_age_seconds

**HTF Alignment (6):**
19. daily
20. h4
21. h1
22. m15
23. m5
24. m1

**Targets (20):**
25-44. 1R through 20R target prices

**Market Context (2):**
45. trend_regime
46. volatility_regime

**Setup Quality (3):**
47. setup_family
48. setup_variant
49. signal_strength

**Data Quality (5):**
50. data_source
51. confidence_score
52. reconciliation_timestamp
53. reconciliation_reason
54. payload_checksum

**Plus:**
- `raw_payload` - Complete JSON with everything

---

## 📊 Data Volume Analysis

### Single Signal (Complete Lifecycle)

**Events:** 7 (SIGNAL_CREATED, ENTRY, MFE_UPDATE×many, BE_TRIGGERED, EXIT)

**For 1-day trade:**
- SIGNAL_CREATED: 1 event
- ENTRY: 1 event
- MFE_UPDATE: ~390 events (6.5 hours × 60 minutes)
- BE_TRIGGERED: 1 event (if applicable)
- EXIT: 1 event
- **Total:** ~394 events

**For 2-week trade:**
- SIGNAL_CREATED: 1 event
- ENTRY: 1 event
- MFE_UPDATE: ~3,900 events (10 trading days × 390 minutes)
- BE_TRIGGERED: 1 event
- EXIT: 1 event
- **Total:** ~3,904 events

**For 3-week trade:**
- SIGNAL_CREATED: 1 event
- ENTRY: 1 event
- MFE_UPDATE: ~5,850 events (15 trading days × 390 minutes)
- BE_TRIGGERED: 1 event
- EXIT: 1 event
- **Total:** ~5,854 events

---

## 💾 Database Storage

### Current Database Size
- 36 signals
- ~6,000 MFE_UPDATE events
- Total rows: ~6,100

### Projected Growth

**With 50 signals/month:**
- Average trade duration: 1-3 days
- MFE updates per signal: ~400-1,200
- Monthly new rows: 50 × 600 = 30,000 rows
- Yearly: 360,000 rows

**With occasional long trades (2-3 weeks):**
- 1-2 long trades/month
- MFE updates per long trade: ~4,000-6,000
- Additional monthly rows: 8,000-12,000
- Yearly: 96,000-144,000 additional rows

**Total Yearly:** ~450,000-500,000 rows

**PostgreSQL Capacity:** Millions of rows (no problem)

---

## 🎯 What This Means for Long Trades

### ✅ System CAN Track Long Trades

**Database:**
- ✅ Can store 5,000+ MFE updates per trade
- ✅ No storage limitations
- ✅ Fast queries even with large datasets

**Dashboard:**
- ✅ Displays current MFE correctly
- ✅ No performance issues
- ✅ Real-time updates work

**Data Completeness:**
- ✅ Every minute tracked
- ✅ Complete MFE history
- ✅ Hybrid Sync fills gaps

### ⚠️ Limitations to Consider

**Indicator:**
- ⚠️ Array size limits (500 signals)
- ⚠️ Restart risk (loses tracking)
- ⚠️ Chart history limits (~7 days)

**Webhooks:**
- ⚠️ Rate limits (300/hour)
- ⚠️ Multiple long trades = high volume
- ⚠️ Could miss updates if rate limited

**Stop Detection:**
- ⚠️ Might miss intrabar stop hits
- ⚠️ Indicator restart could miss stop
- ⚠️ Example: Dec 8th trade still active when should be stopped

---

## 💡 Recommendations

### For Strategy Discovery (Current Phase)

**Accept These Limitations:**
- Some long trades might have incomplete data
- Occasional missed stops
- Focus on collecting ENOUGH data, not PERFECT data

**Why It's OK:**
- Need 300-600 signals for strategy discovery
- A few incomplete signals won't invalidate analysis
- Statistical significance matters more than perfection

### For Manual Trading (Months 12-24)

**Monitor These Metrics:**
- How many long trades do you typically have?
- Are you hitting rate limits?
- Are stops being detected correctly?

**Upgrade Triggers:**
- Consistently 5+ long trades
- Missing significant MFE data
- Stop detection failures

### For Automation (Months 24+)

**Must Have:**
- Real-time data integration (no rate limits)
- Backend-driven tracking (no indicator restart risk)
- Perfect stop detection (tick-level accuracy)

---

## 🎯 Bottom Line

**Your system tracks these data points for each signal:**
- **~50 unique fields** per signal
- **~400-6,000 events** per signal (depending on duration)
- **Complete lifecycle** from triangle to exit

**For 2-3 week trades:**
- ✅ System CAN handle it
- ✅ Database stores all data
- ✅ Dashboard displays correctly
- ⚠️ Might have some gaps (rate limits, indicator restart)
- ⚠️ Stop detection might miss some exits

**Good enough for strategy discovery?** YES ✅

**Good enough for manual trading?** YES ✅

**Good enough for automated trading?** NO ⚠️ (need real-time data)

**Your current phase (strategy discovery) doesn't require perfection. It requires ENOUGH good data to identify patterns. The system provides that.**

---

**Focus on collecting 300-600 signals over 6-12 months. The data quality is sufficient for discovering optimal strategy. Upgrade to real-time data later when automating.**

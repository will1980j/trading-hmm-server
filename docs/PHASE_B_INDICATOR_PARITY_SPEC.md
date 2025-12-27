# PHASE B — INDICATOR PARITY SPECIFICATION

**Source:** complete_automated_trading_system.pine (3269 lines)  
**Purpose:** Extract exact parity requirements for Pine → Python translation

---

## 1) INPUTS (PARAMETERS)

### Risk Management
- `account_size`: float, default=100000
- `risk_percent`: float, default=1.0, min=0.1, max=100, step=0.1
- `buffer_points`: float, default=0.25, min=0.01, step=0.01
- `auto_detect_contract`: bool, default=true
- `manual_point_value`: float, default=20.0, min=0.1

### HTF Bias Filter
- `use_daily`: bool, default=false
- `use_4h`: bool, default=false
- `use_1h`: bool, default=false
- `use_15m`: bool, default=false
- `use_5m`: bool, default=false

### Signal Filter
- `require_engulfing`: bool, default=false
- `require_sweep_engulfing`: bool, default=false

### Display
- `htf_aligned_only`: bool, default=false
- `triangle_size`: string, default="Small"
- `bull_color`: color, default=blue
- `bear_color`: color, default=red
- `neutral_color`: color, default=gray
- `show_htf_status`: bool, default=false
- `show_position_table`: bool, default=false
- `show_mfe_labels`: bool, default=false
- `track_be_mfe`: bool, default=false
- `show_entry_sl_lines`: bool, default=false

### Export/Debug
- `ARRAY_VERSION`: int, default=1, min=1
- `RECALCULATE_MFE`: bool, default=false
- `ENABLE_EXPORT`: bool, default=false
- `ENABLE_ALL_SIGNALS_EXPORT`: bool, default=false
- `ENABLE_LIVE_CONFIRMED_EXPORT`: bool, default=true
- `ENABLE_UNIFIED_SNAPSHOT`: bool, default=true
- `EXPORT_DELAY_BARS`: int, default=5, min=0, max=10

---

## 2) STATE (PERSISTENT VARS)

### Bias Calculation State (in get_bias())
- `var string bias` = "Neutral"
- `var float ath` = na (all-time high)
- `var float atl` = na (all-time low)
- `var bull_fvg_highs` = array<float>()
- `var bull_fvg_lows` = array<float>()
- `var bear_fvg_highs` = array<float>()
- `var bear_fvg_lows` = array<float>()
- `var bull_ifvg_highs` = array<float>()
- `var bull_ifvg_lows` = array<float>()
- `var bear_ifvg_highs` = array<float>()
- `var bear_ifvg_lows` = array<float>()

### Signal Confirmation State
- `var float signal_candle_high` = na
- `var float signal_candle_low` = na
- `var int signal_bar_index` = na
- `var int signal_candle_time` = na
- `var string active_signal` = "None"
- `var bool waiting_for_confirmation` = false

### Trade State
- `var float entry_price` = na
- `var float stop_loss_price` = na
- `var float risk_distance` = na
- `var int contract_size` = na
- `var bool trade_ready` = false
- `var bool confirmed_this_bar` = false

### Multi-Signal Tracking Arrays (Confirmed Signals)
- `var array<float> signal_entries`
- `var array<float> signal_stops`
- `var array<float> signal_risks`
- `var array<string> signal_directions`
- `var array<float> signal_mfes`
- `var array<float> signal_be_mfes`
- `var array<float> signal_maes`
- `var array<bool> signal_be_triggered`
- `var array<bool> signal_be_stopped`
- `var array<bool> signal_no_be_stopped`
- `var array<bool> signal_completes`
- `var array<int> signal_entry_times`
- `var array<int> signal_triangle_times`
- `var array<int> signal_completed_times`
- `var array<float> signal_lowest_lows`
- `var array<float> signal_highest_highs`
- `var array<bool> signal_has_entered`
- `var array<int> signal_entry_bar_index`
- `var array<string> confirmed_trade_ids`

### All Signals Tracking Arrays (Every Triangle)
- `var array<int> all_signal_times`
- `var array<string> all_signal_directions`
- `var array<string> all_signal_status`
- `var array<int> all_signal_confirmation_times`
- `var array<int> all_signal_bars_to_confirm`
- `var array<string> all_signal_daily_bias`
- `var array<string> all_signal_h4_bias`
- `var array<string> all_signal_h1_bias`
- `var array<string> all_signal_m15_bias`
- `var array<string> all_signal_m5_bias`
- `var array<string> all_signal_m1_bias`
- `var array<int> all_signal_confirmed_index`
- `var array<string> all_signal_trade_ids`

---

## 3) CORE COMPUTATIONS (ORDER MATTERS)

### Module 1: Engulfing Detection
**Dependencies:** open, close, high, low (current and [1])  
**Outputs:**
- `bearish_engulfing`: bool
- `bullish_engulfing`: bool
- `bearish_sweep_engulfing`: bool
- `bullish_sweep_engulfing`: bool

**Logic:**
- Bearish engulfing: curr_close < curr_open AND prev_close > prev_open AND curr_open >= prev_close AND curr_close < prev_open
- Bullish engulfing: curr_close > curr_open AND prev_close < prev_open AND curr_open <= prev_close AND curr_close > prev_open
- Sweep engulfing adds: high > high[1] (bearish) or low < low[1] (bullish) AND close beyond prev_close

### Module 2: FVG/IFVG Bias Calculation
**Dependencies:** open, high, low, close (current and historical)  
**Outputs:**
- `bias`: string ("Bullish", "Bearish", "Neutral")

**Logic (executed on barstate.isconfirmed):**
1. Update ATH/ATL
2. Check if close > ATH[1] → bias = "Bullish"
3. Check if close < ATL[1] → bias = "Bearish"
4. Detect bullish FVG: high[2] < low[0]
5. Detect bearish FVG: low[2] > high[0]
6. Store FVG levels in arrays
7. Check for IFVG (inverse FVG): close crosses through opposite FVG
8. Update bias on IFVG detection
9. Clean up invalidated IFVGs

### Module 3: HTF Bias Calculation
**Dependencies:** get_bias() function, request.security()  
**Outputs:**
- `daily_bias`: string
- `h4_bias`: string
- `h1_bias`: string
- `m15_bias`: string
- `m5_bias`: string

**Logic:**
- Uses request.security() to call get_bias() on higher timeframes
- Timeframes: "1D", "240", "60", "15", "5"

### Module 4: HTF Alignment Check
**Dependencies:** HTF bias values, use_* input flags  
**Outputs:**
- `htf_bullish`: bool
- `htf_bearish`: bool

**Logic:**
- For each timeframe: if filter enabled, check bias matches direction
- htf_bullish = ALL enabled filters show "Bullish"
- htf_bearish = ALL enabled filters show "Bearish"

### Module 5: Signal Generation
**Dependencies:** bias, bias[1], HTF alignment, engulfing filters  
**Outputs:**
- `fvg_bull_signal`: bool
- `fvg_bear_signal`: bool
- `show_bull_triangle`: bool
- `show_bear_triangle`: bool

**Logic:**
- FVG signal: bias changed to Bullish/Bearish AND (htf_aligned_only disabled OR HTF aligned)
- Triangle display: FVG signal AND (engulfing filter disabled OR engulfing detected)

### Module 6: Pivot Detection
**Dependencies:** high, low (current and historical)  
**Outputs:**
- `is_pivot_low(index)`: bool function
- `is_pivot_high(index)`: bool function

**Logic:**
- 3-candle pivot: low[index] < low[index-1] AND low[index] < low[index+1]
- 4-candle double-bottom: low[index] == low[index+1] AND low[index] < low[index-1] AND low[index] < low[index+2]
- Same for pivot highs (inverted)

---

## 4) SIGNAL EVENTS (WHAT WE MUST MATCH)

### Event 1: SIGNAL_CREATED (Triangle Appears)
**Trigger:** show_bull_triangle OR show_bear_triangle  
**Timing:** Bar close (barstate.isconfirmed)  
**Payload:**
- trade_id (canonical: YYYYMMDD_HHMMSSMMM_DIRECTION)
- direction (Bullish/Bearish)
- triangle_time (timestamp in ms)
- daily_bias, h4_bias, h1_bias, m15_bias, m5_bias, m1_bias
- status: "PENDING"

### Event 2: ENTRY (Confirmation + Entry Calculation)
**Trigger:** Confirmation candle closes (bullish above signal high OR bearish below signal low)  
**Timing:** Bar close after confirmation  
**Payload:**
- trade_id
- entry_price (open of bar after confirmation)
- stop_loss_price (calculated using pivot detection + buffer)
- risk_distance
- contract_size
- status: "CONFIRMED"

### Event 3: MFE_UPDATE (Every Bar While Active)
**Trigger:** Trade is active (entered but not completed)  
**Timing:** Every bar close  
**Payload:**
- trade_id
- be_mfe (MFE with BE=1 strategy)
- no_be_mfe (MFE with No BE strategy)
- mae_global_R (worst adverse excursion, <= 0.0)

### Event 4: BE_TRIGGERED (Breakeven Achieved)
**Trigger:** MFE >= 1.0R  
**Timing:** Bar close when +1R first achieved  
**Payload:**
- trade_id
- be_mfe (should be >= 1.0)

### Event 5: EXIT_STOP_LOSS (Trade Completed)
**Trigger:** Stop loss hit (BE=1 stop OR original stop)  
**Timing:** Bar close when stop hit  
**Payload:**
- trade_id
- final_mfe (be_mfe or no_be_mfe depending on strategy)
- exit_price
- completed: true

### Event 6: CANCELLED (Opposite Signal Before Confirmation)
**Trigger:** Opposite triangle appears while waiting for confirmation  
**Timing:** Bar close  
**Payload:**
- trade_id
- status: "CANCELLED"

---

## 5) PARITY TEST SURFACE (MINIMAL)

### A) Per-Bar Scalar Series (Must Match)
- `bias`: string per bar ("Bullish", "Bearish", "Neutral")
- `daily_bias`, `h4_bias`, `h1_bias`, `m15_bias`, `m5_bias`: string per bar
- `show_bull_triangle`: bool per bar
- `show_bear_triangle`: bool per bar
- `bullish_engulfing`, `bearish_engulfing`: bool per bar
- `bullish_sweep_engulfing`, `bearish_sweep_engulfing`: bool per bar

### B) Discrete Events (Must Match)
- Triangle events: timestamp, direction, HTF biases
- Confirmation events: timestamp, entry_price, stop_loss_price
- MFE updates: timestamp, be_mfe, no_be_mfe, mae
- BE trigger events: timestamp
- Exit events: timestamp, final_mfe
- Cancellation events: timestamp

### PARITY V1 TARGET (MINIMAL FIRST MODULE)

**Recommended:** Module 2 (FVG/IFVG Bias Calculation)

**Justification:**
- Zero dependencies on other modules (uses only OHLC)
- Core foundation for all signal generation
- Well-defined state machine
- Testable output: bias string per bar
- No lookahead, no security() calls in core logic
- Deterministic: same OHLC → same bias

**Parity Test:**
- Input: NQ 1-minute OHLCV bars (2024-01-02 to 2024-01-03)
- Output: bias value per bar
- Success: Python bias[i] == Pine bias[i] for all bars

**Excluded from Parity V1:**
- HTF bias (requires request.security())
- Engulfing detection (separate module)
- Signal generation (depends on bias)
- Pivot detection (separate module)
- MFE tracking (depends on signals)
- All export/webhook logic

---

**Next Step:** Implement get_bias() function in Python with exact FVG/IFVG logic, test on historical NQ data, verify 100% match with Pine output.

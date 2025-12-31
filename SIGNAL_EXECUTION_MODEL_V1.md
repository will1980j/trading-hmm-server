# Signal Execution Model V1 - Canonical Specification

**Version:** 1.0  
**Date:** 2025-12-28  
**Purpose:** Definitive specification for signal states, entry/stop/MFE models to ensure Python/backend matches Pine indicator

---

## 1. Signal States & Transitions

### 1.1 Candidate Signal (Triangle Appears)

**Definition:** A bias change triggers a triangle on the chart

**Timestamp Semantics:**
- **Event:** Triangle appears at bar CLOSE when bias changes
- **Timestamp:** Bar OPEN time of the bar where triangle appears
- **Example:** If bias changes at bar 19:14 (close), triangle timestamp = 19:14 (open)

**Conditions:**
- **Bullish:** Bias changes to "Bullish" (with optional HTF/engulfing filters)
- **Bearish:** Bias changes to "Bearish" (with optional HTF/engulfing filters)

**State:** PENDING (waiting for confirmation)

### 1.2 Confirmed Signal (Entry Ready)

**Definition:** Price action confirms the signal direction

**Confirmation Conditions:**
- **Bullish:** Close > signal_candle_high (any bar after signal)
- **Bearish:** Close < signal_candle_low (any bar after signal)

**Timestamp Semantics:**
- **Confirmation Bar:** The bar that closes above/below the signal candle
- **Confirmation Time:** Confirmation bar CLOSE time
- **Entry Time:** OPEN of the bar AFTER confirmation bar

**Entry Execution:**
- Entry happens at OPEN of the bar AFTER confirmation
- Entry price = OPEN of entry bar (not known until entry bar begins)
- Temporary entry_price = confirmation bar close (updated on next bar)

**State Transition:** PENDING → CONFIRMED

### 1.3 Cancelled Signal

**Definition:** Opposite signal appears before confirmation

**Cancellation Conditions:**
- **Bullish Pending:** Bearish triangle appears → Cancel bullish
- **Bearish Pending:** Bullish triangle appears → Cancel bearish

**Timestamp Semantics:**
- **Cancellation Time:** Bar OPEN time of the cancelling triangle
- **Event:** CANCELLED webhook sent

**State Transition:** PENDING → CANCELLED

---

## 2. Entry Model (Exact)

### 2.1 Entry Timing

**Rule:** Entry occurs at OPEN of the bar AFTER confirmation bar

**Sequence:**
1. Signal bar (triangle appears)
2. Wait for confirmation (any number of bars)
3. Confirmation bar (close above/below signal candle)
4. Entry bar (NEXT bar) - entry at OPEN

**Example:**
- Signal: 19:10 (triangle appears)
- Confirmation: 19:14 (close > signal_candle_high)
- Entry: 19:15 OPEN

### 2.2 Entry Price Definition

**Rule:** Entry price = OPEN of entry bar

**Implementation:**
- At confirmation: entry_price = close (temporary placeholder)
- At entry bar: entry_price = open (actual entry price)

**No Slippage/Offset:** Entry price is exact OPEN, no adjustments

---

## 3. Stop Model (Exact)

### 3.1 Initial Stop Price Definition

**Methodology:** Find lowest point (bullish) or highest point (bearish) from signal candle to confirmation candle, then apply pivot-based stop placement

**Bullish Stop Logic:**
1. Find lowest low from signal candle to confirmation candle
2. Check if lowest point is a 3-candle or 4-candle pivot
3. If pivot: stop = pivot_low - buffer (0.25 points default)
4. If not pivot: Search left 5 candles from signal for pivot
5. If pivot found: stop = pivot_low - buffer
6. If no pivot: stop = first_bearish_candle_low - buffer

**Bearish Stop Logic:**
1. Find highest high from signal candle to confirmation candle
2. Check if highest point is a 3-candle or 4-candle pivot
3. If pivot: stop = pivot_high + buffer (0.25 points default)
4. If not pivot: Search left 5 candles from signal for pivot
5. If pivot found: stop = pivot_high + buffer
6. If no pivot: stop = first_bullish_candle_high + buffer

### 3.2 Stop Validity

**When Valid:** Immediately upon confirmation (stop_loss_price calculated)

### 3.3 Stop Changes

**Rule:** Stop can ONLY move to breakeven (BE) when +1R achieved

**No Other Changes:** Stop does not trail, does not adjust based on market conditions

---

## 4. Dual MFE Model (Exact)

### 4.1 MFE_NoBE (No Breakeven Strategy)

**Evaluation Window:**
- **Start:** Entry bar (when entry_price is set to actual OPEN)
- **End:** Stop loss hit

**Extreme Tracking:**
- **Bullish:** Track highest_high from entry bar onwards
- **Bearish:** Track lowest_low from entry bar onwards
- **Update:** Every bar while trade is active

**Stop Detection:**
- **Bullish:** Stop hit when low <= stop_loss_price
- **Bearish:** Stop hit when high >= stop_loss_price
- **Critical:** Do NOT update extremes on the bar where stop is hit

**MFE Calculation:**
- **Bullish:** MFE_R = (highest_high - entry_price) / risk_distance
- **Bearish:** MFE_R = (entry_price - lowest_low) / risk_distance

**Trade End:** When stop loss is hit

### 4.2 MFE_BE (Breakeven Strategy, BE=1)

**BE Trigger Condition:**
- **Bullish:** highest_high >= entry_price + risk_distance (+1R achieved)
- **Bearish:** lowest_low <= entry_price - risk_distance (+1R achieved)

**Stop Movement:**
- **When Triggered:** Move stop to entry_price (breakeven)
- **BE Offset:** None (stop = exact entry price)
- **Timing:** Checked every bar after entry

**Intrabar Ordering:**
- BE trigger checked BEFORE stop hit check
- If +1R achieved, stop moves to BE immediately
- Then check if BE stop is hit on same bar

**MFE Tracking After BE:**
- **Continue tracking extremes** even after BE triggered
- MFE_BE continues to update until BE stop is hit
- **Critical:** BE MFE can NEVER exceed No-BE MFE (capped)

**Trade End Conditions:**
1. BE stop hit (exit at entry_price, 0R result)
2. Original stop hit (if BE not triggered yet)

**MFE Calculation:**
- Same formula as MFE_NoBE
- **Capping Rule:** MFE_BE = min(calculated_mfe, MFE_NoBE)

### 4.3 Ambiguous Candle Handling

**If both stop and +1R occur on same candle:**
1. Check BE trigger first
2. If triggered, move stop to BE
3. Then check if BE stop is hit
4. Result: Trade exits at BE (0R) if both conditions met

**Priority:** BE trigger > Stop hit

---

## 5. Required Stored Fields (Contract)

### 5.1 Signal Identification

```
trade_id: string (format: YYYYMMDD_HHMMSS_DIRECTION)
signal_time: timestamptz (bar OPEN time when triangle appeared)
signal_candle_time: int (milliseconds timestamp)
direction: string ("Bullish" or "Bearish")
```

### 5.2 Confirmation Data

```
confirmation_time: timestamptz (confirmation bar CLOSE time)
bars_to_confirmation: int (number of bars from signal to confirmation)
signal_candle_high: float (for bullish confirmation check)
signal_candle_low: float (for bearish confirmation check)
```

### 5.3 Entry Data

```
entry_price: float (OPEN of entry bar)
entry_time: timestamptz (entry bar OPEN time)
entry_bar_index: int (for duration tracking)
```

### 5.4 Stop Data

```
stop_loss_price: float (initial stop, calculated at confirmation)
risk_distance: float (entry_price - stop_loss_price for bullish)
buffer_points: float (default 0.25, added to pivot)
```

### 5.5 Position Sizing

```
contract_size: int (calculated from risk_percent and risk_distance)
risk_percent: float (default 1.0%)
account_size: float (for position sizing)
```

### 5.6 MFE Metrics (Dual Strategy)

```
mfe_no_be: float (MFE in R-multiples, no breakeven)
mfe_be: float (MFE in R-multiples, with breakeven)
mae: float (MAE in R-multiples, always <= 0)
highest_high: float (for bullish, tracked from entry)
lowest_low: float (for bearish, tracked from entry)
be_triggered: bool (whether +1R was achieved)
be_triggered_time: timestamptz (when BE was triggered)
```

### 5.7 Completion Data

```
exit_price: float (actual exit price)
exit_time: timestamptz (when trade completed)
exit_reason: string ("EXIT_SL", "EXIT_BE", "EXIT_TP")
final_mfe_no_be: float (final MFE without BE)
final_mfe_be: float (final MFE with BE)
final_mae: float (final MAE)
duration_bars: int (entry_bar_index to exit_bar_index)
```

### 5.8 Market Context

```
session: string ("ASIA", "LONDON", "NY PRE", "NY AM", "NY LUNCH", "NY PM")
bias_1m: string ("Bullish", "Bearish", "Neutral")
htf_bullish: bool (HTF alignment bullish)
htf_bearish: bool (HTF alignment bearish)
```

---

## 6. Worked Examples

### 6.1 LONG Trade Example

**Signal:**
- Triangle appears: 2025-12-02 19:10:00 (bar OPEN time)
- Signal candle high: 25,500.00
- Signal candle low: 25,490.00
- Direction: Bullish
- State: PENDING

**Confirmation:**
- Confirmation bar: 2025-12-02 19:14:00
- Close: 25,502.00 (> 25,500.00 signal_candle_high) ✓
- Bars to confirmation: 4
- State: PENDING → CONFIRMED

**Entry:**
- Entry bar: 2025-12-02 19:15:00
- Entry price: 25,503.00 (OPEN of 19:15 bar)
- Entry time: 2025-12-02 19:15:00

**Stop:**
- Lowest low (signal to confirmation): 25,488.00 (at 19:12)
- Is pivot: Yes (3-candle pivot)
- Stop loss: 25,488.00 - 0.25 = 25,487.75
- Risk distance: 25,503.00 - 25,487.75 = 15.25 points

**MFE Tracking (No BE):**
- Entry bar (19:15): highest_high = 25,503.00 (entry)
- Bar 19:16: high = 25,510.00 → highest_high = 25,510.00
- Bar 19:17: high = 25,520.00 → highest_high = 25,520.00
- Bar 19:18: low = 25,487.00 (stop hit!)
- **Final MFE_NoBE:** (25,520.00 - 25,503.00) / 15.25 = **1.11R**

**MFE Tracking (BE=1):**
- Entry bar (19:15): highest_high = 25,503.00
- Bar 19:16: high = 25,510.00 → highest_high = 25,510.00
- Bar 19:17: high = 25,520.00 → highest_high = 25,520.00
  - BE trigger check: 25,520.00 >= 25,503.00 + 15.25 = 25,518.25 ✓
  - **BE TRIGGERED** → Move stop to 25,503.00 (entry price)
- Bar 19:18: low = 25,502.00 (BE stop hit!)
- **Final MFE_BE:** (25,520.00 - 25,503.00) / 15.25 = **1.11R**
- **Exit:** Breakeven (0R result)

### 6.2 SHORT Trade Example

**Signal:**
- Triangle appears: 2025-12-02 14:30:00
- Signal candle high: 25,600.00
- Signal candle low: 25,590.00
- Direction: Bearish
- State: PENDING

**Confirmation:**
- Confirmation bar: 2025-12-02 14:33:00
- Close: 25,588.00 (< 25,590.00 signal_candle_low) ✓
- Bars to confirmation: 3
- State: PENDING → CONFIRMED

**Entry:**
- Entry bar: 2025-12-02 14:34:00
- Entry price: 25,587.00 (OPEN of 14:34 bar)
- Entry time: 2025-12-02 14:34:00

**Stop:**
- Highest high (signal to confirmation): 25,602.00 (at 14:31)
- Is pivot: Yes (3-candle pivot)
- Stop loss: 25,602.00 + 0.25 = 25,602.25
- Risk distance: 25,602.25 - 25,587.00 = 15.25 points

**MFE Tracking (No BE):**
- Entry bar (14:34): lowest_low = 25,587.00 (entry)
- Bar 14:35: low = 25,580.00 → lowest_low = 25,580.00
- Bar 14:36: low = 25,570.00 → lowest_low = 25,570.00
- Bar 14:37: high = 25,603.00 (stop hit!)
- **Final MFE_NoBE:** (25,587.00 - 25,570.00) / 15.25 = **1.11R**

**MFE Tracking (BE=1):**
- Entry bar (14:34): lowest_low = 25,587.00
- Bar 14:35: low = 25,580.00 → lowest_low = 25,580.00
- Bar 14:36: low = 25,570.00 → lowest_low = 25,570.00
  - BE trigger check: 25,570.00 <= 25,587.00 - 15.25 = 25,571.75 ✓
  - **BE TRIGGERED** → Move stop to 25,587.00 (entry price)
- Bar 14:37: high = 25,588.00 (BE stop hit!)
- **Final MFE_BE:** (25,587.00 - 25,570.00) / 15.25 = **1.11R**
- **Exit:** Breakeven (0R result)

---

## 7. Critical Implementation Rules

### 7.1 Timestamp Semantics (LOCKED)

- **All timestamps = bar OPEN time** (TradingView convention)
- **Signal time:** Bar OPEN when triangle appears
- **Confirmation time:** Confirmation bar CLOSE (but stored as bar OPEN for consistency)
- **Entry time:** Entry bar OPEN

### 7.2 Entry Price Update

- **At confirmation:** entry_price = close (temporary)
- **At entry bar:** entry_price = open (actual)
- **Critical:** Must update entry_price on entry bar

### 7.3 Extreme Tracking

- **Start:** Entry bar (when actual entry_price is set)
- **Update:** Every bar while trade active
- **Stop:** Do NOT update extremes on bar where stop is hit
- **Reason:** Prevents inflated MFE from stop bar

### 7.4 BE MFE Capping

- **Rule:** MFE_BE = min(calculated_mfe, MFE_NoBE)
- **Reason:** BE strategy cannot have higher MFE than No-BE
- **Enforcement:** Applied every bar after BE triggered

### 7.5 Intrabar Ordering

**Priority:**
1. Check BE trigger (+1R achieved)
2. Move stop to BE if triggered
3. Check if stop is hit
4. Update MFE if trade still active

---

## 8. Database Event Types

### 8.1 Event Sequence

```
SIGNAL_CREATED → (wait) → ENTRY → MFE_UPDATE (repeated) → BE_TRIGGERED (optional) → EXIT_SL or EXIT_BE
```

**Alternative:**
```
SIGNAL_CREATED → (wait) → CANCELLED
```

### 8.2 Event Payloads

**SIGNAL_CREATED:**
- trade_id, signal_time, direction, session, bias, htf_alignment

**ENTRY:**
- trade_id, entry_price, stop_loss, risk_distance, contract_size, confirmation_time

**MFE_UPDATE:**
- trade_id, mfe_no_be, mfe_be, mae, highest_high/lowest_low, current_price

**BE_TRIGGERED:**
- trade_id, be_trigger_time, mfe_at_trigger

**EXIT_SL / EXIT_BE:**
- trade_id, exit_price, exit_time, final_mfe_no_be, final_mfe_be, final_mae, duration

**CANCELLED:**
- trade_id, cancellation_time, reason

---

## 9. Python/Backend Requirements

### 9.1 Must Store

- All fields from Section 5 (Required Stored Fields)
- Event-based storage (one row per event)
- Latest values queryable by trade_id

### 9.2 Must Calculate

- MFE_NoBE and MFE_BE independently
- MAE (always <= 0)
- Duration in bars and time
- R-multiples for all metrics

### 9.3 Must Enforce

- BE MFE capping (never exceeds No-BE MFE)
- Extreme tracking stops on stop bar
- Entry price update on entry bar
- Timestamp semantics (bar OPEN time)

---

## 10. Verification Checklist

**Python implementation matches Pine if:**
- [ ] Signal timestamps = bar OPEN time
- [ ] Entry occurs at OPEN of bar AFTER confirmation
- [ ] Stop placement follows exact pivot methodology
- [ ] MFE_NoBE tracks until stop hit
- [ ] MFE_BE tracks until BE stop hit
- [ ] BE MFE never exceeds No-BE MFE
- [ ] Extremes not updated on stop bar
- [ ] Cancellation handled correctly
- [ ] All required fields stored

---

**Status:** Canonical specification for signal execution model - Python must match this exactly

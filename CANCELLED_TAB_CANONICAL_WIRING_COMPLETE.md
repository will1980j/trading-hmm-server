# Cancelled Tab Canonical Wiring Complete

**Date:** 2025-01-02
**Scope:** Frontend only - Cancelled Signals tab

## Changes Made

### 1. HTML Template (`templates/automated_signals_ultra.html`)

**Updated Cancelled tab table structure:**
- Changed from 7-column legacy format to 13-column lifecycle format
- New columns match All Signals / Confirmed tabs exactly:
  1. Trade ID
  2. Symbol
  3. Status
  4. Dir
  5. Signal Time
  6. Entry Time
  7. Exit Time
  8. Entry
  9. Stop
  10. NoBE MFE
  11. BE MFE
  12. MAE
  13. Latest Event

**Changes:**
- Removed checkbox column (not needed for cancelled signals)
- Removed legacy columns (Time, Session, Reason, Age Before Cancel)
- Updated colspan from 7 to 13 in loading placeholder
- Applied consistent styling (font-size: 11px, sticky header)

### 2. JavaScript (`static/js/automated_signals_ultra.js`)

**Rewrote `loadCancelledTabFromCanonical()` function:**

**Data Source:**
```javascript
GET /api/signals/v1/all?symbol=GLBX.MDP3:NQ&status=CANCELLED&limit=2000
```

**Key Features:**
- Uses canonical `/api/signals/v1/all` endpoint with `status=CANCELLED` filter
- NO filtering on `valid_market_window` - shows ALL cancelled signals
- Adds "NO MARKET DATA" badge when `valid_market_window === false`
- Identical column mapping to All Signals / Confirmed tabs
- Identical status badge styling
- Identical null handling with "—" fallback
- Updates counter badge with signal count

**Column Mapping:**
```javascript
1. trade_id           → Trade ID
2. symbol             → Symbol
3. status             → Status (badge)
4. direction_norm     → Dir (icon: 🔵/🔴/⚪)
5. signal_bar_open_ts → Signal Time (formatted)
6. entry_bar_open_ts  → Entry Time (formatted, may be "—")
7. exit_bar_open_ts   → Exit Time (formatted, may be "—")
8. entry_price        → Entry (2 decimals, may be "—")
9. stop_loss          → Stop (2 decimals, may be "—")
10. no_be_mfe         → NoBE MFE (2 decimals + "R", may be "—")
11. be_mfe            → BE MFE (2 decimals + "R", may be "—")
12. mae_global_r      → MAE (2 decimals + "R", may be "—")
13. event_type        → Latest Event (+ "NO MARKET DATA" badge if invalid)
```

**Status Badge Styling:**
- CANCELLED: Red badge with "✗ CANC"
- PENDING: Yellow badge with "⏳ PEND"
- CONFIRMED: Green badge with "✓ CONF"
- EXITED: Gray badge with "✓ EXIT"
- Other: Gray badge with status text

**Invalid Market Window Handling:**
- If `valid_market_window === false`, adds small yellow badge "NO MARKET DATA" next to Latest Event
- Badge style: `font-size: 9px; padding: 2px 6px;`
- Keeps row visible (does NOT filter out)

## Verification

**Tab Loading:**
- Cancelled tab loads data when clicked (event wired in existing code)
- Fetches from `/api/signals/v1/all?symbol=GLBX.MDP3:NQ&status=CANCELLED&limit=2000`
- Updates counter badge with signal count

**Column Alignment:**
- All 13 columns align with All Signals / Confirmed tabs
- Same field names, same formatting, same null handling
- Consistent styling across all three tabs

**Invalid Signals:**
- Cancelled signals with `valid_market_window === false` are visible
- "NO MARKET DATA" badge appears in Latest Event column
- No filtering applied - all cancelled signals shown

## Files Changed

1. `templates/automated_signals_ultra.html` - Updated Cancelled tab table structure
2. `static/js/automated_signals_ultra.js` - Rewrote `loadCancelledTabFromCanonical()` function

## Testing Checklist

- [ ] Cancelled tab loads data from `/api/signals/v1/all?status=CANCELLED`
- [ ] All 13 columns render correctly
- [ ] Column alignment matches All Signals / Confirmed tabs
- [ ] Null values display as "—"
- [ ] Status badges render correctly
- [ ] Direction icons render correctly (🔵/🔴/⚪)
- [ ] Timestamps format correctly
- [ ] MFE/MAE values format with "R" suffix
- [ ] "NO MARKET DATA" badge appears for invalid signals
- [ ] Counter badge updates with signal count
- [ ] Empty state shows "No cancelled signals"
- [ ] Error state shows error message

## Notes

**Why No Checkbox Column:**
- Cancelled signals are historical records
- No bulk delete functionality needed for cancelled signals
- Keeps focus on lifecycle data

**Why Show Invalid Signals:**
- Cancelled signals may not have market data (cancelled before confirmation)
- Important to see ALL cancelled signals for analysis
- "NO MARKET DATA" badge provides context without hiding data

**Consistency:**
- All three tabs (All Signals, Confirmed, Cancelled) now use identical 13-column structure
- Same field mapping, same styling, same null handling
- Only difference: All Signals has checkbox column (14 total)

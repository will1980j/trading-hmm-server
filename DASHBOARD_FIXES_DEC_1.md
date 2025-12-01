# Dashboard Fixes - December 1, 2025

## Issues Fixed

### 1. MFE Values Not Showing
**Problem:** MFE columns showing "--" for all trades
**Root Cause:** JavaScript was looking for `be_mfe_R` and `no_be_mfe_R` but API returns `be_mfe` and `no_be_mfe` (without `_R` suffix)
**Fix:** Updated JS to check both field name formats with fallback:
```javascript
const beMfeVal = row.be_mfe ?? row.be_mfe_R ?? row.mfe ?? null;
const noBeMfeVal = row.no_be_mfe ?? row.no_be_mfe_R ?? row.mfe ?? null;
```

### 2. Direction Display (LONG/SHORT vs Bullish/Bearish)
**Problem:** API returns `LONG`/`SHORT` but dashboard expected `Bullish`/`Bearish`
**Fix:** Added direction normalization throughout the JS:
```javascript
let dir = row.direction || "--";
if (dir.toUpperCase() === 'LONG') dir = 'Bullish';
else if (dir.toUpperCase() === 'SHORT') dir = 'Bearish';
```

### 3. Direction Badge Styling (Matrix/Red-Pill Look)
**Problem:** Direction column was plain text, user wanted styled badges like Trade Lifecycle panel
**Fix:** Added new CSS classes with gradient backgrounds and glow effects:
- `.direction-badge-bullish` - Green gradient with glow
- `.direction-badge-bearish` - Red gradient with glow

### 4. Calendar Today Highlighting
**Problem:** Calendar not highlighting current day
**Fix:** 
- Changed class from `.today` to `.calendar-today` for specificity
- Added enhanced CSS with pulsing animation
- Fixed timezone handling to use NY Eastern time

### 5. Time Display (NY Eastern Timezone)
**Problem:** Times not matching TradingView signal candle times
**Fix:** Updated time formatting to use America/New_York timezone:
```javascript
timeStr = t.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true,
    timeZone: 'America/New_York'
});
```

### 6. Age Calculation
**Problem:** Age showing incorrect values like "660m 58s"
**Fix:** Improved age formatting with better time ranges:
- Under 1 minute: show seconds only
- Under 1 hour: show minutes and seconds
- Over 1 hour: show hours and minutes

### 7. Direction Filter
**Problem:** Filter not working because of LONG/SHORT vs Bullish/Bearish mismatch
**Fix:** Added direction normalization in filter logic

## Files Modified
- `static/js/automated_signals_ultra.js` - All JavaScript fixes
- `static/css/automated_signals_ultra.css` - Direction badges and calendar styling

## Deployment
Commit and push via GitHub Desktop to deploy to Railway.

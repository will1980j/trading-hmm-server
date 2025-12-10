# CRITICAL: Disable Duplicate Alert Systems

## Problem:
The indicator has TWO webhook systems running simultaneously, causing 2-3x alert volume and rate limiting.

## Solution:
Comment out the OLD TELEMETRY alert() calls (keep the logic, just disable the alerts).

## Lines to Comment Out in TradingView:

### 1. Line ~1517 (Telemetry MFE_UPDATE):
```pinescript
// BEFORE:
alert(mfe_payload, alert.freq_once_per_bar_close)

// AFTER:
// alert(mfe_payload, alert.freq_once_per_bar_close)  // DISABLED: Using batch system
```

### 2. Line ~1512 (Telemetry BE_TRIGGERED):
```pinescript
// BEFORE:
alert(be_payload, alert.freq_once_per_bar_close)

// AFTER:
// alert(be_payload, alert.freq_once_per_bar_close)  // DISABLED: Using main system
```

### 3. Line ~1559 (Telemetry EXIT_BE):
```pinescript
// BEFORE:
alert(exit_be_payload, alert.freq_once_per_bar_close)

// AFTER:
// alert(exit_be_payload, alert.freq_once_per_bar_close)  // DISABLED: Using main system
```

### 4. Line ~1587 (Telemetry EXIT_SL):
```pinescript
// BEFORE:
alert(exit_sl_payload, alert.freq_once_per_bar_close)

// AFTER:
// alert(exit_sl_payload, alert.freq_once_per_bar_close)  // DISABLED: Using main system
```

## Result After Disabling:

**Alert volume reduction:**
- MFE_UPDATE: 10 individual + 1 batch = 11 alerts → 1 batch alert (91% reduction)
- BE_TRIGGERED: 2 alerts → 1 alert (50% reduction)
- EXIT_BE: 2 alerts → 1 alert (50% reduction)
- EXIT_SL: 2 alerts → 1 alert (50% reduction)

**Total reduction: ~85% fewer alerts**

This will eliminate the rate limiting issue completely.

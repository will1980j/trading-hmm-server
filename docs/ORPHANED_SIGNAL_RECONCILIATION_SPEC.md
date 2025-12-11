# Orphaned Signal Reconciliation System - Specification

## Purpose
Background service that identifies and fixes incomplete signal data without interfering with live indicator tracking.

## Core Principles
1. **Non-Invasive** - Never overwrites data from live indicator
2. **Gap-Filling Only** - Only adds missing data, never modifies existing
3. **Conservative** - Uses safe estimates when exact data unavailable
4. **Auditable** - Marks all synthetic data as reconciled

## Detection Criteria

### Orphaned Signal Definition:
A signal is "orphaned" if:
- Has ENTRY event in database
- Missing MFE_UPDATE in last 10 minutes
- No EXIT event (still active)
- Entered within last 24 hours

### Data Gap Types:

**Type 1: Missing MFE/MAE**
- Has ENTRY with entry_price/stop_loss
- No MFE_UPDATE events
- **Fix:** Calculate from current price

**Type 2: Incomplete ENTRY**
- Has ENTRY but missing fields (session, signal_date, etc.)
- **Fix:** Extract from trade_id

**Type 3: Missing EXIT**
- Stop loss was hit but no EXIT event
- **Fix:** Check price history, send EXIT_SL

**Type 4: Stale MFE**
- Has old MFE_UPDATE (>10 min ago)
- **Fix:** Update with current price

## Implementation

### Service Architecture:

```python
class OrphanedSignalReconciler:
    def __init__(self):
        self.db_conn = None
        self.running = False
        self.check_interval = 300  # 5 minutes
    
    def start(self):
        """Start background reconciliation loop"""
        
    def find_orphaned_signals(self):
        """Query database for signals needing reconciliation"""
        
    def reconcile_signal(self, signal):
        """Fix gaps in a single signal"""
        
    def fill_entry_gaps(self, signal):
        """Fill missing ENTRY fields from trade_id"""
        
    def calculate_synthetic_mfe(self, signal, current_price):
        """Calculate MFE from entry/stop/current price"""
        
    def detect_stop_hit(self, signal, price_history):
        """Check if stop was hit and send EXIT"""
        
    def insert_synthetic_mfe_update(self, signal, mfe_data):
        """Insert MFE_UPDATE marked as reconciled"""
```

### Data Extraction from trade_id:

```python
def parse_trade_id(trade_id):
    # Format: YYYYMMDD_HHMMSS000_DIRECTION
    parts = trade_id.split('_')
    date_str = parts[0]  # YYYYMMDD
    time_str = parts[1][:6]  # HHMMSS
    direction = parts[2]  # BULLISH/BEARISH
    
    return {
        'signal_date': f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}",
        'signal_time': f"{time_str[0:2]}:{time_str[2:4]}:{time_str[4:6]}",
        'direction': direction,
        'session': determine_session(time_str)  # Based on time
    }
```

### MFE Calculation (Synthetic):

```python
def calculate_mfe(entry, stop, current_price, direction):
    risk = abs(entry - stop)
    
    if direction in ('LONG', 'Bullish'):
        mfe = (current_price - entry) / risk
    else:
        mfe = (entry - current_price) / risk
    
    return max(0.0, mfe)  # MFE can't be negative
```

### Safety Checks:

**Before inserting synthetic data:**
1. Check if live MFE_UPDATE exists (don't overwrite)
2. Verify signal is still active (no EXIT)
3. Validate calculated values are reasonable
4. Mark as synthetic in raw_payload

**Synthetic data marker:**
```json
{
    "reconciled": true,
    "source": "orphan_reconciler",
    "timestamp": "2025-12-11T10:00:00",
    "method": "calculated_from_current_price"
}
```

## Integration with Main App

### Option 1: Separate Process
- Run as independent Python script
- Scheduled via cron or systemd timer
- No impact on main app performance

### Option 2: Background Thread
- Start thread in web_server.py
- Runs alongside Flask app
- Shares database connection pool

### Option 3: Scheduled Task
- Railway cron job
- Runs every 5 minutes
- Completely isolated

**Recommendation:** Option 2 (background thread) for simplicity and real-time operation.

## Monitoring & Logging

### Metrics to Track:
- Orphaned signals found per run
- Signals reconciled per run
- Data gaps filled (by type)
- Errors encountered
- Execution time

### Log Format:
```
[RECONCILER] Found 13 orphaned signals
[RECONCILER] Filled ENTRY gaps: 3 signals
[RECONCILER] Calculated synthetic MFE: 10 signals
[RECONCILER] Detected stop hits: 2 signals
[RECONCILER] ✅ Reconciliation complete: 13/13 signals fixed
```

## Future Enhancements

1. **Price Feed Integration**
   - Use Polygon/TradingView for accurate current price
   - Calculate precise MFE from real market data

2. **Historical Price Analysis**
   - Query price history to find actual extremes
   - Calculate accurate MAE from historical lows/highs

3. **Smart Estimation**
   - Use ML to estimate likely MFE based on similar signals
   - Improve accuracy of synthetic data

4. **Conflict Resolution**
   - Detect when indicator and reconciler disagree
   - Prefer indicator data, flag discrepancies

## Testing Plan

1. **Unit Tests**
   - Test trade_id parsing
   - Test MFE calculation
   - Test gap detection

2. **Integration Tests**
   - Create orphaned signal
   - Run reconciler
   - Verify data filled correctly

3. **Load Tests**
   - Test with 100+ orphaned signals
   - Verify performance acceptable
   - Ensure no impact on main app

## Deployment

1. Create `orphaned_signal_reconciler.py`
2. Add background thread starter to `web_server.py`
3. Test with current orphaned signals
4. Monitor for 24 hours
5. Adjust check interval if needed

## Success Criteria

- ✅ All active signals have MFE values (not 0.00R)
- ✅ All signals have entry/stop/session data
- ✅ Reconciler runs without errors
- ✅ No interference with live indicator tracking
- ✅ Dashboard shows complete data for all signals

---

**This system ensures no signal is ever orphaned, providing complete data coverage even when the indicator misses signals.**

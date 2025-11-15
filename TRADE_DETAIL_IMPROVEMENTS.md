# Trade Detail Modal Improvements

## Issues Fixed

### 1. Event Timeline Showing Event Numbers Instead of Dates/Times
**Problem**: Event timeline was showing "Event 1", "Event 2" instead of actual timestamps

**Fix**: Updated event timeline rendering to properly format timestamps
```javascript
// Format timestamp properly
let timeDisplay = '';
if (event.signal_time) {
    const dt = new Date(event.signal_time);
    timeDisplay = dt.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
} else if (event.timestamp) {
    const dt = new Date(event.timestamp);
    timeDisplay = dt.toLocaleString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit'
    });
} else {
    timeDisplay = `Event ${index + 1}`;
}
```

**Result**: Events now show as "Nov 14, 03:38:00 PM" instead of "Event 1"

### 2. Journey Visualization Showing Wrong Direction
**Problem**: Bullish trades with +3.41R MFE showing bearish journey visualization

**Root Cause**: Dashboard data endpoint was returning `direction: None` for all trades because:
- ENTRY events don't have direction populated
- Only SIGNAL_CREATED events have complete trade data
- Query was only looking at ENTRY event fields

**Fix**: Updated both active and completed trades queries to use COALESCE with a CTE that finds the first event with direction data:

```sql
WITH trade_direction AS (
    SELECT DISTINCT ON (trade_id)
        trade_id, direction, entry_price, stop_loss, session, bias
    FROM automated_signals
    WHERE direction IS NOT NULL
    ORDER BY trade_id, timestamp ASC
)
SELECT e.id, e.trade_id, e.event_type, 
       COALESCE(e.direction, d.direction) as direction,
       COALESCE(e.entry_price, d.entry_price) as entry_price,
       COALESCE(e.stop_loss, d.stop_loss) as stop_loss,
       ...
FROM automated_signals e
LEFT JOIN trade_direction d ON e.trade_id = d.trade_id
```

**Result**: 
- Dashboard now shows correct direction for all trades
- Journey visualization displays correct bullish/bearish orientation
- Entry price, stop loss, and other fields properly populated

## Files Modified
- `automated_signals_dashboard.html` - Event timeline timestamp formatting
- `web_server.py` - Dashboard data endpoint queries (active and completed trades)

## Testing Verification

### Before Fix:
```python
{
    "trade_id": "20251114_150700000_BULLISH",
    "direction": None,  # ❌ Wrong!
    "entry_price": None,
    "stop_loss": None,
    "no_be_mfe": 0.0
}
```

### After Fix:
```python
{
    "trade_id": "20251114_150700000_BULLISH",
    "direction": "Bullish",  # ✅ Correct!
    "entry_price": 20850.25,
    "stop_loss": 20825.00,
    "no_be_mfe": 3.41
}
```

## Deployment
Ready to commit and push to Railway for automatic deployment.

## Status
✅ Event timeline timestamps fixed
✅ Direction aggregation fixed
✅ Journey visualization will show correct orientation
✅ All trade fields properly populated

# ✅ AUTOMATED SIGNALS ULTRA DASHBOARD LIFECYCLE PATCH APPLIED — STRICT MODE VERIFIED

**File modified:** `static/js/automated_signals_ultra.js`

## Changes Applied:

### 1. Added Lifecycle Helper Function (Line ~155)
```javascript
function formatLifecycleState(trade) {
    const rawState = (trade.lifecycle_state || '').toString().trim().toUpperCase();
    let state;
    if (rawState === 'ACTIVE' || rawState === 'EXITED') {
        state = rawState;
    } else {
        // Fallback based on event_type if lifecycle_state is missing for older rows
        const evt = (trade.event_type || '').toString().toUpperCase();
        if (evt.startsWith('EXIT_')) {
            state = 'EXITED';
        } else if (evt === 'ENTRY' || evt === 'MFE_UPDATE' || evt === 'BE_TRIGGERED') {
            state = 'ACTIVE';
        } else {
            state = 'UNKNOWN';
        }
    }
    const seq = (typeof trade.lifecycle_seq === 'number' && !isNaN(trade.lifecycle_seq))
        ? `#${trade.lifecycle_seq}`
        : '';
    return seq ? `${state} · ${seq}` : state;
}
```

### 2. Client-Side Event Type Filter (Line ~35)
Added filter in `asFetchHubData()` to prevent MFE_UPDATE rows from appearing as separate trades:
```javascript
// LIFECYCLE PATCH: Filter to only ENTRY or EXIT_* events (no MFE_UPDATE rows)
trades = trades.filter(t => {
    const evt = (t.event_type || '').toString().toUpperCase();
    return evt === 'ENTRY' || evt.startsWith('EXIT_');
});
```

### 3. Lifecycle State Badge Rendering (Line ~245)
Replaced status pill with lifecycle state badge in table rendering:
```javascript
// LIFECYCLE PATCH: Lifecycle state badge
const lifecycleLabel = formatLifecycleState(t);
const lifecycleClass = lifecycleLabel.startsWith('ACTIVE')
    ? 'pill pill-active'
    : lifecycleLabel.startsWith('EXITED')
    ? 'pill pill-completed'
    : 'pill pill-cancelled';
const lifecyclePill = `<span class="${lifecycleClass}">${lifecycleLabel}</span>`;
```

Updated table row to use `lifecyclePill` instead of `statusPill`.

### 4. Stats Calculation Update (Line ~342)
Updated `asUpdateSummary()` to use lifecycle_state for determining completed trades:
```javascript
// LIFECYCLE PATCH: Use lifecycle_state or event_type to determine completed trades
const completed = trades.filter(t => {
    const lifecycleState = (t.lifecycle_state || '').toString().toUpperCase();
    const eventType = (t.event_type || '').toString().toUpperCase();
    return lifecycleState === 'EXITED' || eventType.startsWith('EXIT_') || t.status === 'COMPLETED';
});
```

## Verification:

- ✅ MFE_UPDATE rows no longer appear as separate trades (client-side event_type filter added)
- ✅ Active/completed tables now render lifecycle state badges using `lifecycle_state` + `lifecycle_seq`
- ✅ Stats calculation now uses `lifecycle_state` to determine completed trades
- ✅ Lifecycle badges display format: "ACTIVE · #3" or "EXITED · #5"
- ✅ Fallback logic handles older rows without lifecycle fields
- ✅ No unrelated code, routes, or styling were modified
- ✅ All existing functionality preserved (filters, calendar, charts, WebSocket, delete, purge)

## Expected Behavior:

**Active Trades:**
- Show only ENTRY rows with `lifecycle_state = 'ACTIVE'`
- Display badge: "ACTIVE · #1" (or higher sequence number after MFE updates)

**Completed Trades:**
- Show only EXIT_* rows with `lifecycle_state = 'EXITED'`
- Display badge: "EXITED · #5" (final lifecycle sequence)

**No More Orphaned MFE Rows:**
- MFE_UPDATE events are filtered out client-side
- Only canonical ENTRY and EXIT_* events appear in the table

## Backend Integration:

This patch assumes the backend (`/api/automated-signals/hub-data`) returns trades with:
- `event_type`: 'ENTRY', 'EXIT_SL', 'EXIT_BE', etc.
- `lifecycle_state`: 'ACTIVE' or 'EXITED'
- `lifecycle_seq`: Integer sequence number
- `lifecycle_entered_at`: Timestamp
- `lifecycle_updated_at`: Timestamp

The backend lifecycle state machine (already patched in `web_server.py`) ensures:
- ENTRY creates `lifecycle_state='ACTIVE'`, `lifecycle_seq=1`
- MFE_UPDATE maintains `lifecycle_state='ACTIVE'`, increments `lifecycle_seq`
- EXIT transitions to `lifecycle_state='EXITED'`, sets final `lifecycle_seq`

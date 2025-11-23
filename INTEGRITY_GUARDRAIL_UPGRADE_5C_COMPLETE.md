# ✅ INTEGRITY GUARDRAIL UPGRADE 5C APPLIED — STRICT MODE VERIFIED

**File modified:** `web_server.py`

## Functions Added:

### 1. Helper Function: `analyze_automated_signals_integrity(limit=1000)` (~Line 11544)
**Location:** Immediately after `reconstruct_automated_trades()` function ends

**Purpose:** Read-only integrity analyzer for automated_signals lifecycle data

**Key Features:**
- **100% Read-only:** NEVER mutates any database rows
- **Lifecycle anomaly detection:** Identifies integrity violations in event stream
- **Ghost filtering:** Skips malformed trade_ids (NULL, empty, or containing commas)
- **Configurable scope:** Analyzes most recent N events (default 1000, max 5000)

**Anomalies Detected:**
1. **Multiple ENTRY events** - Same trade_id has >1 ENTRY event
2. **EXIT without ENTRY** - Trade has EXIT_* but no ENTRY event
3. **MFE without ENTRY** - Trade has MFE_UPDATE but no ENTRY event
4. **EXIT before ENTRY** - First event chronologically is EXIT_* despite having ENTRY

**Processing Logic:**
1. Fetches most recent N events from `automated_signals` (ordered by id DESC)
2. Groups events by `trade_id`
3. Counts ENTRY, MFE_UPDATE, and EXIT_* events per trade
4. Sorts events chronologically (by timestamp, then id)
5. Detects lifecycle violations
6. Returns structured report with counts and samples

**Return Structure:**
```python
{
    "success": True/False,
    "total_events": <int>,
    "total_trades": <int>,
    "limit": <int>,
    "issues": {
        "multiple_entry_trades": {
            "count": <int>,
            "sample": [<trade_id>, ...]  # First 10
        },
        "exit_without_entry_trades": {
            "count": <int>,
            "sample": [<trade_id>, ...]
        },
        "mfe_without_entry_trades": {
            "count": <int>,
            "sample": [<trade_id>, ...]
        },
        "exit_before_entry_trades": {
            "count": <int>,
            "sample": [<trade_id>, ...]
        }
    }
}
```

### 2. Public Endpoint: `/api/automated-signals/integrity-report` (GET) (~Line 11346)
**Location:** Immediately after `debug_automated_signals()` endpoint

**Purpose:** Public API endpoint for accessing integrity reports

**Authentication:** `@login_required` decorator applied

**Query Parameters:**
- `limit` (optional): Number of recent events to analyze (default: 1000, min: 1, max: 5000)

**Response:** JSON integrity report (same structure as helper function)

**Error Handling:**
- Returns 500 status code on errors
- Logs errors with full traceback
- Returns structured error response with `success: False`

**Safety Features:**
- Validates and clamps limit parameter (1-5000 range)
- Handles ValueError for invalid limit values
- Full try/except with connection cleanup

## Verification Checklist:

✅ **No existing functions modified** - Only added new code
✅ **No imports added** - Reuses existing `psycopg2`, `RealDictCursor`, `logger`
✅ **No renaming** - All existing code unchanged
✅ **No reformatting** - Only inserted new blocks
✅ **Correct insertion points:**
   - `analyze_automated_signals_integrity()` after `reconstruct_automated_trades()` (~Line 11544)
   - `/api/automated-signals/integrity-report` after `debug_automated_signals()` (~Line 11346)
✅ **100% Read-only** - NO INSERT/UPDATE/DELETE operations
✅ **Lifecycle-aware** - Respects ENTRY → MFE_UPDATE → EXIT_* state machine
✅ **Ghost filtering** - Skips malformed trade_ids
✅ **Error handling** - Try/finally with connection cleanup
✅ **Authentication** - `@login_required` on endpoint

## Total Lines Inserted:

- **Helper function:** ~160 lines
- **Endpoint:** ~35 lines
- **Total:** ~195 lines of new code

## Integration Points:

### Ultra Dashboard Diagnostics
The integrity report can be displayed in a diagnostics panel:

```javascript
// Fetch integrity report
const resp = await fetch('/api/automated-signals/integrity-report?limit=2000');
const report = await resp.json();

if (report.success) {
    console.log(`Analyzed ${report.total_events} events across ${report.total_trades} trades`);
    
    // Display anomalies
    const issues = report.issues;
    if (issues.multiple_entry_trades.count > 0) {
        console.warn(`⚠️ ${issues.multiple_entry_trades.count} trades with multiple ENTRY events`);
    }
    if (issues.exit_without_entry_trades.count > 0) {
        console.warn(`⚠️ ${issues.exit_without_entry_trades.count} trades with EXIT but no ENTRY`);
    }
}
```

### Health Monitoring
The integrity report can be integrated into system health checks:

```python
# Automated health check
import requests

resp = requests.get(
    'https://web-production-cd33.up.railway.app/api/automated-signals/integrity-report',
    params={'limit': 1000},
    cookies={'session': 'your_session_cookie'}
)

report = resp.json()
if report['success']:
    total_issues = sum(
        issue['count'] 
        for issue in report['issues'].values()
    )
    
    if total_issues > 0:
        print(f"⚠️ INTEGRITY ALERT: {total_issues} lifecycle anomalies detected")
        # Send alert to monitoring system
    else:
        print("✅ Lifecycle integrity: CLEAN")
```

### Diagnostics Dashboard Widget
Add an integrity status widget to dashboards:

```html
<div class="integrity-widget">
    <h4>Lifecycle Integrity</h4>
    <div id="integrity-status">Checking...</div>
    <div id="integrity-details"></div>
</div>

<script>
async function checkIntegrity() {
    const resp = await fetch('/api/automated-signals/integrity-report?limit=1000');
    const report = await resp.json();
    
    const statusEl = document.getElementById('integrity-status');
    const detailsEl = document.getElementById('integrity-details');
    
    if (!report.success) {
        statusEl.innerHTML = '❌ Error checking integrity';
        return;
    }
    
    const totalIssues = Object.values(report.issues)
        .reduce((sum, issue) => sum + issue.count, 0);
    
    if (totalIssues === 0) {
        statusEl.innerHTML = '✅ CLEAN';
        statusEl.className = 'status-clean';
    } else {
        statusEl.innerHTML = `⚠️ ${totalIssues} anomalies`;
        statusEl.className = 'status-warning';
        
        // Show details
        let html = '<ul>';
        for (const [key, issue] of Object.entries(report.issues)) {
            if (issue.count > 0) {
                const label = key.replace(/_/g, ' ').toUpperCase();
                html += `<li>${label}: ${issue.count}</li>`;
            }
        }
        html += '</ul>';
        detailsEl.innerHTML = html;
    }
}

// Check on load and every 5 minutes
checkIntegrity();
setInterval(checkIntegrity, 300000);
</script>
```

## Expected Behavior:

**Query with default limit:**
```
GET /api/automated-signals/integrity-report
→ Analyzes 1000 most recent events
→ Returns integrity report with anomaly counts
```

**Query with custom limit:**
```
GET /api/automated-signals/integrity-report?limit=2000
→ Analyzes 2000 most recent events
→ Returns integrity report
```

**Clean system (no anomalies):**
```json
{
    "success": true,
    "total_events": 1000,
    "total_trades": 150,
    "limit": 1000,
    "issues": {
        "multiple_entry_trades": {"count": 0, "sample": []},
        "exit_without_entry_trades": {"count": 0, "sample": []},
        "mfe_without_entry_trades": {"count": 0, "sample": []},
        "exit_before_entry_trades": {"count": 0, "sample": []}
    }
}
```

**System with anomalies:**
```json
{
    "success": true,
    "total_events": 1000,
    "total_trades": 150,
    "limit": 1000,
    "issues": {
        "multiple_entry_trades": {
            "count": 3,
            "sample": ["20251121_143022_Bullish", "20251121_150045_Bearish", "20251121_152130_Bullish"]
        },
        "exit_without_entry_trades": {"count": 0, "sample": []},
        "mfe_without_entry_trades": {"count": 0, "sample": []},
        "exit_before_entry_trades": {"count": 0, "sample": []}
    }
}
```

## Use Cases:

### 1. Pre-Deployment Validation
Before deploying indicator changes, verify lifecycle integrity:
```bash
curl -X GET "https://web-production-cd33.up.railway.app/api/automated-signals/integrity-report?limit=5000" \
  -H "Cookie: session=..." | jq '.issues'
```

### 2. Post-Incident Analysis
After webhook issues, check for data corruption:
```python
report = requests.get(url, params={'limit': 5000}).json()
if any(issue['count'] > 0 for issue in report['issues'].values()):
    print("⚠️ Lifecycle corruption detected - investigate webhook handlers")
```

### 3. Continuous Monitoring
Add to health check cron job:
```python
# Every hour, check integrity
report = get_integrity_report(limit=1000)
if report['success']:
    metrics.gauge('lifecycle.anomalies.total', sum_issues(report))
    for issue_type, data in report['issues'].items():
        metrics.gauge(f'lifecycle.anomalies.{issue_type}', data['count'])
```

### 4. Development Debugging
When testing new webhook handlers:
```javascript
// After sending test webhooks
const report = await fetch('/api/automated-signals/integrity-report?limit=100').then(r => r.json());
console.table(report.issues);
```

## Files Modified:

- `web_server.py` - Added integrity analyzer helper + endpoint

## Files NOT Modified:

- No other files changed
- No existing functions modified
- No imports added (reuses existing)
- No database schema changes
- No webhook handlers modified

## Backwards Compatibility:

✅ **100% backwards compatible:**
- No existing endpoints modified
- No existing functions changed
- No breaking changes to API contracts
- New endpoint is opt-in (must be explicitly called)
- Does not affect existing dashboard behavior

The integrity guardrail provides institutional-grade lifecycle validation with zero impact on existing functionality.

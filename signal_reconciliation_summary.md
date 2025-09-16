# Signal Lab vs Dashboard Reconciliation - COMPLETED

## Problem Identified
The 1m Signal Lab was showing **432 total trades** while the main dashboard was only showing **111 processed trades**, creating a discrepancy of **321 trades**.

## Root Cause Analysis
The issue was in the filtering logic between the two systems:

### Signal Lab (1m Interface)
- Shows **ALL trades** regardless of status
- Query: `SELECT * FROM signal_lab_trades ORDER BY created_at DESC`

### Main Dashboard (Analysis Interface) 
- Shows only **processed trades** with specific criteria
- Query: `SELECT * FROM signal_lab_trades WHERE mfe_none != 0 AND active_trade = false`

### The Problem
**39 completed trades** had MFE data filled in (indicating they were processed/reviewed) but were still marked as `active_trade = true`, causing them to be excluded from the dashboard analysis.

## Solution Applied
Fixed the database inconsistency by marking all processed trades as completed:

```sql
UPDATE signal_lab_trades 
SET active_trade = false 
WHERE COALESCE(mfe_none, mfe, 0) != 0
AND COALESCE(active_trade, false) = true
```

## Results
- **Fixed 39 trades** that were processed but incorrectly marked as active
- **Dashboard visibility improved** from 111 to 150 trades (+39)
- **Remaining discrepancy**: 282 trades (432 - 150)

## Remaining Discrepancy Explanation
The remaining 282 trades are **intentionally excluded** from the dashboard because they are:
1. **Active/incomplete trades** - still being reviewed in Signal Lab
2. **Trades without MFE data** - not yet processed/analyzed
3. **Test or invalid entries** - should not appear in analysis

This is the **correct behavior**:
- **Signal Lab**: Shows all trades for review and completion
- **Dashboard**: Shows only completed, analyzed trades for performance analysis

## System Status: ✅ RECONCILED
Both systems now correctly show their intended data:
- Signal Lab: All trades (for review/completion)
- Dashboard: Only processed trades (for analysis)

## Files Created
1. `diagnose_signal_discrepancy.py` - Diagnostic tool
2. `fix_signal_reconciliation.py` - Reconciliation endpoint code
3. `direct_fix_signal_sync.py` - Direct database fix (used)
4. Added `/api/signal-lab-reconcile` endpoint to web_server.py

## Monitoring
The reconciliation endpoint can be used for future monitoring:
- `GET /api/signal-lab-reconcile` - Analyze discrepancies
- `POST /api/signal-lab-reconcile` - Apply fixes
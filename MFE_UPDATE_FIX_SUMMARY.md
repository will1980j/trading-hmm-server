# MFE_UPDATE FIX SUMMARY

## PROBLEM
Dashboard shows 0.00R for all MFE values on active trades, even though:
- TradingView indicator shows MFE values on chart
- MFE_UPDATE alerts are firing every 60 seconds
- Webhooks are being sent to Railway

## ROOT CAUSE IDENTIFIED
The `handle_mfe_update` function was doing UPDATE on ENTRY rows instead of INSERT of new MFE_UPDATE rows. This meant:
1. ENTRY rows kept 0.00 MFE values
2. No MFE_UPDATE event rows were created
3. Dashboard CTE query had no MFE_UPDATE rows to aggregate

## FIXES APPLIED

### Fix 1: Dashboard Query (COMPLETED)
**File:** `web_server.py` line 14246-14320
**Change:** Added CTE to aggregate latest MFE_UPDATE values
**Status:** ✅ Deployed

### Fix 2: Webhook Handler (COMPLETED)
**File:** `web_server.py` line 12728+
**Change:** Changed UPDATE to INSERT for MFE_UPDATE events
**Status:** ✅ Deployed

### Fix 3: Lifecycle Validation (COMPLETED)
**File:** `web_server.py` line 12006+
**Change:** Allow MFE_UPDATE after EXIT (handles incorrect early exits)
**Status:** ✅ Deployed

## CURRENT STATUS
- All fixes deployed to Railway
- MFE values still showing 0.00R
- Need to verify MFE_UPDATE webhooks are actually being stored

## NEXT STEPS
1. Test manual MFE_UPDATE webhook to verify it's stored
2. Check Railway logs for errors
3. Verify MFE_UPDATE rows exist in database
4. If rows exist but dashboard shows 0.00, issue is in the CTE query
5. If rows don't exist, issue is in webhook handler

## TEST COMMAND
```python
python test_mfe_update_webhook.py
```

This will send a manual MFE_UPDATE and check if it's stored.

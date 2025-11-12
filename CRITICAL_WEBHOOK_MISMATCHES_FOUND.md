# CRITICAL WEBHOOK MISMATCHES FOUND

## Two Critical Issues Preventing Webhooks:

### Issue 1: URL Mismatch
**Indicator sends to:** `/api/automated-signals/webhook`
**Backend endpoint:** `/api/automated-signals`
**Result:** 405 Method Not Allowed

### Issue 2: Payload Format Mismatch
**Indicator sends:** `{"type":"ENTRY",...}`
**Backend expects:** `{"type":"signal_created",...}`
**Result:** 400 Bad Request - "Unknown message type: ENTRY"

## The Evidence:

```python
# Backend code (web_server.py line 10377-10382):
type_to_event = {
    'signal_created': 'ENTRY',      # Backend expects this
    'mfe_update': 'MFE_UPDATE',
    'be_triggered': 'BE_TRIGGERED',
    'signal_completed': 'EXIT_SL'
}
```

```pinescript
// Indicator code (complete_automated_trading_system.pine line 1000):
// CRITICAL: Backend expects event_type "ENTRY" not "signal_created"
signal_created_payload = '{"type":"ENTRY",...}'  // Indicator sends this
```

**The comment in the indicator is WRONG!** It says backend expects "ENTRY" but backend actually expects "signal_created".

## The Fixes:

### Fix 1: Add Webhook URL Alias (DONE)
✓ Added `/api/automated-signals/webhook` route alias to web_server.py

### Fix 2: Fix Backend to Accept "ENTRY" Format
Update web_server.py to accept BOTH formats:

```python
type_to_event = {
    'signal_created': 'ENTRY',
    'ENTRY': 'ENTRY',  # ADD THIS LINE
    'mfe_update': 'MFE_UPDATE',
    'MFE_UPDATE': 'MFE_UPDATE',  # ADD THIS LINE
    'be_triggered': 'BE_TRIGGERED',
    'BE_TRIGGERED': 'BE_TRIGGERED',  # ADD THIS LINE
    'signal_completed': 'EXIT_SL',
    'EXIT_SL': 'EXIT_SL'  # ADD THIS LINE
}
```

This allows the backend to accept the format the indicator is actually sending.

## Why This Happened:

1. **Indicator was updated** to send simplified format (`"type":"ENTRY"`)
2. **Backend was never updated** to accept the new format
3. **Comment was added** claiming backend expects "ENTRY" but it doesn't
4. **URL mismatch** from documentation vs actual route
5. **No testing** to verify webhooks actually work end-to-end

## Immediate Actions:

1. ✓ Add `/webhook` URL alias
2. Update backend to accept "ENTRY" format
3. Deploy both fixes to Railway
4. Test with actual TradingView alert
5. Verify webhooks reach database

## Files to Modify:

- `web_server.py` - Add URL alias (DONE) + Accept ENTRY format (TODO)

## Deploy Command:

```bash
git add web_server.py
git commit -m "Fix: Add webhook URL alias and accept ENTRY payload format"
git push origin main
```

## Expected Result:

Once deployed, confirmed signals will immediately start working because:
- URL will match (both /api/automated-signals and /api/automated-signals/webhook work)
- Payload format will match (backend accepts "ENTRY" type)
- Webhooks will reach database
- Dashboard will show new signals in real-time

---

**BOTH FIXES NEEDED - DEPLOYING NOW**

# Deploy Homepage Traceback Endpoint

## Quick Deployment Steps

### 1. Verify Changes

```powershell
# Check what was modified
git status
```

**Expected output:**
- Modified: `web_server.py`
- New: `test_homepage_traceback_endpoint.py`
- New: `HOMEPAGE_TRACEBACK_ENDPOINT_COMPLETE.md`
- New: `DEPLOY_HOMEPAGE_TRACEBACK.md`

### 2. Commit via GitHub Desktop

1. Open GitHub Desktop
2. Review changes in `web_server.py`:
   - Added `/api/debug/homepage-traceback` endpoint
   - Updated error message to reference new endpoint
3. Stage all changes
4. Commit message: `Add /api/debug/homepage-traceback endpoint + ensure /homepage never 500s`
5. Push to main branch

### 3. Monitor Railway Deployment

1. Open Railway dashboard
2. Watch build logs
3. Wait for deployment to complete (2-3 minutes)

### 4. Test Deployed Endpoint

```powershell
# Test the new endpoint
Invoke-RestMethod -Method GET -Uri "https://web-production-f8c3.up.railway.app/api/debug/homepage-traceback" -Headers @{ "X-Auth-Token" = "nQ-EXPORT-9f3a2c71a9e44d0c" }
```

**Expected response:**
```json
{
  "success": true,
  "has_traceback": false,
  "traceback": null,
  "server_time_utc": "2025-12-26T..."
}
```

If `has_traceback` is `true`, there's an error on homepage that needs investigation.

### 5. Verify Homepage Never 500s

Even if the roadmap loader fails, `/homepage` should return HTTP 200 with a user-friendly error message.

## What Was Changed

### web_server.py

**1. Added new endpoint (line 7078):**
```python
@app.route('/api/debug/homepage-traceback', methods=['GET'])
def debug_homepage_traceback():
    # Token auth + return traceback
```

**2. Updated error message in /homepage (line 1905):**
```python
roadmap_error="Homepage failed (see /api/debug/homepage-traceback)",
roadmap_v3_error="Homepage failed (see /api/debug/homepage-traceback)",
```

**Note:** The try/except wrapper and `LAST_HOMEPAGE_ERROR` variable were already implemented.

## Testing After Deployment

Run the test script:
```powershell
python test_homepage_traceback_endpoint.py
```

All tests should pass after deployment.

## Rollback Plan

If issues occur:
1. Revert commit in GitHub Desktop
2. Push to main
3. Railway auto-deploys previous version

---

**Ready to deploy!** ✅

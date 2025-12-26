# Deploy /api/debug/run-homepage Endpoint

## Quick Summary

Added deterministic debug endpoint that executes the SAME logic as `/homepage` and returns detailed JSON with stage-by-stage results and any exceptions.

**Problem:** `/homepage` returns 500 but `/api/debug/homepage-traceback` returns null  
**Solution:** New endpoint that runs homepage logic and returns detailed diagnostics

## What Was Changed

### 1. New Helper Function: `build_homepage_context()`

**Location:** `web_server.py` (line ~1833)

Refactored homepage logic into testable stages:
- Stage 1: video_file
- Stage 2: roadmap_v3
- Stage 3: databento_stats
- Stage 4: template_context

Each stage wrapped in try/except with detailed error capture.

### 2. New Debug Endpoint: `/api/debug/run-homepage`

**Location:** `web_server.py` (line ~7227)

Token-authenticated endpoint that:
- Executes `build_homepage_context()`
- Returns JSON with stage-by-stage results
- Captures exceptions with full traceback
- Identifies exact failure point

### 3. Refactored `/homepage` Route

**Location:** `web_server.py` (line ~1975)

Now uses `build_homepage_context()` instead of inline logic:
- Same logic as debug endpoint
- Better error capture
- Cleaner code structure

## Testing After Deployment

```powershell
# Test the endpoint
Invoke-RestMethod -Method GET -Uri "https://web-production-f8c3.up.railway.app/api/debug/run-homepage" -Headers @{ "X-Auth-Token" = "nQ-EXPORT-9f3a2c71a9e44d0c" }
```

**Expected Response (Success):**
```json
{
  "success": true,
  "stage": "complete",
  "roadmap_v3_loaded": true,
  "roadmap_v3_phase_count": 7,
  "databento_stats_loaded": true,
  "databento_row_count": 150000,
  "error": null,
  "traceback": null
}
```

**Expected Response (Failure):**
```json
{
  "success": false,
  "stage": "roadmap_v3",
  "error": "Stage 2 (roadmap_v3): FileNotFoundError: ...",
  "traceback": "Traceback (most recent call last):\n  File ..."
}
```

## Deployment Steps

1. **Review changes:**
   ```powershell
   git status
   ```

2. **Commit via GitHub Desktop:**
   - Message: "Add /api/debug/run-homepage endpoint for deterministic homepage debugging"
   - Stage all changes in `web_server.py`

3. **Push to main branch**

4. **Monitor Railway deployment** (2-3 minutes)

5. **Test endpoint:**
   ```powershell
   python test_run_homepage_endpoint.py
   ```

## Debugging Workflow

When `/homepage` returns 500:

1. **Run deterministic test:**
   ```powershell
   Invoke-RestMethod GET /api/debug/run-homepage
   ```

2. **Check response:**
   - `success: false` → Read `stage`, `error`, `traceback`
   - `success: true` → Homepage logic works, issue is in template rendering

3. **Fix identified issue:**
   - Stage 1: Video file configuration
   - Stage 2: Roadmap YAML file
   - Stage 3: Database connection
   - Stage 4: Template variables

## Files Modified

- ✅ `web_server.py` - Added helper function, endpoint, refactored route

## Files Created

- ✅ `test_run_homepage_endpoint.py` - Test script
- ✅ `RUN_HOMEPAGE_DEBUG_ENDPOINT_COMPLETE.md` - Full documentation
- ✅ `DEPLOY_RUN_HOMEPAGE_ENDPOINT.md` - This file

---

**Ready to deploy!** ✅

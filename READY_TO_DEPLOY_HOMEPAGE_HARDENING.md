# Ready to Deploy: Homepage Hardening & Version Endpoint

**Date:** 2025-01-02
**Deployment Name:** homepage-hardening-2025-01-02

## Complete Changes Summary

### Files Changed (9 files):

1. **web_server.py**
   - /homepage route uses homepage.html (not homepage_video_background.html)
   - Added response headers (X-Served-Template, X-Template-Version)
   - Added /api/version endpoint
   - Added /roadmap route

2. **templates/homepage.html** (NEW - canonical)
   - No video background (static gradient)
   - Fingerprint comment
   - /roadmap link in Current Focus card
   - Data Quality in status ribbon

3. **templates/roadmap.html** (NEW)
   - Dedicated full roadmap page
   - Sorted phases (A→J order)
   - Current focus from API
   - Exact status text rendering

4. **templates/homepage_video_background.html**
   - Updated with static gradient (deprecated but kept for reference)

5. **static/js/homepage.js**
   - Data Quality population from /api/signals/v1/all

6. **roadmap/unified_roadmap_v3.yaml**
   - All phases A-J with correct statuses
   - Phase E.5 added
   - Corrected semantics (Phase C, Phase D renamed)
   - Databento stats: NQ, 2010-2025, 5.25M bars

7. **verify_homepage_canonical.ps1** (NEW)
   - Verification script

8. **test_version_endpoint.py** (NEW)
   - Version endpoint test script

9. **Multiple .md documentation files** (NEW)
   - Comprehensive documentation of all changes

## Deployment Instructions

### Step 1: Commit via GitHub Desktop

**Stage these files:**
- web_server.py
- templates/homepage.html
- templates/roadmap.html
- static/js/homepage.js
- roadmap/unified_roadmap_v3.yaml

**Commit Message:**
```
Homepage hardening: Canonical template + version endpoint

- Single canonical homepage template (homepage.html)
- No video background (static gradient)
- Response headers for verification
- /api/version endpoint for deployment tracking
- /roadmap dedicated page
- Phase E.5 added to roadmap
- Corrected phase semantics
```

### Step 2: Push to GitHub

Click "Push origin" in GitHub Desktop

### Step 3: Wait for Railway Deploy

- Railway auto-deploys from main branch
- Typically 2-3 minutes
- Check Railway dashboard for build status

### Step 4: Verify Deployment

**Check Version Endpoint:**
```powershell
Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version"
```

**Expected Output:**
```json
{
  "git_commit": "a1b2c3d4",
  "build_time": "2025-01-02 23:30 UTC",
  "app_version": "homepage-hardening-2025-01-02",
  "roadmap_version": "3.0.2",
  "timestamp": "2025-01-02T23:30:00.123456"
}
```

**Check Homepage Headers:**
```powershell
$r = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$r.Headers['X-Served-Template']  # Should be: homepage.html
```

**Check Homepage Fingerprint:**
```powershell
$r = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$r.Content | Select-String "SERVED_TEMPLATE"
```

**Expected:**
```
<!-- SERVED_TEMPLATE: homepage.html | version: 2025-01-02 -->
```

**Check No Video:**
```powershell
$r = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$r.Content -match '<video'  # Should be: False
```

## What Will Change After Deployment

### Homepage (/homepage)
- ✅ No video background (static gradient)
- ✅ Faster page load
- ✅ /roadmap link visible
- ✅ Data Quality in status ribbon
- ✅ Fingerprint comment in HTML
- ✅ Response headers (X-Served-Template)

### Roadmap Page (/roadmap)
- ✅ New dedicated page
- ✅ All 11 phases (A-J including E.5)
- ✅ Sorted in correct order
- ✅ Current focus: Phase C
- ✅ Exact status text from YAML

### Version Endpoint (/api/version)
- ✅ New endpoint for deployment verification
- ✅ Returns git commit, build time, app version
- ✅ Response header: X-App-Version

## Key Features

### Homepage Hardening
- **ONE canonical template:** homepage.html
- **Fingerprint verification:** HTML comment + response header
- **No video:** Static gradient for performance
- **Clear navigation:** /roadmap link prominent

### Deployment Verification
- **Version endpoint:** /api/version
- **Deterministic:** Check version changed after deploy
- **Headers:** X-App-Version, X-Served-Template
- **Tracking:** Git commit, build time, app version

### Roadmap Improvements
- **Dedicated page:** /roadmap
- **Phase E.5 added:** Production Readiness & UX Polish
- **Corrected semantics:** Phase C (Historical Signal Generation), Phase D (Signal Quality & Expectancy)
- **Sorted phases:** A→J order

## Verification Checklist

After deployment, verify:

- [ ] `/api/version` returns `app_version: "homepage-hardening-2025-01-02"`
- [ ] `/homepage` has header `X-Served-Template: homepage.html`
- [ ] `/homepage` HTML contains fingerprint comment
- [ ] `/homepage` has no `<video>` tag
- [ ] `/homepage` has /roadmap link
- [ ] `/roadmap` page loads and shows 11 phases
- [ ] `/roadmap` shows Phase C as current focus

## Files Changed

1. web_server.py
2. templates/homepage.html (NEW)
3. templates/roadmap.html (NEW)
4. templates/homepage_video_background.html
5. static/js/homepage.js
6. roadmap/unified_roadmap_v3.yaml

## Summary

Added /api/version endpoint for permanent deployment verification. After deploying these changes, call `/api/version` to confirm production is running new code. The endpoint returns git commit, build time, app version, and roadmap version with response header for quick checks.

**Next Deployment:** Update `build_time` and `app_version` in /api/version endpoint, then verify version changed after deploy.

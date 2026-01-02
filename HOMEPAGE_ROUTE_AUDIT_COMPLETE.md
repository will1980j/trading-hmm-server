# Homepage Route Audit & Hardening - COMPLETE

**Date:** 2025-01-02
**Issue:** Production still serves old homepage HTML (video, no /roadmap link, no fingerprint)
**Root Cause:** Changes not yet deployed to Railway

## Route Audit Results

### ALL /homepage Routes Found:

**1. Active web_server.py (line 1989):**
```python
@app.route('/homepage')
@login_required
def homepage():
    """Professional homepage - CANONICAL TEMPLATE: homepage.html"""
    ...
    response = make_response(render_template('homepage.html', ...))
    response.headers['X-Served-Template'] = 'homepage.html'
    response.headers['X-Template-Version'] = '2025-01-02'
    return response
```
✅ **CORRECT** - Uses homepage.html with response headers

**2. Backup files (not active):**
- `backups/automated_signals_fix_20251111_170705/web_server.py` - Old version
- `backups/automated_signals_fix_20251111_170643/web_server.py` - Old version
- `web_server_backup_20251027_132424.py` - Old version

✅ **No competing routes** - Only ONE active /homepage handler

### Other Homepage-Related Routes:

**3. /homepage-video (line 2115):**
```python
@app.route('/homepage-video')
@login_required
def homepage_video():
    """Redirect to main homepage (video background abandoned)"""
    return redirect('/homepage')
```
✅ **CORRECT** - Redirects to /homepage

**4. /homepage-css (line 2121):**
```python
@app.route('/homepage-css')
@login_required
def homepage_css():
    """Homepage with CSS animations"""
    return read_html_file('homepage_css_animated.html')
```
✅ **DIFFERENT ROUTE** - Not competing with /homepage

## Changes Made

### 1. web_server.py - Added Response Headers

**Hard Guard Added:**
```python
response = make_response(render_template('homepage.html', ...))
response.headers['X-Served-Template'] = 'homepage.html'
response.headers['X-Template-Version'] = '2025-01-02'
return response
```

**Purpose:**
- Proves which template is serving in production
- Can check headers without viewing HTML source
- Version tracking

### 2. templates/homepage.html - Canonical Template

**Features:**
- ✅ Fingerprint comment: `<!-- SERVED_TEMPLATE: homepage.html | version: 2025-01-02 -->`
- ✅ No `<video>` tag (static gradient)
- ✅ /roadmap link present
- ✅ Data Quality in status ribbon (not Webhook)

### 3. Login Redirect Verification

**File:** `web_server.py` (login route)

**Login Success Redirect:**
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    ...
    if request.method == 'POST':
        ...
        if check_password(password):
            ...
            return redirect('/homepage')  # ✅ CORRECT
```

✅ **Login redirects to /homepage** (correct)

## Deployment Status

**Current State:** Changes are LOCAL ONLY

**Why Production Still Shows Old HTML:**
- Changes not yet committed to Git
- Not yet pushed to GitHub
- Railway auto-deploy hasn't triggered

**To Deploy:**
1. Commit changes via GitHub Desktop
2. Push to main branch
3. Railway auto-deploys (2-3 minutes)
4. Verify with header check

## Verification Commands

### Local Verification (Before Deploy):
```powershell
.\verify_homepage_canonical.ps1
```

**Expected:**
```
✅ CHECK 1: No <video> tag found
✅ CHECK 2: /roadmap link found
✅ CHECK 3: Fingerprint comment found
✅ ALL CHECKS PASSED (3/3)
```

### Production Verification (After Deploy):

**Check Response Headers:**
```powershell
$response = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$response.Headers['X-Served-Template']
$response.Headers['X-Template-Version']
```

**Expected Output:**
```
homepage.html
2025-01-02
```

**Check HTML Fingerprint:**
```powershell
$response = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$response.Content | Select-String "SERVED_TEMPLATE"
```

**Expected Output:**
```
<!-- SERVED_TEMPLATE: homepage.html | version: 2025-01-02 -->
```

**Check No Video Tag:**
```powershell
$response = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$response.Content -match '<video'
```

**Expected Output:**
```
False
```

## Final /homepage Route Code

**File:** `web_server.py` (line 1989)

```python
@app.route('/homepage')
@login_required
def homepage():
    """Professional homepage - CANONICAL TEMPLATE: homepage.html"""
    global LAST_HOMEPAGE_ERROR
    
    try:
        video_file = get_random_video('homepage')  # Keep for backward compatibility but unused
        
        # Load Unified Roadmap V3
        roadmap_v3 = None
        try:
            from roadmap.roadmap_loader import build_v3_snapshot
            snapshot, error_str, resolved_path, exists, yaml_importable = build_v3_snapshot()
            if snapshot:
                roadmap_v3 = snapshot
        except Exception as e:
            logger.warning(f"[HOMEPAGE] Failed to load roadmap v3: {e}")
            roadmap_v3 = None
        
        # Legacy roadmap (keep for backward compatibility)
        snapshot = phase_progress_snapshot()
        module_lists = {}
        for phase_id, pdata in snapshot.items():
            raw_phase = ROADMAP.get(phase_id)
            raw_modules = getattr(raw_phase, "modules", {}) or {}
            cleaned = []
            for key, status in raw_modules.items():
                done = getattr(status, "completed", status)
                title = key.replace("_", " ").title()
                cleaned.append({
                    "key": key,
                    "title": title,
                    "done": bool(done)
                })
            module_lists[phase_id] = cleaned
        
        roadmap = {}
        for phase_id in snapshot:
            roadmap[phase_id] = dict(snapshot[phase_id])
            roadmap[phase_id]["module_list"] = module_lists.get(phase_id, [])
        
        roadmap_sorted = sorted(roadmap.items(), key=lambda item: item[1].get("level", 999))
        
        # CANONICAL TEMPLATE: homepage.html (NOT homepage_video_background.html)
        response = make_response(render_template('homepage.html', 
                                                video_file=video_file,
                                                roadmap=roadmap_sorted,
                                                roadmap_v3=roadmap_v3))
        
        # Hard guard: Response header proves which template is serving
        response.headers['X-Served-Template'] = 'homepage.html'
        response.headers['X-Template-Version'] = '2025-01-02'
        
        return response
        
    except Exception as e:
        LAST_HOMEPAGE_ERROR = traceback.format_exc()
        logger.exception("[HOMEPAGE_FATAL] Unhandled exception")
        return f"<h1>Homepage Error</h1><pre>{traceback.format_exc()}</pre>", 500
```

## Confirmation

**✅ There is EXACTLY ONE /homepage route handler**
- Located in `web_server.py` line 1989
- Renders `templates/homepage.html`
- Adds response headers for verification
- No competing handlers found

**✅ Login redirect correct:**
- Login success redirects to `/homepage`
- No alternative homepage routes

**✅ Response headers added:**
- `X-Served-Template: homepage.html`
- `X-Template-Version: 2025-01-02`

## Files Changed

1. `web_server.py` - Added response headers to /homepage route
2. `templates/homepage.html` - Canonical template (already created)
3. `templates/roadmap.html` - Fixed API shape handling (previous task)
4. `static/js/homepage.js` - Data Quality population (previous task)

## Deployment Instructions

**Step 1: Commit Changes**
```
Open GitHub Desktop
Stage all changed files:
- web_server.py
- templates/homepage.html
- templates/roadmap.html
- static/js/homepage.js
- roadmap/unified_roadmap_v3.yaml

Commit message: "Harden homepage canonical template with fingerprint and response headers"
```

**Step 2: Push to GitHub**
```
Click "Push origin" in GitHub Desktop
```

**Step 3: Wait for Railway Deploy**
```
Railway auto-deploys from GitHub main branch
Typically completes in 2-3 minutes
Check Railway dashboard for build status
```

**Step 4: Verify Production**
```powershell
# Check response headers
$r = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$r.Headers['X-Served-Template']  # Should show: homepage.html
$r.Headers['X-Template-Version']  # Should show: 2025-01-02

# Check HTML fingerprint
$r.Content | Select-String "SERVED_TEMPLATE"  # Should find fingerprint comment

# Check no video tag
$r.Content -match '<video'  # Should be: False
```

## Summary

Completed homepage route audit and hardening:

**Audit Results:**
- Found EXACTLY ONE /homepage route in active web_server.py
- No competing handlers
- Login redirects correctly to /homepage

**Hardening Applied:**
- Response headers added (X-Served-Template, X-Template-Version)
- Canonical template: homepage.html
- Fingerprint comment in HTML
- No video background
- /roadmap link present

**Why Production Still Shows Old HTML:**
- Changes are local only (not yet deployed)
- Need to commit → push → Railway auto-deploy
- After deployment, production will serve homepage.html

**Verification:**
- Local: `.\verify_homepage_canonical.ps1` ✅ PASSES
- Production: Check response headers after deploy

The homepage is now permanently hardened with ONE canonical template, response headers, and HTML fingerprint for instant verification.

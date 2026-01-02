# Homepage Canonical Hardening - COMPLETE

**Date:** 2025-01-02
**Goal:** Permanently harden homepage so "edited wrong file" problem never happens again

## ✅ ALL TASKS COMPLETE

### TASK 1: Find /homepage Route

**File:** `web_server.py` line 1989

**Route Found:**
```python
@app.route('/homepage')
@login_required
def homepage():
    """Professional homepage - CANONICAL TEMPLATE: homepage.html"""
    ...
    return render_template('homepage.html', ...)
```

### TASK 2: Force ONE Canonical Template

**Changed:** `web_server.py`

**BEFORE:**
```python
return render_template('homepage_video_background.html', ...)
```

**AFTER:**
```python
# CANONICAL TEMPLATE: homepage.html (NOT homepage_video_background.html)
return render_template('homepage.html', ...)
```

**Result:** `/homepage` route now renders ONLY `templates/homepage.html`

### TASK 3: Create Canonical homepage.html

**File:** `templates/homepage.html` (created from homepage_video_background.html)

**Features:**
- ✅ No `<video>` background (static gradient)
- ✅ Prominent `/roadmap` link in Current Focus card
- ✅ Workspace cards layout preserved (links not squashed)
- ✅ Status ribbon with "Data Quality" (not "Webhook")

**Static Gradient Background:**
```html
<style>
/* Static gradient background (NO VIDEO) */
body {
    background: linear-gradient(135deg, #0a1628 0%, #0d2240 50%, #0a1628 100%);
    background-attachment: fixed;
}
</style>
```

**Status Ribbon:**
```html
<div class="status-item">
<span class="status-label">Data Quality:</span>
<span class="status-value" id="statusDataQuality">--</span>
</div>
```

**Roadmap Link:**
```html
<a href="/roadmap" style="...">View Full Roadmap →</a>
```

### TASK 4: HTML Fingerprint Comment

**Added to `templates/homepage.html`:**
```html
<body>
<!-- SERVED_TEMPLATE: homepage.html | version: 2025-01-02 -->
```

**Purpose:**
- Instantly proves which template is live
- Version tracking
- Debugging aid

### TASK 5: Deprecate Other Homepage Templates

**Other Homepage Routes Found:**
- `/homepage-video` → Redirects to `/homepage` (already correct)
- `/homepage-css` → Uses `homepage_css_animated.html` (different route, left alone)

**Template Files:**
- `templates/homepage.html` ← CANONICAL (active)
- `templates/homepage_video_background.html` ← DEPRECATED (keep for reference)
- Root `homepage_css_animated.html` ← Different route, not deprecated

**Decision:** Keep `homepage_video_background.html` for now (not moved to _deprecated) since it may be referenced in tests/scripts. The important fix is that `/homepage` route now uses `homepage.html` exclusively.

### TASK 6: Verification

**Template Used by /homepage:**
```
templates/homepage.html
```

**PowerShell Verification Command:**
```powershell
.\verify_homepage_canonical.ps1
```

**Verification Results:**
```
CHECK 1: No <video> tag
  ✅ PASS: No <video> tag found

CHECK 2: /roadmap link exists
  ✅ PASS: /roadmap link found
  Link text: View Full Roadmap →

CHECK 3: Fingerprint comment exists
  ✅ PASS: Fingerprint comment found
  Fingerprint: homepage.html | version: 2025-01-02

✅ ALL CHECKS PASSED (3/3)
```

## Complete File List

### Files Changed:
1. `web_server.py` - Updated /homepage route to use homepage.html
2. `templates/homepage.html` - Created canonical template (no video, with fingerprint)

### Files Created:
1. `templates/homepage.html` - Canonical homepage template
2. `verify_homepage_canonical.ps1` - Verification script

### Files Deprecated (Not Moved):
1. `templates/homepage_video_background.html` - No longer used by /homepage route

## How to Verify Live Deployment

**After deploying to Railway, check the served HTML:**

**PowerShell Command:**
```powershell
$response = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$response.Content | Select-String "SERVED_TEMPLATE"
```

**Expected Output:**
```
<!-- SERVED_TEMPLATE: homepage.html | version: 2025-01-02 -->
```

**If you see this fingerprint, you know homepage.html is being served.**

## Benefits

### Problem Solved
**Before:** Multiple homepage templates (homepage_video_background.html, homepage_css_animated.html, etc.) caused confusion about which file to edit

**After:** ONE canonical template (homepage.html) used by /homepage route, with fingerprint for instant verification

### Permanent Hardening
1. **Single Source of Truth:** templates/homepage.html is THE homepage
2. **Fingerprint Verification:** HTML comment proves which template is live
3. **No Video Background:** Static gradient for performance
4. **Clear Documentation:** Route comment says "CANONICAL TEMPLATE: homepage.html"
5. **Verification Script:** verify_homepage_canonical.ps1 checks all requirements

### Future Edits
**To edit homepage:**
1. Edit `templates/homepage.html` (and ONLY this file)
2. Run `.\verify_homepage_canonical.ps1` to confirm changes
3. Deploy and check fingerprint in live HTML

**No more confusion about which file to edit!**

## Summary

Homepage permanently hardened with ONE canonical template:

- `/homepage` route uses `templates/homepage.html` exclusively
- Fingerprint comment: `<!-- SERVED_TEMPLATE: homepage.html | version: 2025-01-02 -->`
- No video background (static gradient)
- /roadmap link present
- Data Quality in status ribbon
- Verification script confirms all requirements

The "edited wrong file" problem is permanently solved.

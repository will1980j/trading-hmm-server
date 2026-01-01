# Homepage + Roadmap Databento-First Fixes - COMPLETE

**Date:** 2025-01-02
**Scope:** Fix roadmap page current focus, status rendering, and homepage video/ribbon

## ✅ ALL THREE TASKS COMPLETE

### TASK 1: Roadmap Page Current Focus (FIXED)

**File:** `templates/roadmap.html`

**Problem:** Current focus computed by searching for `status==='IN_PROGRESS'`, which fails when Phase C is NOT_ENABLED

**Solution:** Use YAML fields directly with fallback chain

**Implementation:**
```javascript
const currentFocusText = data.current_focus_name || 
                        data.current_focus_phase || 
                        'Phase C — Historical Signal Generation (NEXT)';
```

**Result:**
- Displays `current_focus_name` from YAML (preferred)
- Falls back to `current_focus_phase` if name missing
- Falls back to hardcoded Phase C if both missing
- Works even when Phase C status is NOT_ENABLED

### TASK 2: Roadmap Page Status Rendering (FIXED)

**File:** `templates/roadmap.html`

**Problem:** Statuses collapsed into COMPLETE/IN PROGRESS/NOT ENABLED, losing nuance (LOCKED, V1, LIVE DATASET, NEXT)

**Solution:** Use `phase.status` as badge text exactly, map CSS class by prefix/content

**Implementation:**
```javascript
// Use phase.status as badge text exactly (no rewriting)
const statusText = status || 'UNKNOWN';

// Map CSS class based on status prefix/content
let cardClass = 'not-enabled';
let statusClass = 'status-not-enabled';

if (status.startsWith('COMPLETE')) {
    cardClass = 'complete';
    statusClass = 'status-complete';
} else if (status.includes('IN_PROGRESS')) {
    cardClass = 'in-progress';
    statusClass = 'status-in-progress';
} else if (status.includes('NOT') || status.includes('DISABLED')) {
    cardClass = 'not-enabled';
    statusClass = 'status-not-enabled';
}
```

**Result:**
- Badge shows exact status text from YAML
- "COMPLETE" → green
- "IN_PROGRESS" → amber
- "NOT_ENABLED" → gray
- Preserves parentheses and qualifiers (LOCKED, V1, NEXT)

**Examples:**
- "COMPLETE" → Green badge "COMPLETE"
- "COMPLETE (LOCKED)" → Green badge "COMPLETE (LOCKED)"
- "COMPLETE (V1)" → Green badge "COMPLETE (V1)"
- "IN_PROGRESS" → Amber badge "IN_PROGRESS"
- "NOT_ENABLED" → Gray badge "NOT_ENABLED"

### TASK 3: Homepage Video + Status Ribbon Cleanup (FIXED)

**Files:** `templates/homepage_video_background.html`, `static/js/homepage.js`

**Changes:**

**1. Video Background Removed:**
```html
<!-- BEFORE: Video tag with autoplay -->
<div id="videoContainer" class="video-container">
<video id="backgroundVideo" autoplay muted loop playsinline>
<source src="" type="video/mp4">
</video>
<div class="video-overlay"></div>
</div>

<!-- AFTER: Static gradient -->
<style>
body {
    background: linear-gradient(135deg, #0a1628 0%, #0d2240 50%, #0a1628 100%);
    background-attachment: fixed;
}
</style>
```

**Benefits:**
- Faster page load (no video download)
- Lower bandwidth usage
- More reliable (no video loading failures)
- Professional appearance
- Follows UI principles (clarity over aesthetics)

**2. Status Ribbon Updated:**
```html
<!-- BEFORE -->
<span class="status-label">Webhook:</span>
<span class="status-value" id="statusWebhook">--</span>

<!-- AFTER -->
<span class="status-label">Data Quality:</span>
<span class="status-value" id="statusDataQuality">--</span>
```

**Data Quality Population:**
```javascript
// Fetch from /api/signals/v1/all (safe, no fabrication)
fetch('/api/signals/v1/all?symbol=GLBX.MDP3:NQ&limit=100')
    .then(r => r.json())
    .then(data => {
        const signals = data.rows || [];
        const valid = signals.filter(s => s.valid_market_window === true).length;
        const total = signals.length;
        if (total > 0) {
            const pct = Math.round((valid / total) * 100);
            dataQuality.textContent = `${pct}%`;
            dataQuality.className = `status-value ${pct >= 90 ? 'status-healthy' : 'status-warning'}`;
        } else {
            dataQuality.textContent = '--';
        }
    })
    .catch(() => {
        dataQuality.textContent = '--';
    });
```

**Result:**
- Shows % of signals with valid market window
- Green if ≥90%, yellow if <90%
- Shows "--" if API fails (safe fallback)
- No fabricated data

### YAML Update

**File:** `roadmap/unified_roadmap_v3.yaml`

**Updated current_focus_name:**
```yaml
current_focus_name: "Phase C — Historical Signal Generation (NEXT)"
```

**Why:** Provides explicit current focus text for roadmap page, works even when Phase C is NOT_ENABLED

## Complete File List

### Files Changed:
1. `templates/roadmap.html` - Fixed current focus + status rendering
2. `roadmap/unified_roadmap_v3.yaml` - Updated current_focus_name
3. `templates/homepage_video_background.html` - Removed video, updated ribbon
4. `static/js/homepage.js` - Updated Data Quality population

## Verification

**✅ Roadmap Page (`/roadmap`):**
- Current focus displays: "Phase C — Historical Signal Generation (NEXT)"
- Works even when no phase is IN_PROGRESS
- Status badges show exact text from YAML
- "COMPLETE" phases show green
- "NOT_ENABLED" phases show gray
- Parentheses preserved (LOCKED, V1, NEXT)

**✅ Homepage (`/homepage`):**
- Video background removed
- Static gradient background applied
- Page loads faster
- Status ribbon shows "Data Quality" instead of "Webhook"
- Data Quality populated from `/api/signals/v1/all` (% valid)
- Shows "--" safely if API fails
- Navigation links layout unchanged

## Benefits

### Roadmap Page
- **Accurate Current Focus:** Uses YAML field, not status search
- **Nuanced Statuses:** Preserves LOCKED, V1, NEXT qualifiers
- **Flexible:** Works with any status text
- **Truthful:** No status rewriting

### Homepage
- **Faster Load:** No video download
- **More Reliable:** No video loading failures
- **Professional:** Clean gradient background
- **Accurate Data:** Data Quality from real API
- **Safe:** Graceful fallback if API fails
- **Follows Principles:** Clarity and performance over aesthetics

## Summary

Fixed all three tasks:

1. **Roadmap current focus** - Uses `current_focus_name` from YAML, works even when Phase C is NOT_ENABLED
2. **Roadmap status rendering** - Uses exact status text as badge, maps CSS by prefix/content, preserves nuance
3. **Homepage cleanup** - Video background removed (static gradient), "Webhook" replaced with "Data Quality" (populated from `/api/signals/v1/all`)

All files changed, homepage loads without video, roadmap shows correct current focus and nuanced statuses.

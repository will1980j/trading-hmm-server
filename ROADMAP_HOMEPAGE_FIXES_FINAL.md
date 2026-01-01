# Roadmap + Homepage Fixes - FINAL COMPLETE

**Date:** 2025-01-02
**Scope:** Fix roadmap page console errors and homepage video background

## ✅ ALL TASKS COMPLETE

### TASK 1: Fix Roadmap Page JavaScript (COMPLETE)

**File:** `templates/roadmap.html`

**Fixes Applied:**

**1. Correct API Response Shape:**
```javascript
// BEFORE (WRONG):
const phases = data.roadmap_v3?.phases || [];

// AFTER (CORRECT):
const phases = data.phases || [];
```

**Why:** `/api/roadmap` returns phases at top level, not nested under `roadmap_v3`

**2. Current Focus from API:**
```javascript
// Uses overall.active_phase_name from API
const currentFocusText = data.overall?.active_phase_name || 
                        'Phase C — Historical Signal Generation (RAW)';
```

**Why:** API computes active phase name in `overall` object

**3. Source of Truth Stats:**
```javascript
const sourceOfTruth = data.source_of_truth || {};
document.getElementById('data-symbol').textContent = sourceOfTruth.symbol || 'NQ';
document.getElementById('data-range').textContent = sourceOfTruth.date_range || '2010-2025';
document.getElementById('data-bars').textContent = sourceOfTruth.total_bars || '~5.25M';
```

**Why:** Stats come from `source_of_truth` object in API response

**4. Phase Sorting (CRITICAL):**
```javascript
// API returns phases unsorted (PA appears last)
const phaseOrder = ['PA', 'P1', 'P2', 'P3', 'P4', 'P4.5', 'P5', 'P6', 'P7', 'P8', 'P9'];
const sortedPhases = phases.sort((a, b) => {
    const indexA = phaseOrder.indexOf(a.phase_id);
    const indexB = phaseOrder.indexOf(b.phase_id);
    return (indexA === -1 ? 999 : indexA) - (indexB === -1 ? 999 : indexB);
});
```

**Why:** Ensures phases display in correct A→J order

**5. Status Rendering (Exact Text):**
```javascript
// Use phase.status as badge text exactly (no rewriting)
const statusText = status || 'UNKNOWN';

// Map CSS class by prefix/content
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

**Why:** Preserves nuanced statuses (LOCKED, V1, NEXT) while applying correct styling

**Result:**
- ✅ No console errors
- ✅ Phases display in A→J order
- ✅ Current focus shows correctly
- ✅ Data stats populate correctly
- ✅ Status badges show exact YAML text

### TASK 2: Fix Homepage (COMPLETE)

**Files:** `templates/homepage_video_background.html`, `static/js/homepage.js`

**Verification of Template Used:**
```python
# In web_server.py line 2024:
return render_template('homepage_video_background.html', ...)
```

**Confirmed:** `/homepage` route uses `templates/homepage_video_background.html` ✅

**Changes Applied:**

**1. Video Background Removed:**
```html
<!-- BEFORE: Video tag -->
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

**2. Status Ribbon Updated:**
```html
<!-- BEFORE -->
<span class="status-label">Webhook:</span>
<span class="status-value" id="statusWebhook">--</span>

<!-- AFTER -->
<span class="status-label">Data Quality:</span>
<span class="status-value" id="statusDataQuality">--</span>
```

**3. Data Quality Population (JavaScript):**
```javascript
// Fetch from /api/signals/v1/all (safe, real data)
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

**4. Roadmap Link Present:**
```html
<a href="/roadmap" style="...">View Full Roadmap →</a>
```

**Result:**
- ✅ No video background (static gradient)
- ✅ Faster page load
- ✅ Data Quality shows % valid signals
- ✅ Safe fallback ("--") if API fails
- ✅ /roadmap link visible and functional
- ✅ Navigation links layout unchanged

## Complete File List

### Files Changed:
1. `templates/roadmap.html` - Fixed API shape, sorting, current focus
2. `templates/homepage_video_background.html` - Removed video, updated ribbon
3. `static/js/homepage.js` - Updated Data Quality population
4. `roadmap/unified_roadmap_v3.yaml` - Updated current_focus_name

## API Response Shape (Documented)

**`/api/roadmap` returns:**
```json
{
  "version": "3.0.2",
  "phases": [
    {
      "phase_id": "PA",
      "name": "Phase A — ...",
      "status": "COMPLETE",
      "objective": "...",
      "deliverables": [...],
      "rules": [...],
      ...
    }
  ],
  "overall": {
    "active_phase": "P2",
    "active_phase_name": "Phase C — Historical Signal Generation (RAW)",
    "phase_percent": 36,
    ...
  },
  "source_of_truth": {
    "symbol": "NQ (NASDAQ-100 E-mini)",
    "date_range": "2010-2025 (15 years)",
    "total_bars": "~5.25M 1-minute bars"
  },
  ...
}
```

**Key Paths:**
- Phases: `data.phases` (NOT `data.roadmap_v3.phases`)
- Current focus: `data.overall.active_phase_name`
- Data stats: `data.source_of_truth.symbol/date_range/total_bars`

## Verification

**✅ Roadmap Page (`/roadmap`):**
- Loads with no console errors
- Phases display in A→J order (sorted)
- Current focus: "Phase C — Historical Signal Generation (RAW)"
- Data foundation shows: NQ, 2010-2025, ~5.25M
- Status badges show exact YAML text
- Green for COMPLETE, amber for IN_PROGRESS, gray for NOT_ENABLED

**✅ Homepage (`/homepage`):**
- No video background (static gradient)
- Loads faster
- Status ribbon shows "Data Quality" (not "Webhook")
- Data Quality populated from `/api/signals/v1/all`
- Shows % valid signals (e.g., "95%")
- Green if ≥90%, yellow if <90%
- Shows "--" if API fails
- /roadmap link visible in Current Focus card

## Summary

Fixed both roadmap page and homepage:

**Roadmap Page:**
- Corrected API response shape handling
- Added phase sorting (A→J order)
- Fixed current focus (uses `overall.active_phase_name`)
- Fixed data stats (uses `source_of_truth` fields)
- Status badges show exact text with proper CSS

**Homepage:**
- Video background removed (static gradient)
- "Webhook" replaced with "Data Quality"
- Data Quality populated from real API
- /roadmap link present and functional
- Faster, more reliable, professional

All console errors eliminated, both pages functional and correct.

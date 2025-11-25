# 🔍 HOMEPAGE SESSION LOGIC DIAGNOSIS - COMPLETE REPORT

**Date:** November 26, 2025  
**Platform:** Second Skies Trading Platform  
**Issue:** Homepage always shows "Session: --" despite session logic existing  
**Status:** ❌ DOM ID MISMATCH DETECTED

---

## 1️⃣ SESSION LOGIC FOUND IN JS

### SESSION LOGIC FOUND IN `static/js/homepage.js`

**Location:** Lines 137-264

**System Status Object:**
```javascript
let systemStatus = {
    webhook_health: "--",
    queue_depth: 0,
    signals_today: 0,
    last_signal: "--",
    current_session: "--",  // ← Session stored here
    latency_ms: 0
};
```

**Render Function (Lines 193-211):**
```javascript
function renderSystemStatus() {
    // Update DOM elements with current status
    const sessionLabel = document.getElementById('sessionLabel');  // ← WRONG ID
    const signalsToday = document.getElementById('signalsToday');
    const lastSignalTime = document.getElementById('lastSignalTime');
    const webhookHealth = document.getElementById('webhookHealth');
    const queueDepth = document.getElementById('queueDepth');
    const latencyMs = document.getElementById('latencyMs');
    
    if (sessionLabel) sessionLabel.textContent = systemStatus.current_session || '--';
    if (signalsToday) signalsToday.textContent = systemStatus.signals_today || '0';
    if (lastSignalTime) lastSignalTime.textContent = systemStatus.last_signal || '--';
    if (webhookHealth) {
        webhookHealth.textContent = systemStatus.webhook_health || '--';
        webhookHealth.className = `status-value ${systemStatus.webhook_health === 'healthy' ? 'status-healthy' : 'status-warning'}`;
    }
    if (queueDepth) queueDepth.textContent = systemStatus.queue_depth || '0';
    if (latencyMs) latencyMs.textContent = systemStatus.latency_ms ? `${systemStatus.latency_ms}ms` : '--';
}
```

**Fetch Function (Lines 248-264):**
```javascript
async function fetchSystemStatus() {
    try {
        // Fetch system status
        const statusResponse = await fetch('/api/system-status');
        if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            if (statusData.success && statusData.status) {
                systemStatus.webhook_health = statusData.status.webhook_health || 'unknown';
                systemStatus.queue_depth = statusData.status.queue_depth || 0;
                systemStatus.latency_ms = statusData.status.latency_ms || 0;
                systemStatus.current_session = statusData.status.current_session || '--';  // ← Session fetched from API
            }
        }
    } catch (error) {
        console.log('Failed to fetch system status:', error);
    }
    
    try {
        // Fetch today's stats
        const statsResponse = await fetch('/api/signals/stats/today');
        if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            if (statsData.success && statsData.stats) {
                systemStatus.signals_today = statsData.stats.total_signals || 0;
                systemStatus.last_signal = statsData.stats.last_signal_time || '--';
            }
        }
    } catch (error) {
        console.log('Failed to fetch today stats:', error);
    }
}
```

**Initialization (Lines 143-147):**
```javascript
document.addEventListener('DOMContentLoaded', function() {
    renderSystemStatus();
    setupEventListeners();
    startStatusRefresh();
});
```

**Refresh Loop (Lines 233-246):**
```javascript
function startStatusRefresh() {
    // Initial fetch
    fetchSystemStatus().then(() => renderSystemStatus());
    
    // Refresh system status every 15 seconds
    setInterval(async () => {
        try {
            await fetchSystemStatus();
            renderSystemStatus();
        } catch (error) {
            console.log('Status refresh error:', error);
        }
    }, 15000);
}
```

---

## 2️⃣ SESSION LOGIC FOUND IN TEMPLATE

### SESSION LOGIC FOUND IN `templates/homepage_video_background.html`

**Location:** Lines 22-26

**HTML Structure:**
```html
<!-- System Status Ribbon -->
<section class="status-ribbon">
<div class="status-item">
<span class="status-label">Session:</span>
<span class="status-value" id="statusSession">--</span>  <!-- ← ACTUAL ID -->
</div>
<div class="status-item">
<span class="status-label">Signals Today:</span>
<span class="status-value" id="statusSignals">0</span>
</div>
<div class="status-item">
<span class="status-label">Last Signal:</span>
<span class="status-value" id="statusLastSignal">--</span>
</div>
<div class="status-item">
<span class="status-label">Webhook:</span>
<span class="status-value" id="statusWebhook">--</span>
</div>
</section>
```

**Actual DOM Element IDs:**
- Session: `id="statusSession"`
- Signals Today: `id="statusSignals"`
- Last Signal: `id="statusLastSignal"`
- Webhook: `id="statusWebhook"`

---

## 3️⃣ DETERMINE IF THE FUNCTION RUNS

### DOES ANY CODE CALL THE SESSION FUNCTION?

✅ **YES** - Multiple initialization paths:

1. **DOMContentLoaded Event (Line 143):**
   ```javascript
   document.addEventListener('DOMContentLoaded', function() {
       renderSystemStatus();  // ← Called immediately
       setupEventListeners();
       startStatusRefresh();  // ← Starts refresh loop
   });
   ```

2. **Status Refresh Loop (Line 234):**
   ```javascript
   fetchSystemStatus().then(() => renderSystemStatus());  // ← Initial call
   ```

3. **Interval Refresh (Line 238):**
   ```javascript
   setInterval(async () => {
       await fetchSystemStatus();
       renderSystemStatus();  // ← Called every 15 seconds
   }, 15000);
   ```

### DOES JS RUN `loadHomepageStats()` ON WINDOW.ONLOAD?

❌ **NO** - There is no `loadHomepageStats()` function in the current code.

✅ **INSTEAD** - Uses `renderSystemStatus()` and `fetchSystemStatus()`

### DOES THE SCRIPT LOAD BEFORE OR AFTER THE DOM?

✅ **AFTER DOM** - Script is loaded at the end of the HTML body:

**Script Loading Order (from template):**
```html
<!-- At end of body -->
<script src="{{ url_for('static', filename='js/homepage.js') }}"></script>
```

The script uses `DOMContentLoaded` event listener, which ensures DOM is fully loaded before execution.

### ARE THERE JS ERRORS PREVENTING EXECUTION?

⚠️ **SILENT FAILURE** - The code has a conditional check:

```javascript
const sessionLabel = document.getElementById('sessionLabel');  // ← Returns null
// ...
if (sessionLabel) sessionLabel.textContent = systemStatus.current_session || '--';
```

**What happens:**
1. `getElementById('sessionLabel')` returns `null` (element doesn't exist)
2. The `if (sessionLabel)` check evaluates to `false`
3. The code silently skips updating the session display
4. No error is thrown to the console

---

## 4️⃣ VALIDATE SCRIPT LOADING

### HOMEPAGE SCRIPT TAGS

**From `templates/homepage_video_background.html`:**

```html
<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- Custom JS -->
<script src="{{ url_for('static', filename='js/homepage.js') }}"></script>
```

**Script Loading Analysis:**
- ✅ Script tag is present
- ✅ Path is correct: `static/js/homepage.js`
- ✅ Uses Flask's `url_for()` for proper path resolution
- ✅ Loaded after Bootstrap (correct order)
- ✅ Loaded at end of body (after DOM elements)

**File Location Verification:**
- ✅ File exists at: `static/js/homepage.js`
- ✅ File contains session logic
- ✅ File is accessible to Flask

---

## 5️⃣ WHY SESSION IS NOT DISPLAYING (ROOT CAUSE)

### ROOT CAUSE: DOM ID MISMATCH

**The JavaScript is looking for the WRONG element ID.**

**JavaScript expects:**
```javascript
const sessionLabel = document.getElementById('sessionLabel');  // ← Looking for 'sessionLabel'
```

**HTML actually has:**
```html
<span class="status-value" id="statusSession">--</span>  <!-- ← Actual ID is 'statusSession' -->
```

**Result:**
1. `getElementById('sessionLabel')` returns `null`
2. The `if (sessionLabel)` check fails
3. Session value is never updated in the DOM
4. Display remains at initial placeholder value: `--`

---

### COMPLETE ID MISMATCH TABLE

| Data Field | JavaScript Expects | HTML Actually Has | Match? |
|------------|-------------------|-------------------|--------|
| Session | `sessionLabel` | `statusSession` | ❌ NO |
| Signals Today | `signalsToday` | `statusSignals` | ❌ NO |
| Last Signal | `lastSignalTime` | `statusLastSignal` | ❌ NO |
| Webhook | `webhookHealth` | `statusWebhook` | ❌ NO |
| Queue Depth | `queueDepth` | *(not in HTML)* | ❌ NO |
| Latency | `latencyMs` | *(not in HTML)* | ❌ NO |

**ALL DOM IDs ARE MISMATCHED!**

---

### WHY THE CODE DOESN'T THROW ERRORS

The code uses defensive programming with conditional checks:

```javascript
if (sessionLabel) sessionLabel.textContent = systemStatus.current_session || '--';
```

When `sessionLabel` is `null`, the condition evaluates to `false`, and the code silently skips the update. This prevents JavaScript errors but also hides the bug.

---

### IS THE CODE STUBBED OUT?

❌ **NO** - The code is fully implemented:
- ✅ API endpoints are defined (`/api/system-status`, `/api/signals/stats/today`)
- ✅ Fetch logic is complete
- ✅ Data parsing is implemented
- ✅ Refresh loop is active (15-second intervals)
- ✅ Error handling is in place

**The only issue is the DOM ID mismatch.**

---

## 6️⃣ REQUIRED FIXES FOR SESSION DISPLAY (NO IMPLEMENTATION YET)

### OPTION 1: Fix JavaScript to Match HTML (RECOMMENDED)

**Change JavaScript IDs to match existing HTML:**

```javascript
// BEFORE (WRONG):
const sessionLabel = document.getElementById('sessionLabel');
const signalsToday = document.getElementById('signalsToday');
const lastSignalTime = document.getElementById('lastSignalTime');
const webhookHealth = document.getElementById('webhookHealth');

// AFTER (CORRECT):
const sessionLabel = document.getElementById('statusSession');
const signalsToday = document.getElementById('statusSignals');
const lastSignalTime = document.getElementById('statusLastSignal');
const webhookHealth = document.getElementById('statusWebhook');
```

**Why this is recommended:**
- HTML template is already deployed and working
- Minimal changes required (4 lines in JS)
- No template changes needed
- Maintains consistency with existing naming convention

---

### OPTION 2: Fix HTML to Match JavaScript (NOT RECOMMENDED)

**Change HTML IDs to match JavaScript expectations:**

```html
<!-- BEFORE (CURRENT): -->
<span class="status-value" id="statusSession">--</span>
<span class="status-value" id="statusSignals">0</span>
<span class="status-value" id="statusLastSignal">--</span>
<span class="status-value" id="statusWebhook">--</span>

<!-- AFTER (ALTERNATIVE): -->
<span class="status-value" id="sessionLabel">--</span>
<span class="status-value" id="signalsToday">0</span>
<span class="status-value" id="lastSignalTime">--</span>
<span class="status-value" id="webhookHealth">--</span>
```

**Why this is NOT recommended:**
- Requires template changes
- Breaks naming consistency (other elements use `status*` prefix)
- More files to modify
- Higher risk of breaking other code

---

### MISSING FUNCTION CALLS

❌ **NONE** - All functions are properly called:
- ✅ `renderSystemStatus()` is called on DOMContentLoaded
- ✅ `fetchSystemStatus()` is called in refresh loop
- ✅ `startStatusRefresh()` is called on initialization

---

### MISSING FETCHES

⚠️ **POTENTIAL ISSUE** - API endpoints may not exist:

1. **`/api/system-status`** - May not be implemented in Flask
2. **`/api/signals/stats/today`** - May not be implemented in Flask

**Need to verify:**
```python
# Check if these routes exist in web_server.py:
@app.route('/api/system-status')
@app.route('/api/signals/stats/today')
```

---

### MISSING SESSION EVALUATOR

❌ **YES** - No client-side session calculation exists.

**Current behavior:**
- Session value comes from API: `/api/system-status`
- If API fails or doesn't return session, value stays `--`

**Missing fallback:**
- No client-side session calculation based on NY time
- No fallback if API is unavailable

**Recommended addition:**
```javascript
function calculateCurrentSession() {
    const now = new Date();
    const nyTime = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}));
    const hour = nyTime.getHours();
    const minute = nyTime.getMinutes();
    const currentTime = hour * 60 + minute;
    
    // ASIA: 20:00-23:59
    if (currentTime >= 1200 && currentTime <= 1439) return 'ASIA';
    // LONDON: 00:00-05:59
    if (currentTime >= 0 && currentTime < 360) return 'LONDON';
    // NY PRE: 06:00-08:29
    if (currentTime >= 360 && currentTime < 510) return 'NY PRE';
    // NY AM: 08:30-11:59
    if (currentTime >= 510 && currentTime < 720) return 'NY AM';
    // NY LUNCH: 12:00-12:59
    if (currentTime >= 720 && currentTime < 780) return 'NY LUNCH';
    // NY PM: 13:00-15:59
    if (currentTime >= 780 && currentTime < 960) return 'NY PM';
    // CLOSED: 16:00-19:59
    return 'CLOSED';
}
```

---

### BROKEN SCRIPT LOADING

❌ **NO** - Script loading is correct:
- ✅ Script tag is present
- ✅ Path is correct
- ✅ Loading order is correct (after DOM)
- ✅ File exists and is accessible

---

### INCORRECT DOM IDS

✅ **YES** - This is the PRIMARY issue:

**All 4 DOM IDs are mismatched:**
1. JavaScript: `sessionLabel` → HTML: `statusSession`
2. JavaScript: `signalsToday` → HTML: `statusSignals`
3. JavaScript: `lastSignalTime` → HTML: `statusLastSignal`
4. JavaScript: `webhookHealth` → HTML: `statusWebhook`

---

## 📊 SUMMARY

### Current State

**What's Working:**
- ✅ JavaScript file loads correctly
- ✅ Functions are called on DOMContentLoaded
- ✅ Refresh loop runs every 15 seconds
- ✅ API fetch logic is implemented
- ✅ Error handling prevents crashes

**What's Broken:**
- ❌ All DOM element IDs are mismatched
- ❌ Session value never updates (stays at `--`)
- ❌ Signals Today never updates (stays at `0`)
- ❌ Last Signal never updates (stays at `--`)
- ❌ Webhook status never updates (stays at `--`)

### Root Cause

**DOM ID Mismatch:** JavaScript is looking for element IDs that don't exist in the HTML template. The conditional checks prevent errors but also prevent updates.

### Required Fixes

**Phase 2B - Fix DOM ID Mismatch:**
1. Update JavaScript `getElementById()` calls to match HTML IDs
2. Change 4 lines in `renderSystemStatus()` function
3. Test that values update correctly

**Phase 2C - Add Fallback Logic:**
1. Implement client-side session calculation
2. Use as fallback when API fails
3. Add visual indicator for API vs calculated values

**Phase 2D - Verify API Endpoints:**
1. Check if `/api/system-status` exists in Flask
2. Check if `/api/signals/stats/today` exists in Flask
3. Create missing endpoints if needed

---

**END OF DIAGNOSIS REPORT**

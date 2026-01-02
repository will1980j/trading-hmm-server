# SOP — Web UI & Dashboard Changes (Databento-First System)

**Last Updated:** 2025-01-02
**Purpose:** Standard Operating Procedure for all web UI and dashboard modifications

## MANDATORY TEMPLATE VERIFICATION

### Before Editing ANY Template

**ALWAYS verify which template a route actually serves:**

1. Check `web_server.py` for the route definition
2. Identify the exact template name in `render_template('...')`
3. Edit ONLY that template file
4. Add HTML fingerprint comment if not present:
   ```html
   <!-- SERVED_TEMPLATE: filename.html | version: YYYY-MM-DD -->
   ```

### Canonical Homepage

**Route:** `/homepage`
**Template:** `templates/homepage.html` (ONLY)
**Fingerprint:** `<!-- SERVED_TEMPLATE: homepage.html | version: 2025-01-02 -->`

**NEVER edit:**
- `templates/homepage_video_background.html` (deprecated)
- Any other homepage_*.html files

### Route-to-Template Mapping

**Before editing, verify in web_server.py:**
- `/automated-signals` → `templates/automated_signals_ultra.html`
- `/main-dashboard` → `templates/main_dashboard.html`
- `/time-analysis` → `templates/time_analysis.html`
- `/roadmap` → `templates/roadmap.html`

## DATA SOURCE REQUIREMENTS

### Canonical Data Endpoints

**For signal/trade data, use ONLY:**
- `/api/signals/v1/all` - Canonical signals endpoint
- `/api/roadmap` - Roadmap data

**NEVER use:**
- Legacy webhook endpoints
- Deprecated v2 endpoints
- Direct database queries in frontend

### Mandatory Filtering

**ALL analytics MUST filter:**
```javascript
// Stage 1: Valid market window only
const validSignals = allSignals.filter(s => s.valid_market_window === true);

// Stage 2: Metrics present (computable signals)
const computableSignals = validSignals.filter(s => 
    s.metrics_source === 'event' || s.metrics_source === 'computed'
);
```

**Why:** Excludes weekend/holiday artifacts and signals without metrics

## UI/UX PRINCIPLES

### Video Backgrounds

**Policy:** Remove or replace with static/lightweight assets

**Implementation:**
```html
<style>
body {
    background: linear-gradient(135deg, #0a1628 0%, #0d2240 50%, #0a1628 100%);
    background-attachment: fixed;
}
</style>
```

**NO video tags allowed on:**
- Homepage
- Login page
- Any dashboard

### Performance Requirements

- Page load: <2 seconds
- Minimize heavy visual effects
- Optimize asset loading
- Reduce JavaScript bundle size

### Clarity Requirements

- Clear visual hierarchy (primary vs secondary metrics)
- Standardized table spacing across all dashboards
- Consistent typography (font sizes and weights)
- Explicit system state cues (current phase, valid data only)

## ROADMAP CHANGES

### Single Source of Truth

**File:** `roadmap/unified_roadmap_v3.yaml`

**Structure:**
```yaml
phases:
  - phase_id: "PA"
    name: "Phase A — ..."
    objective: "..."
    status: "COMPLETE"
    deliverables:
      - "Bullet 1"
      - "Bullet 2"
    rules:  # Optional
      - "No X"
      - "No Y"
    description: "..."  # Optional
    modules: []
```

### Roadmap Loader

**File:** `roadmap/roadmap_loader.py`

**MUST include in phase snapshot:**
- `deliverables` (list from YAML)
- `rules` (list from YAML)
- `description` (string from YAML)
- All computed fields (modules_done, tasks_done, etc.)

### API Endpoint

**Endpoint:** `/api/roadmap`

**MUST return:**
```json
{
  "roadmap_v3": {
    "phases": [
      {
        "phase_id": "PA",
        "name": "...",
        "deliverables": [...],
        "rules": [...],
        "description": "...",
        ...
      }
    ]
  }
}
```

## DEPLOYMENT VERIFICATION

### Version Endpoint

**Endpoint:** `/api/version`

**Returns:**
- `git_commit`
- `build_time`
- `app_version`
- `roadmap_version`

**Usage:**
```powershell
Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version"
```

### Homepage Verification

**Check fingerprint:**
```powershell
$r = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/homepage" -UseBasicParsing
$r.Content | Select-String "SERVED_TEMPLATE"
```

**Check no video:**
```powershell
$r.Content -match '<video'  # Should be False
```

## COMMON MISTAKES TO AVOID

### ❌ DON'T

- Edit wrong template file (verify route first)
- Use video backgrounds
- Include fake/fallback data
- Filter out valid signals from analytics
- Create multiple homepage templates
- Use deprecated endpoints

### ✅ DO

- Verify template via route definition
- Add HTML fingerprint comments
- Use canonical data endpoints
- Filter invalid signals (valid_market_window)
- Use static gradient backgrounds
- Check `/api/version` after deployment

## TROUBLESHOOTING

### Template Not Updating

1. Verify correct template file being edited
2. Check route in `web_server.py`
3. Look for HTML fingerprint in served page
4. Check response headers (`X-Served-Template`)

### Data Not Showing

1. Verify endpoint URL is correct
2. Check browser console for errors
3. Verify filtering logic (valid_market_window)
4. Check API response shape matches code

### Deployment Not Working

1. Check `/api/version` for current version
2. Verify git commit and push succeeded
3. Check Railway build logs
4. Wait 2-3 minutes for deployment

## ENFORCEMENT

This SOP is loaded by the steering system and MUST be followed for all web UI and dashboard changes. Violations will result in wasted time, broken deployments, and user frustration.

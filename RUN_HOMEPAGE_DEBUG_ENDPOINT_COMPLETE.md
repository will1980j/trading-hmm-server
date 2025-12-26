# /api/debug/run-homepage Endpoint - Implementation Complete

## Summary

Added deterministic debug endpoint that executes the SAME logic as `/homepage` and returns detailed stage-by-stage results with any exceptions. This solves the problem where `/homepage` returns 500 in browser but `/api/debug/homepage-traceback` returns null.

## Problem Statement

- `/homepage` was returning 500 in browser
- `/api/debug/homepage-traceback` returned null (no error captured)
- Need deterministic way to test homepage logic and identify exact failure point

## Solution

Created `/api/debug/run-homepage` endpoint that:
1. Executes the same context-building logic as `/homepage`
2. Breaks execution into explicit stages
3. Returns JSON with stage-by-stage results
4. Captures exceptions at each stage with full traceback
5. Does NOT render template (separates logic from presentation)

## Implementation Details

### 1. Refactored Helper Function: `build_homepage_context()`

**Location:** `web_server.py` (after `get_databento_stats()`)

```python
def build_homepage_context():
    """
    Build all homepage context variables in explicit stages.
    Returns detailed stage-by-stage results for debugging.
    
    Returns:
        dict: {
            'success': bool,
            'stage': str (which stage failed, or 'complete'),
            'roadmap_v3': dict or None,
            'roadmap_v3_loaded': bool,
            'roadmap_v3_phase_count': int,
            'roadmap_error': str or None,
            'databento_stats': dict or None,
            'databento_stats_loaded': bool,
            'databento_row_count': int or None,
            'stats_error': str or None,
            'video_file': str,
            'error': str or None,
            'traceback': str or None
        }
    """
```

**Stages:**
1. **video_file** - Get random video file
2. **roadmap_v3** - Load roadmap from unified_roadmap_v3.yaml
3. **databento_stats** - Query Databento OHLCV data from database
4. **template_context** - Validate all context variables

Each stage is wrapped in try/except. If any stage fails, the function returns immediately with:
- `success: false`
- `stage: <failed_stage_name>`
- `error: <exception_message>`
- `traceback: <full_traceback>`

### 2. New Debug Endpoint: `/api/debug/run-homepage`

**Location:** `web_server.py` (after `/api/debug/homepage-traceback`)

```python
@app.route('/api/debug/run-homepage', methods=['GET'])
def debug_run_homepage():
    """
    Token-authenticated endpoint that executes homepage context building logic
    and returns detailed stage-by-stage results with any exceptions.
    
    This endpoint runs the SAME logic as /homepage but returns JSON instead of HTML,
    allowing deterministic debugging of homepage failures.
    
    Auth: X-Auth-Token header with value 'nQ-EXPORT-9f3a2c71a9e44d0c'
    """
```

**Authentication:**
- Same token pattern as other debug endpoints
- Token: `nQ-EXPORT-9f3a2c71a9e44d0c`
- Header: `X-Auth-Token`

**Response Format:**
```json
{
  "success": true,
  "stage": "complete",
  "roadmap_v3_loaded": true,
  "roadmap_v3_phase_count": 7,
  "roadmap_v3": {
    "version": "3.0.0",
    "phase_count": 7
  },
  "roadmap_error": null,
  "databento_stats_loaded": true,
  "databento_row_count": 150000,
  "databento_stats": {
    "row_count": 150000,
    "min_ts": "2024-01-01",
    "max_ts": "2024-12-26",
    "latest_close": 21234.50,
    "latest_ts": "2024-12-26 16:00"
  },
  "stats_error": null,
  "video_file": "homepage_video_1.mp4",
  "error": null,
  "traceback": null,
  "server_time_utc": "2025-12-26T12:34:56.789012+00:00"
}
```

**Failure Response Example:**
```json
{
  "success": false,
  "stage": "roadmap_v3",
  "roadmap_v3_loaded": false,
  "roadmap_v3_phase_count": 0,
  "roadmap_error": "FileNotFoundError: [Errno 2] No such file or directory: 'roadmap/unified_roadmap_v3.yaml'",
  "databento_stats_loaded": false,
  "databento_row_count": null,
  "video_file": "homepage_video_2.mp4",
  "error": "Stage 2 (roadmap_v3): FileNotFoundError: [Errno 2] No such file or directory: 'roadmap/unified_roadmap_v3.yaml'",
  "traceback": "Traceback (most recent call last):\n  File \"/app/web_server.py\", line 1850, in build_homepage_context\n    snapshot, error_str, resolved_path, exists, yaml_importable = build_v3_snapshot()\n  File \"/app/roadmap/roadmap_loader.py\", line 123, in build_v3_snapshot\n    with open(ROADMAP_V3_PATH, 'r') as f:\nFileNotFoundError: [Errno 2] No such file or directory: 'roadmap/unified_roadmap_v3.yaml'\n",
  "server_time_utc": "2025-12-26T12:34:56.789012+00:00"
}
```

### 3. Updated /homepage Route

**Location:** `web_server.py`

The `/homepage` route now uses `build_homepage_context()` instead of inline logic:

```python
@app.route('/homepage')
@login_required
def homepage():
    """Professional homepage - main landing page after login with nature videos"""
    global LAST_HOMEPAGE_ERROR
    
    try:
        # Build homepage context using refactored helper
        context = build_homepage_context()
        
        if not context['success']:
            # Context building failed - capture error and return safe response
            LAST_HOMEPAGE_ERROR = context.get('traceback') or context.get('error')
            logger.error(f"[HOMEPAGE_CONTEXT_FAILED] stage={context['stage']} error={context.get('error')}")
            
            return render_template('homepage_video_background.html', ...)
        
        # Clear any previous error on successful context build
        LAST_HOMEPAGE_ERROR = None
        
        # Render template with context
        return render_template('homepage_video_background.html', ...)
    
    except Exception as e:
        # FATAL ERROR HANDLER - Capture full traceback and return safe HTTP 200
        LAST_HOMEPAGE_ERROR = traceback.format_exc()
        logger.exception("[HOMEPAGE_FATAL] Unhandled exception in /homepage route")
        
        return render_template('homepage_video_background.html', ...)
```

**Benefits:**
- Same logic in both `/homepage` and `/api/debug/run-homepage`
- Easier to maintain (single source of truth)
- Better error capture and logging
- Cleaner code structure

## Usage

### PowerShell Command

```powershell
# Basic execution
Invoke-RestMethod -Method GET -Uri "https://web-production-f8c3.up.railway.app/api/debug/run-homepage" -Headers @{ "X-Auth-Token" = "nQ-EXPORT-9f3a2c71a9e44d0c" }

# With formatted output
Invoke-RestMethod -Method GET -Uri "https://web-production-f8c3.up.railway.app/api/debug/run-homepage" -Headers @{ "X-Auth-Token" = "nQ-EXPORT-9f3a2c71a9e44d0c" } | ConvertTo-Json -Depth 10
```

### Python Example

```python
import requests

headers = {"X-Auth-Token": "nQ-EXPORT-9f3a2c71a9e44d0c"}
response = requests.get(
    "https://web-production-f8c3.up.railway.app/api/debug/run-homepage",
    headers=headers
)

data = response.json()

if data['success']:
    print("✅ Homepage context built successfully")
    print(f"Roadmap phases: {data['roadmap_v3_phase_count']}")
    print(f"Databento rows: {data['databento_row_count']}")
else:
    print(f"❌ Failed at stage: {data['stage']}")
    print(f"Error: {data['error']}")
    print(f"\nTraceback:\n{data['traceback']}")
```

### cURL Example

```bash
curl -H "X-Auth-Token: nQ-EXPORT-9f3a2c71a9e44d0c" \
  https://web-production-f8c3.up.railway.app/api/debug/run-homepage | jq
```

## Testing

Run the test script:

```bash
python test_run_homepage_endpoint.py
```

**Test Coverage:**
1. ✅ Authentication required (401 without token)
2. ✅ Executes all homepage stages
3. ✅ Returns detailed results
4. ✅ Captures exceptions with traceback
5. ✅ Identifies exact failure stage

## Debugging Workflow

When `/homepage` returns 500:

1. **Check captured error:**
   ```powershell
   Invoke-RestMethod -Method GET -Uri "https://web-production-f8c3.up.railway.app/api/debug/homepage-traceback" -Headers @{ "X-Auth-Token" = "nQ-EXPORT-9f3a2c71a9e44d0c" }
   ```

2. **Run deterministic test:**
   ```powershell
   Invoke-RestMethod -Method GET -Uri "https://web-production-f8c3.up.railway.app/api/debug/run-homepage" -Headers @{ "X-Auth-Token" = "nQ-EXPORT-9f3a2c71a9e44d0c" }
   ```

3. **Analyze results:**
   - Check `success` field
   - If false, check `stage` to see where it failed
   - Read `error` for exception message
   - Read `traceback` for full stack trace with line numbers

4. **Fix the issue:**
   - Stage 1 (video_file): Check video file configuration
   - Stage 2 (roadmap_v3): Check roadmap YAML file exists and is valid
   - Stage 3 (databento_stats): Check database connection and table exists
   - Stage 4 (template_context): Check template variable validation

## Acceptance Criteria

✅ **All criteria met:**

1. ✅ Endpoint executes same logic as `/homepage`
   - Uses shared `build_homepage_context()` function
   - Both routes use identical context building

2. ✅ Returns JSON with stage-by-stage results
   - `success`: bool
   - `stage`: which stage failed or 'complete'
   - `roadmap_v3_loaded`: bool
   - `roadmap_v3_phase_count`: int
   - `databento_stats_loaded`: bool
   - `databento_row_count`: int or null
   - `error`: exception string or null
   - `traceback`: full traceback or null

3. ✅ Does NOT render template
   - Returns JSON only
   - Template rendering separated from logic

4. ✅ Captures exceptions at each stage
   - Stage 1: video_file
   - Stage 2: roadmap_v3
   - Stage 3: databento_stats
   - Stage 4: template_context

5. ✅ Returns exact failing code line
   - Full traceback with file paths and line numbers
   - Exception type and message
   - Stage identification

## Files Modified

- ✅ `web_server.py` - Added `build_homepage_context()`, `/api/debug/run-homepage`, refactored `/homepage`

## Files Created

- ✅ `test_run_homepage_endpoint.py` - Test script
- ✅ `RUN_HOMEPAGE_DEBUG_ENDPOINT_COMPLETE.md` - This document

## Code Snippets

### Helper Function: build_homepage_context()

```python
def build_homepage_context():
    """
    Build all homepage context variables in explicit stages.
    Returns detailed stage-by-stage results for debugging.
    """
    result = {
        'success': False,
        'stage': 'init',
        'roadmap_v3': None,
        'roadmap_v3_loaded': False,
        'roadmap_v3_phase_count': 0,
        'roadmap_error': None,
        'databento_stats': None,
        'databento_stats_loaded': False,
        'databento_row_count': None,
        'stats_error': None,
        'video_file': None,
        'error': None,
        'traceback': None
    }
    
    # STAGE 1: Get video file
    try:
        result['stage'] = 'video_file'
        result['video_file'] = get_random_video('homepage')
    except Exception as e:
        result['error'] = f"Stage 1 (video_file): {type(e).__name__}: {e}"
        result['traceback'] = traceback.format_exc()
        return result
    
    # STAGE 2: Load roadmap V3
    try:
        result['stage'] = 'roadmap_v3'
        snapshot, error_str, resolved_path, exists, yaml_importable = build_v3_snapshot()
        
        if snapshot:
            result['roadmap_v3'] = snapshot
            result['roadmap_v3_loaded'] = True
            result['roadmap_v3_phase_count'] = len(snapshot.get('phases', []))
        else:
            result['roadmap_error'] = error_str or "Unknown error loading roadmap"
            result['roadmap_v3'] = get_homepage_roadmap_data()
            result['roadmap_v3_loaded'] = False
            result['roadmap_v3_phase_count'] = len(result['roadmap_v3'].get('phases', [])) if result['roadmap_v3'] else 0
            
    except Exception as e:
        result['roadmap_error'] = f"{type(e).__name__}: {e}\nTraceback: {traceback.format_exc()}"
        result['error'] = f"Stage 2 (roadmap_v3): {type(e).__name__}: {e}"
        result['traceback'] = traceback.format_exc()
        return result
    
    # STAGE 3: Fetch Databento stats
    try:
        result['stage'] = 'databento_stats'
        databento_stats, stats_error = get_databento_stats()
        
        result['databento_stats'] = databento_stats
        result['stats_error'] = stats_error
        
        if databento_stats:
            result['databento_stats_loaded'] = True
            result['databento_row_count'] = databento_stats.get('row_count')
            
    except Exception as e:
        result['stats_error'] = f"{type(e).__name__}: {e}"
        result['error'] = f"Stage 3 (databento_stats): {type(e).__name__}: {e}"
        result['traceback'] = traceback.format_exc()
        return result
    
    # STAGE 4: Prepare template context
    try:
        result['stage'] = 'template_context'
        
        # Validate all required context variables exist
        context = {
            'video_file': result['video_file'],
            'roadmap_v3': result['roadmap_v3'],
            'roadmap_snapshot': result['roadmap_v3'],
            'databento_stats': result['databento_stats'],
            'roadmap_error': result['roadmap_error'],
            'roadmap_v3_error': result['roadmap_error'],
            'stats_error': result['stats_error']
        }
        
        if context['video_file'] is None:
            raise ValueError("video_file is None")
        
    except Exception as e:
        result['error'] = f"Stage 4 (template_context): {type(e).__name__}: {e}"
        result['traceback'] = traceback.format_exc()
        return result
    
    # All stages complete
    result['stage'] = 'complete'
    result['success'] = True
    return result
```

### Debug Endpoint: /api/debug/run-homepage

```python
@app.route('/api/debug/run-homepage', methods=['GET'])
def debug_run_homepage():
    """
    Token-authenticated endpoint that executes homepage context building logic
    and returns detailed stage-by-stage results with any exceptions.
    """
    # Token authentication
    expected_token = "nQ-EXPORT-9f3a2c71a9e44d0c"
    header_token = request.headers.get('X-Auth-Token')
    
    if header_token != expected_token:
        return jsonify({
            'success': False,
            'error': 'Unauthorized - provide X-Auth-Token header'
        }), 401
    
    from datetime import datetime, timezone
    
    # Execute homepage context building
    result = build_homepage_context()
    
    # Add server timestamp
    result['server_time_utc'] = datetime.now(timezone.utc).isoformat()
    
    # Remove large objects from response (keep only metadata)
    if result.get('roadmap_v3'):
        result['roadmap_v3'] = {
            'version': result['roadmap_v3'].get('version'),
            'phase_count': len(result['roadmap_v3'].get('phases', []))
        }
    
    return jsonify(result), 200
```

## Deployment

Ready to deploy via GitHub Desktop:

1. Stage changes in `web_server.py`
2. Commit: "Add /api/debug/run-homepage endpoint for deterministic homepage debugging"
3. Push to main branch
4. Railway auto-deploys within 2-3 minutes
5. Test with PowerShell command above

---

**Status:** ✅ COMPLETE - Ready to deploy

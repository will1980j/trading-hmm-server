# Version Endpoint for Deployment Verification - COMPLETE

**Date:** 2025-01-02
**Purpose:** Permanent endpoint to verify deployments deterministically

## Implementation

### Endpoint Added: GET /api/version

**File:** `web_server.py` (after /api/health endpoint)

**Route Code:**
```python
@app.route('/api/version')
def api_version():
    """
    Permanent version endpoint for deterministic deployment verification.
    
    Returns:
        - git_commit: Git commit hash (from env var or "unknown")
        - build_time: Hardcoded build timestamp
        - app_version: Application version string
        - roadmap_version: Roadmap version from YAML
    
    Usage:
        Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version"
    """
    import os
    
    # Git commit from environment variable (Railway sets this)
    git_commit = os.environ.get('RAILWAY_GIT_COMMIT_SHA', 
                                os.environ.get('GIT_COMMIT', 'unknown'))
    
    # Build time - hardcoded at patch time
    build_time = "2025-01-02 23:30 UTC"
    
    # App version - semantic version for this deployment
    app_version = "homepage-hardening-2025-01-02"
    
    # Roadmap version - read from YAML
    roadmap_version = "unknown"
    try:
        from roadmap.roadmap_loader import load_roadmap_v3
        roadmap_data = load_roadmap_v3()
        roadmap_version = roadmap_data.get('roadmap_version', 'unknown')
    except Exception as e:
        logger.warning(f"[VERSION] Failed to load roadmap version: {e}")
    
    response_data = {
        'git_commit': git_commit[:8] if len(git_commit) > 8 else git_commit,
        'build_time': build_time,
        'app_version': app_version,
        'roadmap_version': roadmap_version,
        'timestamp': datetime.now().isoformat()
    }
    
    response = jsonify(response_data)
    response.headers['X-App-Version'] = app_version
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response
```

## Response Format

**JSON Body:**
```json
{
  "git_commit": "a1b2c3d4",
  "build_time": "2025-01-02 23:30 UTC",
  "app_version": "homepage-hardening-2025-01-02",
  "roadmap_version": "3.0.2",
  "timestamp": "2025-01-02T23:30:00.123456"
}
```

**Response Headers:**
```
X-App-Version: homepage-hardening-2025-01-02
Cache-Control: no-cache, no-store, must-revalidate
Access-Control-Allow-Origin: *
```

## Usage

### Quick Version Check (PowerShell):
```powershell
Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version"
```

### Check Specific Field:
```powershell
$v = Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version"
$v.app_version
```

### Check Response Header:
```powershell
$r = Invoke-WebRequest -Uri "https://web-production-f8c3.up.railway.app/api/version" -UseBasicParsing
$r.Headers['X-App-Version']
```

### Verify Deployment Changed:
```powershell
# Before deploy
$before = Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version"
Write-Host "Before: $($before.app_version)"

# ... deploy via GitHub Desktop ...

# After deploy (wait 2-3 minutes)
$after = Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version"
Write-Host "After: $($after.app_version)"

if ($before.app_version -ne $after.app_version) {
    Write-Host "✅ DEPLOYMENT VERIFIED - Version changed" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING - Version unchanged" -ForegroundColor Yellow
}
```

## Benefits

### Deterministic Verification
- **Before:** Guess if deployment worked by checking features
- **After:** Call /api/version and see exact build time/version

### Deployment Tracking
- **Git Commit:** Shows which commit is deployed
- **Build Time:** Shows when code was built
- **App Version:** Semantic version for this deployment
- **Roadmap Version:** Shows roadmap state

### Debugging
- **Production Issues:** Check version first
- **Stale Code:** Instantly see if old version is running
- **Cache Issues:** Verify version changed after deploy

### Future Deployments
- **Update build_time** on each significant deployment
- **Update app_version** with descriptive name
- **Check /api/version** after every deploy to confirm

## Files Changed

1. `web_server.py` - Added /api/version endpoint

## Test Script

**File:** `test_version_endpoint.py`

**Usage:**
```powershell
python test_version_endpoint.py
```

**Tests:**
- Local endpoint (localhost:5000)
- Production endpoint (Railway)
- Compares versions
- Shows if deployment is current

## Deployment Workflow

**Step 1: Make Changes**
- Edit code files
- Update build_time in /api/version
- Update app_version with descriptive name

**Step 2: Commit & Push**
```
GitHub Desktop:
1. Stage all changes
2. Commit with message
3. Push to main branch
```

**Step 3: Verify Deployment**
```powershell
# Wait 2-3 minutes for Railway deploy
python test_version_endpoint.py

# Or quick check:
Invoke-RestMethod "https://web-production-f8c3.up.railway.app/api/version" | Select app_version, build_time
```

**Step 4: Confirm Version Changed**
```
Expected:
  app_version: homepage-hardening-2025-01-02
  build_time: 2025-01-02 23:30 UTC
```

## Summary

Added permanent /api/version endpoint for deterministic deployment verification:

**Endpoint:** `GET /api/version`

**Returns:**
- git_commit (from Railway env var)
- build_time (hardcoded: 2025-01-02 23:30 UTC)
- app_version (homepage-hardening-2025-01-02)
- roadmap_version (from YAML: 3.0.2)

**Response Header:** `X-App-Version: homepage-hardening-2025-01-02`

**Usage:** Call after each deployment to verify version changed

**File Changed:** web_server.py

This endpoint provides permanent, deterministic verification that deployments are actually running new code.

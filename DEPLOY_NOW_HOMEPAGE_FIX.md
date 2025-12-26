# Deploy Homepage Fix NOW

## Current Status

✅ Code changes complete and ready in working directory
❌ Not yet deployed to Railway (that's why you're seeing 500)

## What's Ready

1. ✅ `web_server.py` - Homepage route rolled back to working state + V3 roadmap added
2. ✅ `templates/homepage_video_background.html` - Restored template + V3 block inserted

## Deploy Steps (GitHub Desktop)

### 1. Open GitHub Desktop

### 2. Review Changes

You should see:
- Modified: `web_server.py`
- Modified: `templates/homepage_video_background.html`

### 3. Commit

**Commit message:**
```
Surgical rollback: restore homepage to working state + add V3 roadmap
```

**Description:**
```
- Rolled back /homepage route to commit a866c09 (last working state)
- Added V3 roadmap loading with safe try/except (never raises)
- Restored template from commit a866c09
- Inserted V3 roadmap block with safe dict access
- No new endpoints, no refactors, no feature flags
```

### 4. Push to Main

Click "Push origin" button

### 5. Wait for Railway Deployment

- Railway will auto-deploy within 2-3 minutes
- Monitor deployment in Railway dashboard

### 6. Test

Once deployed, test:
```
https://web-production-f8c3.up.railway.app/homepage
```

Should show:
- ✅ No 500 error
- ✅ Blue box with "Unified Roadmap v3 (3.0.0)"
- ✅ List of phases with percentages
- ✅ Legacy roadmap below

## Why 500 Error Now?

The 500 error you're seeing is because:
- Changes are in your local working directory
- But NOT yet deployed to Railway
- Railway is still running the old broken code

**Solution:** Commit and push to deploy the fix!

---

**Ready to deploy!** Just commit and push in GitHub Desktop.

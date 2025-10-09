# Pre-Deploy Checklist ✅

## Before You Deploy

### 1. Verify Local Files
```bash
# Check files exist
dir unified_ml_intelligence.py
dir ml_intelligence_dashboard.html
dir web_server.py
```

**Expected:** All files should exist

### 2. Test ML Locally (Optional)
```bash
python test_ml_local.py
```

**Expected:** All tests pass ✅

### 3. Check Git Status
```bash
git status
```

**Expected:** New files shown as untracked

### 4. Verify Railway Connection
```bash
git remote -v
```

**Expected:** Shows Railway remote

## Deploy Commands

### Automatic (Windows)
```bash
deploy_ml_to_railway.bat
```

### Manual
```bash
git add unified_ml_intelligence.py
git add ml_intelligence_dashboard.html
git add web_server.py
git add ML_INTELLIGENCE_SOLUTION.md
git add RAILWAY_ML_DEPLOYMENT.md
git add ML_QUICK_START.md
git add test_ml_local.py
git add check_railway_ml.py
git add deploy_ml_to_railway.bat
git add DEPLOY_NOW.md
git add ML_SYSTEM_OVERVIEW.txt
git add PRE_DEPLOY_CHECKLIST.md

git commit -m "Deploy unified ML intelligence system"
git push origin main
```

## After Deploy

### 1. Wait for Railway (~2 min)
Check Railway dashboard for:
- ✅ Build successful
- ✅ Deploy successful
- ✅ Service running

### 2. Check Logs
Railway logs should show:
```
✅ ML dependencies available
✅ Database connected successfully
✅ Unified ML Intelligence System loaded
```

### 3. Visit ML Dashboard
```
https://[your-app].railway.app/ml-dashboard
```

**Expected:** Dashboard loads, shows "Not Trained" initially

### 4. Train ML
Click: "Train ML Models" button

**Expected:** 
- Training completes in 10-30 seconds
- Status changes to "Trained" ✅
- Shows 300+ training samples
- Displays insights

### 5. Verify Live Predictions
Send a test signal from TradingView

**Expected:** Railway logs show:
```
🤖 ML: Strength=X%, MFE=X.XXR, Success=X.X%, Rec=TAKE/SKIP
```

## Troubleshooting

### If Build Fails
- Check Railway logs for errors
- Verify requirements.txt has ML dependencies
- Check Python version (3.9+)

### If ML Doesn't Train
- Verify database has 20+ trades with MFE data
- Check Railway logs for specific error
- Try manual train via API: `POST /api/ml-train`

### If Dashboard Shows Error
- Check database connection in Railway
- Verify web_server.py deployed correctly
- Review Railway logs for Python errors

## Success Criteria

✅ Railway build successful
✅ ML dashboard loads
✅ ML trains successfully (300+ samples)
✅ Insights displayed
✅ Live signals get ML predictions
✅ Logs show ML working

## Ready to Deploy?

If all checks pass, run:
```bash
deploy_ml_to_railway.bat
```

Or manually:
```bash
git add .
git commit -m "Deploy unified ML intelligence"
git push origin main
```

Then visit: `https://[your-app].railway.app/ml-dashboard`

## Need Help?

Check these files:
- `ML_QUICK_START.md` - Quick reference
- `RAILWAY_ML_DEPLOYMENT.md` - Detailed guide
- `ML_INTELLIGENCE_SOLUTION.md` - Full documentation
- `ML_SYSTEM_OVERVIEW.txt` - Visual overview

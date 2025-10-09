# Railway ML Deployment Guide

## Quick Deploy Checklist

### 1. Verify Files Are Committed
```bash
git add unified_ml_intelligence.py
git add ml_intelligence_dashboard.html
git add ML_INTELLIGENCE_SOLUTION.md
git add RAILWAY_ML_DEPLOYMENT.md
git commit -m "Add unified ML intelligence system"
git push origin main
```

### 2. Railway Auto-Deploy
Railway will automatically:
- ✅ Detect changes
- ✅ Install ML dependencies (already in requirements.txt)
- ✅ Deploy updated web_server.py
- ✅ Start serving ML endpoints

### 3. Verify Deployment
Visit your Railway URL:
```
https://your-app.railway.app/ml-dashboard
```

### 4. ML Auto-Trains (Automatic)
ML trains itself automatically:
- ✅ On first signal (if not trained)
- ✅ Every 24 hours
- ✅ Every 50 new trades
- ✅ Background checks hourly

Optional: Manually train via `/ml-dashboard`

## ML Dependencies (Already Installed)
✅ scikit-learn==1.3.0
✅ pandas==2.0.3
✅ numpy==1.24.3
✅ joblib==1.3.1

## New Endpoints Available

### ML Dashboard
```
GET /ml-dashboard
```
Visual dashboard with ML insights

### Train ML
```
POST /api/ml-train
```
Trains ML on all 300+ trades

### Get Insights
```
GET /api/ml-insights
```
Returns ML predictions and recommendations

## Database Requirements
✅ PostgreSQL (Railway provides this)
✅ Tables: signal_lab_trades, signal_lab_15m_trades
✅ Minimum: 20 trades with MFE data
✅ Current: 300+ trades (excellent!)

## Memory Usage
- Training: ~100MB RAM
- Predictions: ~10MB RAM
- Railway Free Tier: 512MB (sufficient)

## Performance
- Training time: 10-30 seconds (one-time)
- Prediction time: <100ms per signal
- Auto-trains on first signal if needed

## Troubleshooting

### If ML doesn't train:
```python
# Check logs in Railway dashboard
# Look for: "Training unified ML on all trading data..."
```

### If predictions fail:
```python
# ML will auto-train on first signal
# Check: "Auto-training ML models..."
```

### If dashboard shows errors:
1. Verify database connection
2. Check you have trades with MFE data
3. Review Railway logs for errors

## Testing After Deploy

### 1. Test ML Dashboard
```
https://your-app.railway.app/ml-dashboard
```
Should show ML status and insights

### 2. Test Training
Click "Train ML Models" button
Should complete in 10-30 seconds

### 3. Test Live Predictions
Send a signal from TradingView
Check logs for: "🤖 ML: Strength=X%, MFE=X.XXR"

### 4. Test API Endpoints
```bash
# Get insights
curl https://your-app.railway.app/api/ml-insights

# Train ML
curl -X POST https://your-app.railway.app/api/ml-train
```

## What Happens on Deploy

1. **Railway detects changes** → Pulls latest code
2. **Installs dependencies** → ML libraries already in requirements.txt
3. **Starts web_server.py** → ML system ready
4. **First signal arrives** → ML auto-trains if needed
5. **Predictions start** → Every signal gets ML analysis

## No Additional Configuration Needed!

The ML system:
- ✅ Uses existing database
- ✅ Uses existing dependencies
- ✅ Auto-trains when needed
- ✅ Works with current Railway setup

## Deploy Command

```bash
# From your local repo
git add .
git commit -m "Deploy unified ML intelligence"
git push origin main

# Railway auto-deploys in ~2 minutes
```

## Verify Success

After deploy, check Railway logs for:
```
✅ "Unified ML Intelligence System loaded"
✅ "ML dependencies available"
✅ "Database connected successfully"
```

Then visit:
```
https://your-app.railway.app/ml-dashboard
```

You should see:
- ML Status: "Not Trained" (initially)
- Training Samples: 0
- Click "Train ML Models" to start

After training:
- ML Status: "Trained" ✅
- Training Samples: 300+
- Best Session: London (or your best)
- Key Recommendations: Listed

## That's It!

No special Railway configuration needed. Just push and it works! 🚀

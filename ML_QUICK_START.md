# ML Intelligence - Quick Start

## Deploy to Railway (3 Steps)

### Option A: Automatic (Windows)
```bash
deploy_ml_to_railway.bat
```

### Option B: Manual
```bash
# 1. Test locally
python test_ml_local.py

# 2. Deploy
git add .
git commit -m "Deploy ML intelligence"
git push origin main
```

## After Deploy

### 1. Open ML Dashboard
```
https://your-railway-app.railway.app/ml-dashboard
```

### 2. Train ML
Click: **"Train ML Models"** button

Wait: ~30 seconds

### 3. View Results
- ✅ ML Status: Trained
- ✅ Training Samples: 300+
- ✅ Best Session: [Your best session]
- ✅ Key Recommendations: [Listed]

## What You Get

### Real-Time Predictions
Every TradingView signal gets:
- **Strength**: ML confidence (0-100%)
- **Predicted MFE**: How far it will go
- **Recommendation**: TAKE/SKIP/CONSIDER

### Fundamental Insights
- 🎯 Best sessions to trade
- 📊 Best signal types
- 🎯 Optimal R-targets
- 📈 Bias performance
- 📰 News impact

### API Endpoints
```
GET  /ml-dashboard          # Visual dashboard
GET  /api/ml-insights       # JSON insights
POST /api/ml-train          # Train models
```

## Verify It's Working

### Check Logs
Railway logs should show:
```
✅ ML dependencies available
✅ Database connected
✅ Unified ML Intelligence System loaded
```

### Check Live Signals
When signal arrives, logs show:
```
🤖 ML: Strength=68%, MFE=1.85R, Success=68.5%, Rec=TAKE
```

### Check Dashboard
Visit `/ml-dashboard`:
- Status: "Trained" (green)
- Samples: 300+
- Recommendations: Listed

## Troubleshooting

### ML Not Training?
- Check: Database has 20+ trades with MFE data
- Check: Railway logs for errors
- Try: Manual train via API

### No Predictions?
- ML auto-trains on first signal
- Wait: 30 seconds for training
- Check: Logs for "Training unified ML..."

### Dashboard Error?
- Verify: Railway deployment successful
- Check: Database connection
- Review: Railway logs

## That's It!

ML is now learning from your 300+ trades and helping you make better trading decisions! 🚀

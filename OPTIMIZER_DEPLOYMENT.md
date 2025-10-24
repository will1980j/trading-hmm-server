# Hyperparameter Optimizer - Deployment Guide

## What Was Fixed

### 1. Auto-Optimizer Improvements
- **Immediate startup check**: Now checks conditions immediately when server starts (not after 1 hour)
- **Better logging**: Shows exactly why optimization runs or doesn't run
- **Sample count tracking**: Logs current sample count on every check
- **Robust error handling**: Won't crash if database has issues

### 2. Manual Trigger Improvements
- **Sample count validation**: Checks if enough samples before running
- **Better error messages**: Shows exactly what went wrong
- **Detailed results**: Returns optimized parameters in response

### 3. New Tools Created
- `force_optimize.py`: Standalone script to force optimization immediately
- `check_optimizer_status.py`: Diagnostic script to see current state

## How It Works Now

### Auto-Optimizer (Runs on Server)
1. **On Server Startup**: Checks immediately if conditions are met
2. **Hourly Checks**: Continues checking every hour
3. **Triggers**:
   - First run: 500+ samples
   - Subsequent runs: 200+ new samples OR 30 days since last run

### Current Status (Based on Your Data)
- **Samples Available**: 2000+ ✅
- **First Run Threshold**: 500 ✅
- **Should Run**: YES - conditions are met!

## Why It Wasn't Running Before

The auto-optimizer was waiting for the first hourly check cycle. Now it checks immediately on startup.

## Deployment Steps

### Option 1: Restart Server (Recommended)
```bash
# On Railway, trigger a redeploy or restart
# The optimizer will check immediately on startup
```

### Option 2: Manual Trigger via API
```bash
# Call the API endpoint
POST https://your-server.railway.app/api/trigger-hyperparameter-optimization
```

### Option 3: Run Force Script on Server
```bash
# SSH into Railway or use Railway CLI
python force_optimize.py
```

## Verification

After deployment, check the logs for:
```
🚀 First run - checking optimization conditions immediately
📊 Sample check: 2000+ samples available
🔧 TRIGGER: First optimization with 2000+ samples (threshold: 500)
🚀 Starting automatic hyperparameter optimization...
```

## Expected Results

With 2000+ samples, you should see:
- **RF Improvement**: +2-5% accuracy
- **GB Improvement**: +2-5% accuracy
- **Duration**: 5-15 minutes (depending on server resources)
- **Best Parameters**: Stored in database and visible in ML Dashboard

## Monitoring

### Check Status via API
```bash
GET https://your-server.railway.app/api/hyperparameter-status
```

### Check Logs
Look for these log messages:
- `✅ Auto-optimizer started (checks hourly)`
- `🔧 TRIGGER: First optimization with X samples`
- `✅ Optimization complete: RF +X%, GB +Y%`

## Troubleshooting

### If Optimization Doesn't Run
1. Check sample count: `SELECT COUNT(*) FROM signal_lab_trades WHERE mfe_none != 0`
2. Check logs for error messages
3. Manually trigger via API endpoint
4. Run `force_optimize.py` directly on server

### If Optimization Fails
- Check logs for specific error
- Verify ML dependencies are installed (sklearn, pandas, numpy, xgboost)
- Ensure database has enough resources
- Check if samples have valid data (not all zeros)

## Next Steps

1. **Deploy**: Push changes to Railway
2. **Restart**: Trigger server restart
3. **Monitor**: Watch logs for optimization run
4. **Verify**: Check ML Dashboard for results
5. **Enjoy**: Optimized ML models will improve predictions!

## Files Modified
- `ml_auto_optimizer.py`: Improved startup logic and logging
- `web_server.py`: Enhanced manual trigger endpoint
- `force_optimize.py`: NEW - Force optimization script
- `check_optimizer_status.py`: NEW - Diagnostic script

## Configuration
- Check interval: 3600 seconds (1 hour)
- First run: 500+ samples
- Subsequent runs: 200+ new samples OR 30 days
- Runs automatically on server startup if conditions met

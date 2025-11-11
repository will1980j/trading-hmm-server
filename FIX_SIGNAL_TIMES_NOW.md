# Fix Signal Times - IMMEDIATE ACTION REQUIRED

## The Problem

Old database records don't have `signal_date` and `signal_time` columns, so they show webhook receipt time instead of signal candle time.

## The Solution - 3 Steps

### Step 1: Add Columns to Railway Database

**Option A: Via Railway Dashboard (Easiest)**
1. Go to Railway dashboard
2. Click on your PostgreSQL database
3. Click "Query" tab
4. Run this SQL:
```sql
ALTER TABLE automated_signals 
ADD COLUMN IF NOT EXISTS signal_date DATE,
ADD COLUMN IF NOT EXISTS signal_time TIME;
```
5. Click "Run Query"

**Option B: Via Python Script**
1. Get your DATABASE_URL from Railway dashboard
2. In PowerShell:
```powershell
$env:DATABASE_URL = "postgresql://user:pass@host:port/db"
python add_signal_time_columns.py
```

### Step 2: Deploy Updated Code

The code is already updated in your local files. Just deploy:

1. Open GitHub Desktop
2. Commit changes: "Add signal_date and signal_time columns"
3. Push to main branch
4. Wait 2-3 minutes for Railway auto-deploy

### Step 3: Test with New Signal

1. Send a test signal from TradingView strategy
2. Check dashboard - new signal should show correct signal candle time
3. Old signals will still show wrong time (NULL columns fall back to timestamp)

## What Gets Fixed

✅ **New signals** - Show correct signal candle time
❌ **Old signals** - Still show wrong time (can't retroactively fix)

## Quick Fix for Old Signals

If you want to clean up old signals:

**Option 1: Delete all old signals**
```sql
DELETE FROM automated_signals WHERE signal_date IS NULL;
```

**Option 2: Leave them** - They'll eventually age out as new signals come in

## Verification

After deploying, check the dashboard:
- New signals should show time when triangle appeared
- Old signals will show time when webhook was received (or NULL)

## Status

- ✅ Pine Script sends correct time
- ✅ Web server stores correct time  
- ✅ API returns correct time
- ✅ Dashboard displays correct time
- ⏳ **DATABASE NEEDS COLUMN MIGRATION** ← DO THIS NOW

**Run the SQL migration in Railway dashboard, then deploy!**

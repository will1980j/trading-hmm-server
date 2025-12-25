# 🔧 FIX: Homepage Databento Stats Not Working

**Issue:** Databento stats not displaying on homepage  
**Likely Cause:** Table doesn't exist on Railway database

---

## 🔍 DIAGNOSIS STEPS

### Step 1: Check if table exists on Railway

```bash
# Run diagnostic script
python debug_homepage_databento_stats.py
```

**Expected output if working:**
```
✅ Table 'market_bars_ohlcv_1m' exists
✅ Table has 2,338,262 rows
✅ CME_MINI:MNQ1! has 2,338,262 rows
```

**If table doesn't exist:**
```
❌ Table 'market_bars_ohlcv_1m' does NOT exist
```

---

## ✅ SOLUTION

### Option 1: Run Migration on Railway (RECOMMENDED)

The table needs to be created on the Railway database:

```bash
# 1. Ensure DATABASE_URL points to Railway
echo $DATABASE_URL

# 2. Run migration
python database/run_databento_migration.py
```

**Expected output:**
```
🚀 Running Databento OHLCV schema migration...
   SQL file: /path/to/database/databento_ohlcv_schema.sql
   SQL file size: 4,567 bytes
   Statements to execute: 12
   Database: railway.app
   ✅ Statement 1/12 executed
   ...
   ✅ Statement 12/12 executed

✅ Transaction committed successfully

✅ Migration completed successfully!
   Tables created: 2
   - data_ingest_runs
   - market_bars_ohlcv_1m
```

---

### Option 2: Check Railway Logs

If migration was already run, check Railway logs for errors:

1. Go to Railway dashboard
2. Select your project
3. Click "Deployments"
4. View logs for errors related to `market_bars_ohlcv_1m`

---

### Option 3: Verify DATABASE_URL

The local `.env` DATABASE_URL might be different from Railway's:

```bash
# Check local DATABASE_URL
cat .env | grep DATABASE_URL

# Compare with Railway
# (Check Railway dashboard > Variables > DATABASE_URL)
```

**Common issue:** Local DATABASE_URL points to a different database than Railway

---

## 🧪 TEST AFTER FIX

### Test 1: Run diagnostic script

```bash
python debug_homepage_databento_stats.py
```

Should show:
```
✅ Table 'market_bars_ohlcv_1m' exists
✅ Table has 2,338,262 rows
✅ Query executed
✅ Stats would display correctly on homepage
```

---

### Test 2: Check homepage

```bash
# Visit homepage
https://web-production-f8c3.up.railway.app/homepage

# Expand Phase 0.5
# Should see:
📊 Live Dataset Stats
Bars:    2,338,262
Range:   2019-05-05 → 2025-12-22
Latest:  2025-12-22 23:59 @ $25,930.50
```

---

## 🚨 COMMON ISSUES

### Issue 1: Table doesn't exist on Railway

**Cause:** Migration not run on Railway database  
**Fix:** Run `python database/run_databento_migration.py` with Railway DATABASE_URL

---

### Issue 2: Wrong DATABASE_URL

**Cause:** Local DATABASE_URL different from Railway  
**Fix:** 
1. Get Railway DATABASE_URL from dashboard
2. Update `.env` file
3. Re-run migration

---

### Issue 3: Data not ingested on Railway

**Cause:** Data ingested locally but not on Railway  
**Fix:** 
1. Verify table exists: `python debug_homepage_databento_stats.py`
2. If table empty, re-run ingestion pointing to Railway database

---

### Issue 4: Homepage code not deployed

**Cause:** Changes not pushed to Railway  
**Fix:**
```bash
# Commit and push
git add web_server.py templates/homepage_video_background.html roadmap_state.py
git commit -m "fix: Add Databento stats to homepage"
git push origin main

# Wait for Railway auto-deploy (2-3 minutes)
```

---

## 📝 QUICK FIX CHECKLIST

- [ ] Run `python debug_homepage_databento_stats.py`
- [ ] If table missing: Run `python database/run_databento_migration.py`
- [ ] Verify table has data (2.3M+ rows)
- [ ] Check Railway logs for errors
- [ ] Verify DATABASE_URL matches Railway
- [ ] Test homepage displays stats
- [ ] If still broken: Check Railway deployment logs

---

## 🔧 EMERGENCY FIX

If stats still don't show, the homepage will gracefully degrade:

**Current behavior:**
- If query fails → Shows "Live stats unavailable"
- Page still loads normally
- Roadmap checklist still visible
- No errors or broken UI

**This is by design** - the page won't break even if stats fail.

---

## 📊 EXPECTED FINAL STATE

**Homepage Phase 0.5 should show:**

```
┌─────────────────────────────────────────────────────────────┐
│ 0.5  Databento Foundation (Phase 0–1A)  (5 modules • 80%)  │
├─────────────────────────────────────────────────────────────┤
│ Source of truth: Databento OHLCV-1m. TradingView:          │
│ charting only. Dataset: 2019-05-05 → 2025-12-22            │
│ (~2.34M bars).                                              │
│                                                              │
│ ✅ Databento Dataset Downloaded (Mnq Ohlcv-1M)             │
│ ✅ Db Schema Migrated (Market Bars Ohlcv 1M + Data...)     │
│ ✅ Ingestion Complete (2019–2025) — 2.34M Bars             │
│ ✅ Stats Endpoint Live (/Api/Market-Data/Mnq/Ohlcv-1M...)  │
│ ⬜ Backfill Optional (2010–2019)                            │
│                                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📊 Live Dataset Stats                                   │ │
│ │ Bars:    2,338,262                                      │ │
│ │ Range:   2019-05-05 → 2025-12-22                       │ │
│ │ Latest:  2025-12-22 23:59 @ $25,930.50                 │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🆘 NEED HELP?

Run the diagnostic script and share the output:

```bash
python debug_homepage_databento_stats.py > debug_output.txt
cat debug_output.txt
```

This will show exactly what's wrong.

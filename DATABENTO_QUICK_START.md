# 🚀 Databento Ingestion - Quick Start

**5-Minute Setup Guide for Phase 1A**

---

## ⚡ Prerequisites

```bash
# 1. Ensure dependencies installed
pip install databento zstandard pandas psycopg2-binary python-dotenv

# 2. Set DATABASE_URL in .env
echo "DATABASE_URL=postgresql://user:pass@host:port/dbname" > .env
```

---

## 📋 Step 1: Run Migration (One-Time)

```bash
python database/run_databento_migration.py
```

**Expected Output:**
```
✅ Migration completed successfully!
   Tables created: 2
   - data_ingest_runs
   - market_bars_ohlcv_1m
```

---

## 🧪 Step 2: Test Ingestion (Dry Run)

```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/mnq/ohlcv_1m/raw/YOUR_FILE.dbn.zst \
    --dry-run \
    --verbose
```

**Expected Output:**
```
✅ DRY RUN COMPLETE - No database changes made
Would process: 50,000 bars
Time range: 2024-01-01 00:00:00+00:00 to 2024-01-15 23:59:00+00:00
```

---

## 💾 Step 3: Ingest Data (Production)

```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/mnq/ohlcv_1m/raw/YOUR_FILE.dbn.zst
```

**Expected Output:**
```
✅ INGESTION COMPLETE
Run ID: 1
Total bars: 50,000
Inserted: 50,000
Updated: 0
```

---

## ✅ Step 4: Verify Ingestion

### Option A: API Endpoint
```bash
curl http://localhost:5000/api/market-data/mnq/ohlcv-1m/stats
```

### Option B: Database Query
```sql
SELECT COUNT(*), MIN(ts), MAX(ts) 
FROM market_bars_ohlcv_1m;
```

### Option C: Test Script
```bash
python test_databento_ingestion.py
```

---

## 🔄 Re-Running (Idempotent)

Safe to run multiple times - no duplicates created:

```bash
# First run
python scripts/ingest_databento_ohlcv_1m.py --input file.dbn.zst
# Output: Inserted: 50,000 | Updated: 0

# Second run (same file)
python scripts/ingest_databento_ohlcv_1m.py --input file.dbn.zst
# Output: Inserted: 0 | Updated: 50,000
```

---

## 🚨 Troubleshooting

### Error: "DATABASE_URL not found"
```bash
# Check .env file exists
cat .env

# Set DATABASE_URL
echo "DATABASE_URL=postgresql://..." > .env
```

### Error: "Input file not found"
```bash
# Verify file path
ls -lh data/databento/mnq/ohlcv_1m/raw/

# Use absolute path
python scripts/ingest_databento_ohlcv_1m.py \
    --input /full/path/to/file.dbn.zst
```

### Error: "Validation failed"
```bash
# Run with verbose logging
python scripts/ingest_databento_ohlcv_1m.py \
    --input file.dbn.zst \
    --dry-run \
    --verbose
```

---

## 📚 Full Documentation

- **Complete Guide:** `data/databento/mnq/ohlcv_1m/README.md`
- **Implementation Details:** `DATABENTO_INGESTION_PHASE1A_COMPLETE.md`
- **Schema:** `database/databento_ohlcv_schema.sql`

---

## 🎯 Common Commands

```bash
# Ingest with limit (testing)
python scripts/ingest_databento_ohlcv_1m.py \
    --input file.dbn.zst \
    --limit 1000

# Ingest with verbose logging
python scripts/ingest_databento_ohlcv_1m.py \
    --input file.dbn.zst \
    --verbose

# Ingest custom symbol
python scripts/ingest_databento_ohlcv_1m.py \
    --input file.dbn.zst \
    --symbol "CME_MINI:MES1!" \
    --dataset "mes_ohlcv_1m"

# Check ingestion runs
psql $DATABASE_URL -c "SELECT * FROM data_ingest_runs ORDER BY started_at DESC LIMIT 5;"

# Check bar count
psql $DATABASE_URL -c "SELECT COUNT(*) FROM market_bars_ohlcv_1m;"
```

---

## ✅ Success Checklist

- [ ] Migration completed (tables created)
- [ ] Dry-run validation passed
- [ ] Production ingestion completed
- [ ] API endpoint returns data
- [ ] Re-run is idempotent (no duplicates)
- [ ] Test script passes all checks

---

**Ready to ingest? Start with Step 1! 🚀**

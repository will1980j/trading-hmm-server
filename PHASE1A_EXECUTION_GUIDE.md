# 🚀 PHASE 1A EXECUTION GUIDE - FULL 15-YEAR INGESTION

**Date:** December 25, 2025  
**Status:** Ready for execution  
**Dataset:** 15 years of MNQ 1-minute OHLCV bars (2010-2025)

---

## 📋 EXECUTION CHECKLIST

Execute these tasks **IN ORDER**:

- [ ] Task 1: Run full ingestion locally
- [ ] Task 2: Verify row counts in PostgreSQL
- [ ] Task 3: Confirm idempotency
- [ ] Task 4: Verify deployed API endpoint
- [ ] Task 5: Update homepage roadmap

---

## 🎯 TASK 1: RUN FULL INGESTION

### Command

```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input "data/databento/mnq/ohlcv_1m/raw/*.dbn.zst" \
    --verbose
```

### Expected Output

```
================================================================================
🚀 DATABENTO OHLCV-1M INGESTION
================================================================================
File: data/databento/mnq/ohlcv_1m/raw/file1.dbn.zst
Symbol: CME_MINI:MNQ1!
Dataset: mnq_ohlcv_1m
Dry Run: False
================================================================================

🔐 Computing file hash...
📦 Decompressing file1.dbn.zst...
📖 Reading DBN file...
   Rows read: 2,500,000
🔄 Normalizing data...
   Normalized rows: 2,500,000
   Time range: 2010-06-06 00:00:00+00:00 to 2012-12-31 23:59:00+00:00
✅ Validating data...
   ✅ All validations passed
   Min timestamp: 2010-06-06 00:00:00+00:00
   Max timestamp: 2012-12-31 23:59:00+00:00
   Total bars: 2,500,000
🔌 Connecting to database...
📝 Created ingestion run ID: 1
💾 Upserting 2,500,000 bars...
   Staged 2,500,000 records
   ✅ Inserted: 2,500,000
   ✅ Updated: 0

================================================================================
✅ INGESTION COMPLETE
================================================================================
Run ID: 1
Total bars: 2,500,000
Inserted: 2,500,000
Updated: 0
Time range: 2010-06-06 00:00:00+00:00 to 2012-12-31 23:59:00+00:00
================================================================================

[Process repeats for each .dbn.zst file...]
```

### Expected Metrics

**15 years of 1-minute bars:**
- **Trading days per year:** ~252
- **Trading hours per day:** ~6.5 (futures market)
- **Minutes per day:** ~390
- **Total bars (approx):** 252 × 15 × 390 = **~1,473,600 bars**

**Actual may be higher** due to extended hours trading and 24-hour futures sessions.

### Save Output

```bash
# Run with output logging
python scripts/ingest_databento_ohlcv_1m.py \
    --input "data/databento/mnq/ohlcv_1m/raw/*.dbn.zst" \
    --verbose > ingestion_output.log 2>&1

# Monitor progress
tail -f ingestion_output.log
```

---

## 🎯 TASK 2: VERIFY ROW COUNTS IN POSTGRESQL

### SQL Queries

```sql
-- Query 1: Total row count and time range
SELECT 
    COUNT(*) AS row_count,
    MIN(ts) AS min_ts,
    MAX(ts) AS max_ts,
    MIN(ts_ms) AS min_ts_ms,
    MAX(ts_ms) AS max_ts_ms
FROM market_bars_ohlcv_1m
WHERE symbol = 'CME_MINI:MNQ1!';

-- Query 2: Recent ingestion runs
SELECT 
    id,
    started_at,
    finished_at,
    row_count,
    inserted_count,
    updated_count,
    status,
    EXTRACT(EPOCH FROM (finished_at - started_at)) AS duration_seconds
FROM data_ingest_runs
ORDER BY id DESC
LIMIT 5;

-- Query 3: Ingestion summary
SELECT 
    COUNT(*) AS total_runs,
    SUM(row_count) AS total_rows_processed,
    SUM(inserted_count) AS total_inserted,
    SUM(updated_count) AS total_updated,
    COUNT(*) FILTER (WHERE status = 'success') AS successful_runs,
    COUNT(*) FILTER (WHERE status = 'failed') AS failed_runs
FROM data_ingest_runs;

-- Query 4: Data distribution by year
SELECT 
    EXTRACT(YEAR FROM ts) AS year,
    COUNT(*) AS bar_count,
    MIN(ts) AS first_bar,
    MAX(ts) AS last_bar
FROM market_bars_ohlcv_1m
WHERE symbol = 'CME_MINI:MNQ1!'
GROUP BY EXTRACT(YEAR FROM ts)
ORDER BY year;
```

### Execute Queries

```bash
# Using psql
psql $DATABASE_URL -f verify_ingestion.sql

# Or using Python script (see below)
python verify_full_ingestion.py
```

### Expected Results

**Query 1:**
```
row_count | min_ts                      | max_ts
----------|-----------------------------|--------------------------
1,500,000 | 2010-06-06 00:00:00+00:00  | 2025-12-23 23:59:00+00:00
```

**Query 2:**
```
id | started_at          | finished_at         | row_count | inserted | updated | status  | duration
---|---------------------|---------------------|-----------|----------|---------|---------|----------
5  | 2025-12-25 10:45:00 | 2025-12-25 10:50:00 | 500,000   | 500,000  | 0       | success | 300
4  | 2025-12-25 10:40:00 | 2025-12-25 10:45:00 | 500,000   | 500,000  | 0       | success | 300
3  | 2025-12-25 10:35:00 | 2025-12-25 10:40:00 | 500,000   | 500,000  | 0       | success | 300
```

---

## 🎯 TASK 3: CONFIRM IDEMPOTENCY

### Re-run Ingestion

```bash
# Run same command again
python scripts/ingest_databento_ohlcv_1m.py \
    --input "data/databento/mnq/ohlcv_1m/raw/*.dbn.zst" \
    --verbose
```

### Expected Output (Second Run)

```
================================================================================
✅ INGESTION COMPLETE
================================================================================
Run ID: 6
Total bars: 2,500,000
Inserted: 0          ← Should be 0 (no new rows)
Updated: 2,500,000   ← Should match row count (all existing rows updated)
Time range: 2010-06-06 00:00:00+00:00 to 2012-12-31 23:59:00+00:00
================================================================================
```

### Verify No Duplicates

```sql
-- Check for duplicate timestamps per symbol
SELECT 
    symbol,
    ts,
    COUNT(*) AS duplicate_count
FROM market_bars_ohlcv_1m
GROUP BY symbol, ts
HAVING COUNT(*) > 1;

-- Expected: 0 rows (no duplicates)
```

---

## 🎯 TASK 4: VERIFY DEPLOYED API ENDPOINT

### Test Production Endpoint

```bash
# Test deployed Railway endpoint
curl https://web-production-f8c3.up.railway.app/api/market-data/mnq/ohlcv-1m/stats
```

### Expected Response

```json
{
  "row_count": 1500000,
  "min_ts": "2010-06-06T00:00:00+00:00",
  "max_ts": "2025-12-23T23:59:00+00:00",
  "latest_close": 21234.50,
  "latest_ts": "2025-12-23T23:59:00+00:00",
  "symbol": "CME_MINI:MNQ1!",
  "timeframe": "1m",
  "vendor": "databento"
}
```

### Validation Checklist

- [ ] `row_count` is in millions (1M+)
- [ ] `min_ts` is near 2010-06-06
- [ ] `max_ts` is near 2025-12-23
- [ ] `latest_close` is a valid price
- [ ] Response time < 1 second
- [ ] HTTP status code 200

### Test Script

```bash
# Save response to file
curl -s https://web-production-f8c3.up.railway.app/api/market-data/mnq/ohlcv-1m/stats \
    | jq '.' > api_response.json

# Verify fields
cat api_response.json
```

---

## 🎯 TASK 5: UPDATE HOMEPAGE ROADMAP

**See separate file:** `update_homepage_roadmap.py`

This will add the Databento Foundation section to the homepage checklist.

---

## 📊 VERIFICATION SCRIPTS

### Script 1: Verify Full Ingestion

**File:** `verify_full_ingestion.py`

```python
#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Query 1: Row count and time range
cursor.execute("""
    SELECT 
        COUNT(*) AS row_count,
        MIN(ts) AS min_ts,
        MAX(ts) AS max_ts
    FROM market_bars_ohlcv_1m
    WHERE symbol = 'CME_MINI:MNQ1!'
""")
result = cursor.fetchone()
print(f"Row Count: {result[0]:,}")
print(f"Min Timestamp: {result[1]}")
print(f"Max Timestamp: {result[2]}")

# Query 2: Ingestion runs
cursor.execute("""
    SELECT id, started_at, finished_at, row_count, inserted_count, updated_count, status
    FROM data_ingest_runs
    ORDER BY id DESC
    LIMIT 5
""")
print("\nRecent Ingestion Runs:")
for row in cursor.fetchall():
    print(f"  Run {row[0]}: {row[6]} - {row[3]:,} rows ({row[4]:,} inserted, {row[5]:,} updated)")

cursor.close()
conn.close()
```

### Script 2: Test API Endpoint

**File:** `test_api_endpoint.py`

```python
#!/usr/bin/env python3
import requests
import json

url = "https://web-production-f8c3.up.railway.app/api/market-data/mnq/ohlcv-1m/stats"

print(f"Testing: {url}")
response = requests.get(url)

print(f"Status Code: {response.status_code}")
print(f"Response Time: {response.elapsed.total_seconds():.2f}s")

if response.status_code == 200:
    data = response.json()
    print("\nAPI Response:")
    print(json.dumps(data, indent=2))
    
    # Validation
    print("\nValidation:")
    print(f"  ✅ Row count: {data['row_count']:,}")
    print(f"  ✅ Min timestamp: {data['min_ts']}")
    print(f"  ✅ Max timestamp: {data['max_ts']}")
    print(f"  ✅ Latest close: ${data['latest_close']:,.2f}")
else:
    print(f"❌ Error: {response.text}")
```

---

## 📝 DELIVERABLES TEMPLATE

### Console Output (Task 1)

```
[Paste ingestion output here]
Total files processed: X
Total bars ingested: X,XXX,XXX
Total duration: XX minutes
```

### SQL Results (Task 2)

```
[Paste SQL query results here]
Row count: X,XXX,XXX
Min timestamp: YYYY-MM-DD HH:MM:SS+00
Max timestamp: YYYY-MM-DD HH:MM:SS+00
```

### Idempotency Results (Task 3)

```
[Paste second ingestion run output here]
Inserted: 0
Updated: X,XXX,XXX
```

### API Response (Task 4)

```json
[Paste curl response here]
{
  "row_count": X,
  "min_ts": "...",
  "max_ts": "...",
  ...
}
```

### Homepage Update (Task 5)

```
File updated: [filename]
Route: [route path]
Commit: [git commit hash]
```

---

## ✅ SUCCESS CRITERIA

Phase 1A is complete when:

- [ ] Full 15-year dataset ingested (1M+ rows)
- [ ] No duplicate rows (idempotency verified)
- [ ] API endpoint returns correct statistics
- [ ] Homepage roadmap shows Databento Foundation section
- [ ] All verification scripts pass

---

## 🚨 TROUBLESHOOTING

### Issue: Ingestion takes too long

**Solution:** Run in background with nohup
```bash
nohup python scripts/ingest_databento_ohlcv_1m.py \
    --input "data/databento/mnq/ohlcv_1m/raw/*.dbn.zst" \
    --verbose > ingestion.log 2>&1 &

# Monitor progress
tail -f ingestion.log
```

### Issue: Out of memory

**Solution:** Ingest files one at a time
```bash
for file in data/databento/mnq/ohlcv_1m/raw/*.dbn.zst; do
    python scripts/ingest_databento_ohlcv_1m.py --input "$file" --verbose
done
```

### Issue: API endpoint returns 0 rows

**Solution:** Check Railway database connection
```bash
# Verify Railway DATABASE_URL matches local
echo $DATABASE_URL

# Test Railway database directly
psql $DATABASE_URL -c "SELECT COUNT(*) FROM market_bars_ohlcv_1m;"
```

---

## 📚 REFERENCE

- **Ingestion Script:** `scripts/ingest_databento_ohlcv_1m.py`
- **Schema:** `database/databento_ohlcv_schema.sql`
- **Migration:** `database/run_databento_migration.py`
- **Documentation:** `data/databento/mnq/ohlcv_1m/README.md`
- **Quick Start:** `DATABENTO_QUICK_START.md`

---

**Ready to execute? Start with Task 1!** 🚀

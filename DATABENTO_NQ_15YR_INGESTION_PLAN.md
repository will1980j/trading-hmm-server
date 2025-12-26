# Databento NQ 15-Year Historical Data Ingestion Plan

## Overview

Replicate the MNQ 6-year ingestion approach for NQ (full-size E-mini NASDAQ-100) with 15 years of historical data.

## Data Specifications

- **Symbol:** NQ (E-mini NASDAQ-100 futures)
- **Databento Symbol:** `GLBX.MDP3:NQ*` or `CME:NQ*` (continuous front-month)
- **Timeframe:** 1-minute OHLCV bars
- **Date Range:** 2010-01-01 to 2025-12-26 (15 years)
- **Estimated Size:** ~3.9 million bars (15 years × 260 trading days × 1,000 bars/day)
- **Format:** DBN.ZST (Databento compressed format)

## Step-by-Step Process

### Step 1: Download Data from Databento

**Using Databento CLI:**
```bash
# Install Databento CLI
pip install databento-cli

# Authenticate
databento auth login

# Download 15 years of NQ 1-minute OHLCV data
databento download \
    --dataset GLBX.MDP3 \
    --symbols NQ.c.0 \
    --schema ohlcv-1m \
    --start 2010-01-01 \
    --end 2025-12-26 \
    --output data/databento/nq/ohlcv_1m/raw/nq_ohlcv_1m_2010_2025.dbn.zst
```

**Alternative: Download via Python API:**
```python
import databento as db

client = db.Historical('YOUR_API_KEY')

# Download 15 years of NQ data
client.timeseries.get_range(
    dataset='GLBX.MDP3',
    symbols=['NQ.c.0'],  # Continuous front-month
    schema='ohlcv-1m',
    start='2010-01-01',
    end='2025-12-26',
    path='data/databento/nq/ohlcv_1m/raw/nq_ohlcv_1m_2010_2025.dbn.zst'
)
```

**Cost Estimate:**
- ~3.9 million bars × $0.000001/bar = ~$3.90 (approximate)
- Check Databento pricing for exact cost

### Step 2: Create Directory Structure

```bash
mkdir -p data/databento/nq/ohlcv_1m/raw
mkdir -p data/databento/nq/ohlcv_1m/processed
```

### Step 3: Run Database Migration (If Not Already Done)

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

**Note:** If tables already exist from MNQ ingestion, this is safe to run (idempotent).

### Step 4: Dry Run Validation

Test ingestion without writing to database:
```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/nq/ohlcv_1m/raw/nq_ohlcv_1m_2010_2025.dbn.zst \
    --symbol "CME:NQ1!" \
    --dataset "nq_ohlcv_1m" \
    --dry-run \
    --verbose
```

**Expected Output:**
```
✅ DRY RUN COMPLETE - No database changes made
Would process: 3,900,000 bars
Time range: 2010-01-01 00:00:00+00:00 to 2025-12-26 23:59:00+00:00
```

### Step 5: Production Ingestion

Ingest all 15 years of data:
```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/nq/ohlcv_1m/raw/nq_ohlcv_1m_2010_2025.dbn.zst \
    --symbol "CME:NQ1!" \
    --dataset "nq_ohlcv_1m" \
    --verbose
```

**Expected Duration:** 10-30 minutes (depending on hardware and database connection)

**Expected Output:**
```
✅ INGESTION COMPLETE
Run ID: 2
Total bars: 3,900,000
Inserted: 3,900,000
Updated: 0
Time range: 2010-01-01 00:00:00+00:00 to 2025-12-26 23:59:00+00:00
```

### Step 6: Verify Ingestion

**Option A: API Endpoint**
```bash
curl https://web-production-f8c3.up.railway.app/api/market-data/nq/ohlcv-1m/stats
```

**Option B: Database Query**
```sql
SELECT 
    COUNT(*) as total_bars,
    MIN(ts) as earliest_bar,
    MAX(ts) as latest_bar,
    symbol
FROM market_bars_ohlcv_1m
WHERE symbol = 'CME:NQ1!'
GROUP BY symbol;
```

**Option C: Test Script**
```bash
python test_nq_databento_ingestion.py
```

## Differences from MNQ

| Aspect | MNQ (Micro) | NQ (Full-Size) |
|--------|-------------|----------------|
| **Symbol** | CME_MINI:MNQ1! | CME:NQ1! |
| **Contract Size** | $2 per point | $20 per point |
| **Tick Size** | 0.25 points | 0.25 points |
| **Data Range** | 6 years (2019-2025) | 15 years (2010-2025) |
| **Estimated Bars** | ~1.5M | ~3.9M |
| **Use Case** | Current trading | Historical backtesting |

## API Endpoint (To Be Created)

**Endpoint:** `GET /api/market-data/nq/ohlcv-1m/stats`

**Response:**
```json
{
  "row_count": 3900000,
  "min_ts": "2010-01-01T00:00:00+00:00",
  "max_ts": "2025-12-26T23:59:00+00:00",
  "latest_close": 21234.50,
  "latest_ts": "2025-12-26T16:00:00+00:00",
  "symbol": "CME:NQ1!",
  "timeframe": "1m",
  "vendor": "databento"
}
```

## Storage Considerations

### Database Size Estimate

**Per Bar Storage:**
- Timestamp: 8 bytes
- OHLC (4 × NUMERIC): ~40 bytes
- Volume: ~10 bytes
- Metadata: ~20 bytes
- **Total:** ~78 bytes/bar

**15 Years:**
- 3.9M bars × 78 bytes = ~304 MB (raw data)
- With indexes: ~500 MB total
- With audit trail: ~510 MB total

**Combined with MNQ (6 years):**
- MNQ: ~117 MB (1.5M bars)
- NQ: ~304 MB (3.9M bars)
- **Total:** ~421 MB (raw data), ~700 MB with indexes

### Railway PostgreSQL Limits

- **Free Tier:** 512 MB (NOT ENOUGH for 15 years)
- **Starter Plan ($5/mo):** 8 GB (plenty of room)
- **Pro Plan ($20/mo):** 32 GB (overkill for this use case)

**Recommendation:** Upgrade to Starter Plan ($5/mo) before ingesting 15 years.

## Ingestion Strategy

### Option A: Single File (Recommended)

Download entire 15-year range as one file:
```bash
databento download \
    --dataset GLBX.MDP3 \
    --symbols NQ.c.0 \
    --schema ohlcv-1m \
    --start 2010-01-01 \
    --end 2025-12-26 \
    --output data/databento/nq/ohlcv_1m/raw/nq_15yr.dbn.zst
```

**Pros:**
- Single ingestion run
- Simpler to manage
- Faster overall

**Cons:**
- Large file download (~500 MB compressed)
- Longer single ingestion time

### Option B: Yearly Files (Alternative)

Download one file per year:
```bash
for year in {2010..2025}; do
    databento download \
        --dataset GLBX.MDP3 \
        --symbols NQ.c.0 \
        --schema ohlcv-1m \
        --start ${year}-01-01 \
        --end ${year}-12-31 \
        --output data/databento/nq/ohlcv_1m/raw/nq_${year}.dbn.zst
done
```

Then ingest each file:
```bash
for file in data/databento/nq/ohlcv_1m/raw/nq_*.dbn.zst; do
    python scripts/ingest_databento_ohlcv_1m.py \
        --input $file \
        --symbol "CME:NQ1!" \
        --dataset "nq_ohlcv_1m"
done
```

**Pros:**
- Smaller individual downloads
- Can resume if interrupted
- Easier to debug issues

**Cons:**
- More complex workflow
- Multiple ingestion runs
- Longer total time

## Post-Ingestion Tasks

### 1. Create API Endpoint

Add to `web_server.py`:
```python
@app.route('/api/market-data/nq/ohlcv-1m/stats', methods=['GET'])
def nq_ohlcv_1m_stats():
    """Get NQ OHLCV-1M dataset statistics"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as row_count,
                MIN(ts) as min_ts,
                MAX(ts) as max_ts,
                (SELECT close FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'CME:NQ1!' 
                 ORDER BY ts DESC LIMIT 1) as latest_close,
                (SELECT ts FROM market_bars_ohlcv_1m 
                 WHERE symbol = 'CME:NQ1!' 
                 ORDER BY ts DESC LIMIT 1) as latest_ts
            FROM market_bars_ohlcv_1m
            WHERE symbol = 'CME:NQ1!'
        """)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] > 0:
            return jsonify({
                'row_count': result[0],
                'min_ts': result[1].isoformat() if result[1] else None,
                'max_ts': result[2].isoformat() if result[2] else None,
                'latest_close': float(result[3]) if result[3] else None,
                'latest_ts': result[4].isoformat() if result[4] else None,
                'symbol': 'CME:NQ1!',
                'timeframe': '1m',
                'vendor': 'databento'
            })
        else:
            return jsonify({
                'row_count': 0,
                'message': 'No NQ data ingested yet'
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Update Homepage Stats

Add NQ stats alongside MNQ stats on homepage.

### 3. Create Verification Script

```python
# test_nq_databento_ingestion.py
import requests

response = requests.get('https://web-production-f8c3.up.railway.app/api/market-data/nq/ohlcv-1m/stats')
data = response.json()

print(f"NQ Data Ingestion Status:")
print(f"  Total Bars: {data['row_count']:,}")
print(f"  Date Range: {data['min_ts']} to {data['max_ts']}")
print(f"  Latest Close: ${data['latest_close']:,.2f}")
print(f"  Latest Time: {data['latest_ts']}")
```

## Timeline

1. **Download:** 30-60 minutes (depends on internet speed)
2. **Dry Run:** 5-10 minutes
3. **Production Ingestion:** 10-30 minutes
4. **Verification:** 2 minutes
5. **API Endpoint:** 5 minutes
6. **Deployment:** 3 minutes

**Total:** ~1-2 hours

## Checklist

- [ ] Upgrade Railway PostgreSQL to Starter Plan ($5/mo)
- [ ] Download 15 years of NQ data from Databento
- [ ] Verify file integrity (check file size, decompress test)
- [ ] Run dry-run validation
- [ ] Run production ingestion
- [ ] Verify via database query
- [ ] Create API endpoint for NQ stats
- [ ] Deploy to Railway
- [ ] Test API endpoint
- [ ] Update homepage with NQ stats

## Cost Analysis

**Databento Data Cost:**
- 15 years × 260 days × 1,000 bars = 3.9M bars
- At $0.000001/bar = ~$3.90

**Railway Storage Cost:**
- Upgrade to Starter Plan: $5/month
- Includes 8 GB storage (plenty for NQ + MNQ)

**Total One-Time Cost:** ~$9 ($4 data + $5 first month)

## Success Criteria

✅ NQ data ingested successfully (3.9M+ bars)
✅ API endpoint returns correct statistics
✅ Date range spans 2010-2025
✅ No duplicate bars
✅ Homepage displays NQ stats
✅ Idempotent re-runs work correctly

---

**Ready to execute? Start with Step 1: Download data from Databento!**

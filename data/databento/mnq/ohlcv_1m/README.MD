# Databento MNQ OHLCV-1M Data

This directory contains 1-minute OHLCV (Open, High, Low, Close, Volume) bar data for the Micro E-mini NASDAQ-100 futures contract (MNQ) from Databento.

## Directory Structure

```
data/databento/mnq/ohlcv_1m/
├── raw/                    # Raw .dbn.zst files (NOT committed to git)
│   ├── *.dbn.zst          # Compressed Databento files
│   ├── manifest.json      # Dataset manifest
│   ├── metadata.json      # Dataset metadata
│   ├── symbology.json     # Symbol mappings
│   └── condition.json     # Condition codes
├── processed/             # Processed data (optional)
└── README.md              # This file
```

## Data Format

- **Format:** Databento DBN (compressed with zstd)
- **Symbol:** CME_MINI:MNQ1! (continuous front-month contract)
- **Timeframe:** 1-minute bars
- **Vendor:** Databento
- **Schema:** ohlcv-1m

## Ingestion

### Prerequisites

1. **Database Migration:**
   ```bash
   python database/run_databento_migration.py
   ```
   
   This creates:
   - `market_bars_ohlcv_1m` table (stores OHLCV bars)
   - `data_ingest_runs` table (audit trail)

2. **Environment Variables:**
   Ensure `DATABASE_URL` is set in `.env` file:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

### Basic Ingestion

Ingest a single file:
```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/mnq/ohlcv_1m/raw/file.dbn.zst
```

### Dry Run (Validation Only)

Test ingestion without writing to database:
```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/mnq/ohlcv_1m/raw/file.dbn.zst \
    --dry-run
```

### Advanced Options

**Limit rows for testing:**
```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/mnq/ohlcv_1m/raw/file.dbn.zst \
    --limit 1000 \
    --verbose
```

**Custom symbol and dataset:**
```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/mnq/ohlcv_1m/raw/file.dbn.zst \
    --symbol "CME_MINI:MNQ1!" \
    --dataset "mnq_ohlcv_1m" \
    --verbose
```

### Expected Output

Successful ingestion:
```
================================================================================
🚀 DATABENTO OHLCV-1M INGESTION
================================================================================
File: data/databento/mnq/ohlcv_1m/raw/file.dbn.zst
Symbol: CME_MINI:MNQ1!
Dataset: mnq_ohlcv_1m
Dry Run: False
================================================================================

🔐 Computing file hash...
📦 Decompressing file.dbn.zst...
📖 Reading DBN file...
   Rows read: 50,000
🔄 Normalizing data...
   Normalized rows: 50,000
   Time range: 2024-01-01 00:00:00+00:00 to 2024-01-15 23:59:00+00:00
✅ Validating data...
   ✅ All validations passed
   Min timestamp: 2024-01-01 00:00:00+00:00
   Max timestamp: 2024-01-15 23:59:00+00:00
   Total bars: 50,000
🔌 Connecting to database...
📝 Created ingestion run ID: 1
💾 Upserting 50,000 bars...
   Staged 50,000 records
   ✅ Inserted: 50,000
   ✅ Updated: 0

================================================================================
✅ INGESTION COMPLETE
================================================================================
Run ID: 1
Total bars: 50,000
Inserted: 50,000
Updated: 0
Time range: 2024-01-01 00:00:00+00:00 to 2024-01-15 23:59:00+00:00
================================================================================
```

### Idempotent Re-runs

The ingestion script is **idempotent** - safe to run multiple times:

**First run:**
```
Inserted: 50,000
Updated: 0
```

**Second run (same file):**
```
Inserted: 0
Updated: 50,000
```

No duplicate data is created. Existing bars are updated with new values.

## Verification

### API Endpoint

Check ingestion status via API:
```bash
curl https://web-production-f8c3.up.railway.app/api/market-data/mnq/ohlcv-1m/stats
```

**Response:**
```json
{
  "row_count": 50000,
  "min_ts": "2024-01-01T00:00:00+00:00",
  "max_ts": "2024-01-15T23:59:00+00:00",
  "latest_close": 16234.50,
  "latest_ts": "2024-01-15T23:59:00+00:00",
  "symbol": "CME_MINI:MNQ1!",
  "timeframe": "1m",
  "vendor": "databento"
}
```

### Database Query

Direct database verification:
```sql
-- Total bars
SELECT COUNT(*) FROM market_bars_ohlcv_1m;

-- Time range
SELECT MIN(ts), MAX(ts) FROM market_bars_ohlcv_1m;

-- Latest bar
SELECT * FROM market_bars_ohlcv_1m 
ORDER BY ts DESC LIMIT 1;

-- Ingestion runs
SELECT * FROM data_ingest_runs 
ORDER BY started_at DESC;
```

## Data Validation

The ingestion script performs comprehensive validation:

### Integrity Checks
- ✅ No empty DataFrames
- ✅ No NaN values in OHLC columns
- ✅ High >= max(Open, Close, Low)
- ✅ Low <= min(Open, Close, High)
- ✅ Timestamps are monotonic increasing
- ✅ No duplicate timestamps

### Warnings (Not Errors)
- ⚠️ Gaps in 1-minute spacing (expected during market closures)

## Troubleshooting

### Error: "DATABASE_URL not found"
**Solution:** Set `DATABASE_URL` in `.env` file:
```bash
echo "DATABASE_URL=postgresql://..." > .env
```

### Error: "Input file not found"
**Solution:** Verify file path is correct:
```bash
ls -lh data/databento/mnq/ohlcv_1m/raw/
```

### Error: "Validation failed"
**Solution:** Run with `--dry-run --verbose` to see detailed validation errors:
```bash
python scripts/ingest_databento_ohlcv_1m.py \
    --input file.dbn.zst \
    --dry-run \
    --verbose
```

### Error: "Missing required columns"
**Solution:** Verify DBN file contains OHLCV schema data. Check with:
```python
import databento as db
store = db.DBNStore.from_file('file.dbn')
print(store.to_df().columns)
```

## Git Ignore

Raw data files are **NOT committed to git**. The `.gitignore` includes:
```
data/databento/mnq/ohlcv_1m/raw/*.dbn
data/databento/mnq/ohlcv_1m/raw/*.dbn.zst
data/databento/mnq/ohlcv_1m/raw/*.json
```

Only documentation and scripts are version controlled.

## Next Steps

After successful ingestion:

1. **Verify data via API:**
   ```bash
   curl https://web-production-f8c3.up.railway.app/api/market-data/mnq/ohlcv-1m/stats
   ```

2. **Build candle aggregation:**
   - 5-minute bars
   - 15-minute bars
   - Hourly bars

3. **Integrate with trading system:**
   - Real-time bar updates
   - Historical backtesting
   - Strategy optimization

4. **Set up automated ingestion:**
   - Daily data downloads
   - Automatic ingestion pipeline
   - Data quality monitoring

## Support

For issues or questions:
- Check logs with `--verbose` flag
- Review `data_ingest_runs` table for error details
- Verify database connection with `run_databento_migration.py`

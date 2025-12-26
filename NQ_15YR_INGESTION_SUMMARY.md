# NQ 15-Year Data Ingestion - Ready to Execute

## What You Asked For

Replicate the MNQ 6-year ingestion approach for NQ with 15 years of historical data (2010-2025).

## The Approach (Same as MNQ)

1. **Download** DBN.ZST file from Databento
2. **Run migration** (if not already done)
3. **Ingest** using `scripts/ingest_databento_ohlcv_1m.py`
4. **Verify** via API endpoint

## Quick Start

### Option 1: Automated Script (Recommended)

```bash
python download_and_ingest_nq_15yr.py
```

This script will:
- Create directory structure
- Download 15 years of NQ data from Databento
- Run dry-run validation
- Prompt for confirmation
- Ingest to PostgreSQL
- Verify success

### Option 2: Manual Steps

```bash
# 1. Download data
databento download \
    --dataset GLBX.MDP3 \
    --symbols NQ.c.0 \
    --schema ohlcv-1m \
    --start 2010-01-01 \
    --end 2025-12-26 \
    --output data/databento/nq/ohlcv_1m/raw/nq_15yr.dbn.zst

# 2. Dry run
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/nq/ohlcv_1m/raw/nq_15yr.dbn.zst \
    --symbol "CME:NQ1!" \
    --dataset "nq_ohlcv_1m" \
    --dry-run

# 3. Production ingestion
python scripts/ingest_databento_ohlcv_1m.py \
    --input data/databento/nq/ohlcv_1m/raw/nq_15yr.dbn.zst \
    --symbol "CME:NQ1!" \
    --dataset "nq_ohlcv_1m"
```

## Key Differences from MNQ

| Aspect | MNQ (Done) | NQ (New) |
|--------|------------|----------|
| Symbol | CME_MINI:MNQ1! | CME:NQ1! |
| Years | 6 (2019-2025) | 15 (2010-2025) |
| Bars | ~1.5M | ~3.9M |
| Storage | ~117 MB | ~304 MB |
| Cost | ~$1.50 | ~$3.90 |

## Prerequisites

1. **Databento CLI installed:**
   ```bash
   pip install databento-cli
   databento auth login
   ```

2. **Railway PostgreSQL upgraded:**
   - Current: Free tier (512 MB) - NOT ENOUGH
   - Required: Starter Plan ($5/mo, 8 GB) - PLENTY

3. **Database migration run:**
   ```bash
   python database/run_databento_migration.py
   ```

## Files Created

- ✅ `DATABENTO_NQ_15YR_INGESTION_PLAN.md` - Complete plan
- ✅ `download_and_ingest_nq_15yr.py` - Automated script
- ✅ `NQ_15YR_INGESTION_SUMMARY.md` - This file

## Timeline

- Download: 30-60 minutes
- Ingestion: 10-30 minutes
- Total: 1-2 hours

## Next Steps

1. **Upgrade Railway PostgreSQL** to Starter Plan ($5/mo)
2. **Run the script:** `python download_and_ingest_nq_15yr.py`
3. **Wait for completion** (~1-2 hours)
4. **Verify success** via API endpoint

---

**Ready to execute!** Run `python download_and_ingest_nq_15yr.py` to start.

# Database Migrations - Railway Deployment Guide

## How to Run Migrations

This repo uses Python scripts to apply database schema changes to Railway PostgreSQL.

### Prerequisites
- `.env` file with `DATABASE_URL` pointing to Railway database
- Python 3.x installed
- `psycopg2` package installed (`pip install psycopg2-binary`)

## Running Indicator Export Migration

### Option 1: Local Script (Recommended)

**Command:**
```bash
python database/run_indicator_export_migration.py
```

**What it does:**
1. Reads `DATABASE_URL` from `.env`
2. Connects to Railway PostgreSQL
3. Executes `database/indicator_export_schema.sql`
4. Creates 3 tables: `indicator_export_batches`, `all_signals_ledger`, `confirmed_signals_ledger`
5. Verifies tables and indexes were created

**Expected output:**
```
🔄 Connecting to database...
📖 Reading schema file...
🚀 Executing migration...

✅ Migration complete!

📊 Verifying tables...

Tables created:
  ✅ all_signals_ledger (18 columns)
  ✅ confirmed_signals_ledger (14 columns)
  ✅ indicator_export_batches (11 columns)

📇 Verifying indexes...

Indexes created:
  ✅ all_signals_ledger (4 indexes)
  ✅ confirmed_signals_ledger (5 indexes)
  ✅ indicator_export_batches (3 indexes)
```

### Option 2: Direct SQL (Railway Console)

**Steps:**
1. Go to Railway dashboard
2. Open your PostgreSQL database
3. Click "Query" tab
4. Copy entire contents of `database/indicator_export_schema.sql`
5. Paste into query editor
6. Click "Run"

**Verification query:**
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger');
```

Should return 3 rows.

### Option 3: Via Railway CLI (Advanced)

**Command:**
```bash
railway run python database/run_indicator_export_migration.py
```

**Note:** Requires Railway CLI installed and project linked.

## Safety Features

### Idempotent
All tables use `CREATE TABLE IF NOT EXISTS` - safe to run multiple times.

### No Data Loss
- Does not drop existing tables
- Does not modify existing tables
- Only creates new tables if they don't exist

### Verification Built-In
Migration script automatically verifies:
- Tables were created
- Indexes were created
- Column counts are correct

## Troubleshooting

### Error: "DATABASE_URL not found"
**Solution:** Ensure `.env` file exists with `DATABASE_URL=postgresql://...`

### Error: "relation already exists"
**Solution:** Tables already created - this is OK (idempotent)

### Error: "permission denied"
**Solution:** Check DATABASE_URL has write permissions

### Error: "connection refused"
**Solution:** Verify DATABASE_URL is correct and Railway database is running

## Verification After Migration

### Check Tables Exist:
```sql
SELECT table_name, 
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns
FROM information_schema.tables t
WHERE table_name IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger')
ORDER BY table_name;
```

### Check Indexes Exist:
```sql
SELECT tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('indicator_export_batches', 'all_signals_ledger', 'confirmed_signals_ledger')
ORDER BY tablename, indexname;
```

### Check Row Counts (Should be 0 initially):
```sql
SELECT 'indicator_export_batches' as table_name, COUNT(*) FROM indicator_export_batches
UNION ALL
SELECT 'all_signals_ledger', COUNT(*) FROM all_signals_ledger
UNION ALL
SELECT 'confirmed_signals_ledger', COUNT(*) FROM confirmed_signals_ledger;
```

## Other Migrations in This Repo

### Data Quality Tables (Already Exists)
```bash
python database/run_data_quality_migration.py
```

### Hybrid Sync Tables (If Needed)
```bash
python database/run_hybrid_sync_migration.py
```

## Migration Workflow

### Standard Process:
1. **Create schema file** in `database/` folder (e.g., `my_feature_schema.sql`)
2. **Create migration script** (e.g., `database/run_my_feature_migration.py`)
3. **Test locally** against Railway database
4. **Commit and push** - Railway auto-deploys code
5. **Run migration** - Execute Python script to create tables
6. **Verify** - Check tables exist and have correct structure

### Why Separate Migration Step?
- Railway auto-deploys code but doesn't auto-run migrations
- Gives you control over when schema changes are applied
- Allows verification before production use
- Prevents accidental schema changes

## Safety Warnings

⚠️ **Run migrations once** - They're idempotent but no need to run repeatedly
⚠️ **Verify DATABASE_URL** - Ensure it points to correct Railway database
⚠️ **Backup first** (optional) - Railway has automatic backups, but you can export data if concerned
⚠️ **Test locally** - Run against Railway database from local machine first

## Post-Migration

After running migration:
1. ✅ Tables created
2. ✅ Indexes created
3. ✅ Foreign keys established
4. ✅ Ready for data import
5. ✅ Deploy code that uses new tables
6. ✅ Test endpoints

**Migrations are safe, idempotent, and verified. Run with confidence.** 🚀

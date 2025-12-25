#!/usr/bin/env python3
"""
Databento OHLCV-1M Ingestion Script

Ingests Databento DBN.ZST files into PostgreSQL with full validation and idempotency.

Features:
- Reads compressed .dbn.zst files directly
- Validates bar integrity (OHLC relationships, monotonic timestamps)
- Idempotent upserts (safe to re-run)
- Comprehensive audit trail
- Dry-run mode for testing

Usage:
    python scripts/ingest_databento_ohlcv_1m.py --input data/databento/mnq/ohlcv_1m/raw/*.dbn.zst
    python scripts/ingest_databento_ohlcv_1m.py --input path/to/file.dbn.zst --dry-run
    python scripts/ingest_databento_ohlcv_1m.py --input path/to/file.dbn.zst --limit 1000 --verbose
"""

import os
import sys
import argparse
import hashlib
import tempfile
import glob
import zstandard as zstd
import databento as db
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DatabentoIngester:
    """Handles ingestion of Databento OHLCV data into PostgreSQL"""
    
    def __init__(self, database_url, verbose=False):
        self.database_url = database_url
        self.verbose = verbose
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        if self.verbose:
            print(" Connecting to database...")
        self.conn = psycopg2.connect(self.database_url)
        self.conn.autocommit = False  # Use transaction mode
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def compute_file_hash(self, file_path):
        """Compute SHA256 hash of file"""
        if self.verbose:
            print(f" Computing file hash...")
        
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def decompress_zst(self, zst_path):
        """Decompress .zst file to temporary .dbn file"""
        if self.verbose:
            print(f" Decompressing {os.path.basename(zst_path)}...")
        
        # Create temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.dbn')
        os.close(temp_fd)
        
        try:
            # Decompress
            dctx = zstd.ZstdDecompressor()
            with open(zst_path, 'rb') as ifh, open(temp_path, 'wb') as ofh:
                dctx.copy_stream(ifh, ofh)
            
            return temp_path
        except Exception as e:
            os.unlink(temp_path)
            raise e
    
    def read_dbn_file(self, file_path, limit=None):
        """Read DBN file and convert to pandas DataFrame"""
        if self.verbose:
            print(f" Reading DBN file...")
        
        # Determine if we need to decompress
        is_compressed = file_path.endswith('.zst')
        dbn_path = file_path
        temp_path = None
        
        try:
            if is_compressed:
                temp_path = self.decompress_zst(file_path)
                dbn_path = temp_path
            
            # Read DBN file
            store = db.DBNStore.from_file(dbn_path)
            df = store.to_df()
            
            if limit:
                df = df.head(limit)
            
            if self.verbose:
                print(f"   Rows read: {len(df):,}")
            
            return df
            
        finally:
            # Clean up temp file (with retry for Windows)
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except PermissionError:
                    # Windows file locking - try again after a brief moment
                    import time
                    time.sleep(0.1)
                    try:
                        os.unlink(temp_path)
                    except:
                        # If still fails, just warn
                        if self.verbose:
                            print(f"     Could not delete temp file: {temp_path}")
    
    def normalize_dataframe(self, df, symbol):
        """Normalize DataFrame to expected schema"""
        if self.verbose:
            print(f" Normalizing data...")
            print(f"   Available columns: {list(df.columns)}")
            print(f"   Index name: {df.index.name}")
        
        # Reset index to make timestamp a column
        df = df.reset_index()
        
        # Create normalized DataFrame
        normalized = pd.DataFrame()
        
        # Timestamp handling - look for timestamp column
        timestamp_col = None
        for col in ['ts_event', 'timestamp', 'ts', 'time']:
            if col in df.columns:
                timestamp_col = col
                break
        
        if timestamp_col is None:
            raise ValueError(f"No timestamp column found. Columns: {list(df.columns)}")
        
        if pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            normalized['ts'] = pd.to_datetime(df[timestamp_col], utc=True)
        else:
            # Assume nanoseconds since epoch
            normalized['ts'] = pd.to_datetime(df[timestamp_col], unit='ns', utc=True)
        
        normalized['ts_ms'] = (normalized['ts'].astype('int64') // 1_000_000).astype('int64')
        
        # OHLCV data
        required_cols = ['open', 'high', 'low', 'close']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}. Available: {list(df.columns)}")
        
        normalized['open'] = df['open'].astype(float)
        normalized['high'] = df['high'].astype(float)
        normalized['low'] = df['low'].astype(float)
        normalized['close'] = df['close'].astype(float)
        normalized['volume'] = df['volume'].astype(float) if 'volume' in df.columns else None
        
        # Add symbol
        normalized['symbol'] = symbol
        
        # Sort by timestamp
        normalized = normalized.sort_values('ts').reset_index(drop=True)
        
        if self.verbose:
            print(f"   Normalized rows: {len(normalized):,}")
            print(f"   Time range: {normalized['ts'].min()} to {normalized['ts'].max()}")
        
        return normalized
    
    def validate_dataframe(self, df):
        """Validate data integrity"""
        if self.verbose:
            print(f" Validating data...")
        
        errors = []
        
        # Check not empty
        if len(df) == 0:
            errors.append("DataFrame is empty")
        
        # Check for NaNs in OHLC
        ohlc_cols = ['open', 'high', 'low', 'close']
        for col in ohlc_cols:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                errors.append(f"Column '{col}' has {nan_count} NaN values")
        
        # Check OHLC relationships
        invalid_high = (df['high'] < df['open']) | (df['high'] < df['close']) | (df['high'] < df['low'])
        if invalid_high.any():
            errors.append(f"Invalid high values: {invalid_high.sum()} bars")
        
        invalid_low = (df['low'] > df['open']) | (df['low'] > df['close']) | (df['low'] > df['high'])
        if invalid_low.any():
            errors.append(f"Invalid low values: {invalid_low.sum()} bars")
        
        # Check timestamp monotonicity
        if not df['ts'].is_monotonic_increasing:
            errors.append("Timestamps are not monotonic increasing")
        
        # Check for duplicate timestamps and remove them
        dup_count = df['ts'].duplicated().sum()
        if dup_count > 0:
            if self.verbose:
                print(f"   Found {dup_count} duplicate timestamps - keeping last occurrence")
            # This modifies df in place, which is returned
        
        # Check 1-minute spacing (allow gaps but log them)
        time_diffs = df['ts'].diff().dt.total_seconds()
        expected_spacing = 60  # 1 minute
        gaps = time_diffs[time_diffs > expected_spacing * 1.5]  # Allow 50% tolerance
        
        if len(gaps) > 0:
            print(f"     Found {len(gaps)} gaps in 1-minute spacing (expected, not an error)")
        
        if errors:
            raise ValueError(f"Validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        
        if self.verbose:
            print(f"    All validations passed")
            print(f"   Min timestamp: {df['ts'].min()}")
            print(f"   Max timestamp: {df['ts'].max()}")
            print(f"   Total bars: {len(df):,}")
        
        # Return deduplicated dataframe
        return df.drop_duplicates(subset=['ts'], keep='last').reset_index(drop=True)
    
    def create_ingest_run(self, vendor, dataset, file_name, file_hash):
        """Create ingestion run record"""
        self.cursor.execute("""
            INSERT INTO data_ingest_runs (vendor, dataset, file_name, file_sha256, status)
            VALUES (%s, %s, %s, %s, 'running')
            RETURNING id
        """, (vendor, dataset, file_name, file_hash))
        run_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return run_id
    
    def update_ingest_run(self, run_id, status, row_count=0, inserted=0, updated=0, 
                         min_ts=None, max_ts=None, error=None):
        """Update ingestion run record"""
        self.cursor.execute("""
            UPDATE data_ingest_runs
            SET finished_at = now(),
                status = %s,
                row_count = %s,
                inserted_count = %s,
                updated_count = %s,
                min_ts = %s,
                max_ts = %s,
                error = %s
            WHERE id = %s
        """, (status, row_count, inserted, updated, min_ts, max_ts, error, run_id))
        self.conn.commit()
    
    def upsert_bars(self, df, run_id):
        """Upsert bars into database with idempotency"""
        if self.verbose:
            print(f" Upserting {len(df):,} bars...")
        
        # Create temporary staging table
        self.cursor.execute("""
            CREATE TEMP TABLE staging_bars (
                symbol TEXT,
                ts TIMESTAMPTZ,
                ts_ms BIGINT,
                open NUMERIC,
                high NUMERIC,
                low NUMERIC,
                close NUMERIC,
                volume NUMERIC
            ) ON COMMIT DROP
        """)
        
        # Prepare data for bulk insert
        records = [
            (
                row['symbol'],
                row['ts'],
                row['ts_ms'],
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'] if pd.notna(row['volume']) else None
            )
            for _, row in df.iterrows()
        ]
        
        # Bulk insert into staging
        execute_values(
            self.cursor,
            """
            INSERT INTO staging_bars (symbol, ts, ts_ms, open, high, low, close, volume)
            VALUES %s
            """,
            records,
            page_size=1000
        )
        
        if self.verbose:
            print(f"   Staged {len(records):,} records")
        
        # Count existing records
        min_ts = df['ts'].min()
        max_ts = df['ts'].max()
        symbol = df['symbol'].iloc[0]
        
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM market_bars_ohlcv_1m
            WHERE symbol = %s AND ts BETWEEN %s AND %s
        """, (symbol, min_ts, max_ts))
        existing_count = self.cursor.fetchone()[0]
        
        # Perform upsert
        self.cursor.execute("""
            INSERT INTO market_bars_ohlcv_1m (
                vendor, schema, symbol, ts, ts_ms, open, high, low, close, volume, ingestion_run_id
            )
            SELECT 
                'databento', 'ohlcv-1m', symbol, ts, ts_ms, open, high, low, close, volume, %s
            FROM staging_bars
            ON CONFLICT (symbol, ts) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume,
                vendor = EXCLUDED.vendor,
                schema = EXCLUDED.schema,
                ingestion_run_id = EXCLUDED.ingestion_run_id
        """, (run_id,))
        
        inserted_count = len(df) - existing_count
        updated_count = existing_count
        
        self.conn.commit()
        
        if self.verbose:
            print(f"    Inserted: {inserted_count:,}")
            print(f"    Updated: {updated_count:,}")
        
        return inserted_count, updated_count
    
    def ingest_file(self, file_path, symbol, dataset, dry_run=False, limit=None):
        """Main ingestion workflow"""
        print(f"\n{'='*80}")
        print(f" DATABENTO OHLCV-1M INGESTION")
        print(f"{'='*80}")
        print(f"File: {file_path}")
        print(f"Symbol: {symbol}")
        print(f"Dataset: {dataset}")
        print(f"Dry Run: {dry_run}")
        if limit:
            print(f"Limit: {limit:,} rows")
        print(f"{'='*80}\n")
        
        # Compute file hash
        file_hash = self.compute_file_hash(file_path)
        file_name = os.path.basename(file_path)
        
        if self.verbose:
            print(f"File hash: {file_hash[:16]}...")
        
        # Read and normalize data
        df = self.read_dbn_file(file_path, limit=limit)
        df = self.normalize_dataframe(df, symbol)
        
        # Validate data (returns deduplicated dataframe)
        df = self.validate_dataframe(df)
        
        if dry_run:
            print(f"\n{'='*80}")
            print(f" DRY RUN COMPLETE - No database changes made")
            print(f"{'='*80}")
            print(f"Would process: {len(df):,} bars")
            print(f"Time range: {df['ts'].min()} to {df['ts'].max()}")
            print(f"{'='*80}\n")
            return
        
        # Connect to database
        self.connect()
        
        try:
            # Create ingestion run
            run_id = self.create_ingest_run('databento', dataset, file_name, file_hash)
            
            if self.verbose:
                print(f" Created ingestion run ID: {run_id}")
            
            # Upsert bars
            inserted, updated = self.upsert_bars(df, run_id)
            
            # Update run record
            self.update_ingest_run(
                run_id,
                status='success',
                row_count=len(df),
                inserted=inserted,
                updated=updated,
                min_ts=df['ts'].min(),
                max_ts=df['ts'].max()
            )
            
            print(f"\n{'='*80}")
            print(f" INGESTION COMPLETE")
            print(f"{'='*80}")
            print(f"Run ID: {run_id}")
            print(f"Total bars: {len(df):,}")
            print(f"Inserted: {inserted:,}")
            print(f"Updated: {updated:,}")
            print(f"Time range: {df['ts'].min()} to {df['ts'].max()}")
            print(f"{'='*80}\n")
            
        except Exception as e:
            # Rollback transaction first
            if self.conn:
                try:
                    self.conn.rollback()
                except:
                    pass
            
            # Update run record with error (in new transaction)
            if 'run_id' in locals():
                try:
                    self.update_ingest_run(run_id, status='failed', error=str(e))
                except:
                    # If update fails, just log it
                    if self.verbose:
                        print(f"   Could not update ingest run record")
            raise
        
        finally:
            self.close()

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Ingest Databento OHLCV-1M data into PostgreSQL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a single file
  python scripts/ingest_databento_ohlcv_1m.py --input data/databento/mnq/ohlcv_1m/raw/file.dbn.zst
  
  # Dry run to validate without writing
  python scripts/ingest_databento_ohlcv_1m.py --input file.dbn.zst --dry-run
  
  # Limit rows for testing
  python scripts/ingest_databento_ohlcv_1m.py --input file.dbn.zst --limit 1000 --verbose
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='Path to .dbn or .dbn.zst file'
    )
    
    parser.add_argument(
        '--symbol',
        default='CME_MINI:MNQ1!',
        help='Symbol identifier (default: CME_MINI:MNQ1!)'
    )
    
    parser.add_argument(
        '--dataset',
        default='mnq_ohlcv_1m',
        help='Dataset name (default: mnq_ohlcv_1m)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate data without writing to database'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of rows to process (for testing)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print(" ERROR: DATABASE_URL not found in environment")
        print("   Set DATABASE_URL in .env file or environment variables")
        sys.exit(1)
    
    # Expand glob pattern to get list of files
    input_pattern = args.input
    file_list = glob.glob(input_pattern)
    
    if not file_list:
        # Try as literal path if glob returns nothing
        if os.path.exists(input_pattern):
            file_list = [input_pattern]
        else:
            print(f" ERROR: No files found matching pattern: {input_pattern}")
            sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"Found {len(file_list)} file(s) to process")
    print(f"{'='*80}")
    for f in file_list:
        print(f"   - {os.path.basename(f)}")
    print(f"{'='*80}\n")
    
    # Process each file
    success_count = 0
    fail_count = 0
    
    for file_path in file_list:
        try:
            # Create new ingester for each file
            ingester = DatabentoIngester(database_url, verbose=args.verbose)
            ingester.ingest_file(
                file_path,
                args.symbol,
                args.dataset,
                dry_run=args.dry_run,
                limit=args.limit
            )
            success_count += 1
        except Exception as e:
            print(f"\n INGESTION FAILED for {os.path.basename(file_path)}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            fail_count += 1
            # Continue with next file instead of exiting
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"INGESTION SUMMARY")
    print(f"{'='*80}")
    print(f"Total files: {len(file_list)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"{'='*80}\n")
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()

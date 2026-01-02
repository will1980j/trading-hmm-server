#!/usr/bin/env python3
"""
Phase C Corpus Run Comparator - Compare two corpus runs for reproducibility
Usage: python scripts/phase_c_compare_runs.py RUN_ID_A RUN_ID_B
"""

import os
import sys
import argparse
import psycopg2


def parse_args():
    parser = argparse.ArgumentParser(description='Compare two corpus runs')
    parser.add_argument('run_id_a', help='First run ID (UUID)')
    parser.add_argument('run_id_b', help='Second run ID (UUID)')
    return parser.parse_args()


def get_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError('DATABASE_URL environment variable not set')
    return psycopg2.connect(database_url)


def fail(message):
    print(f'COMPARISON FAILED: {message}')
    sys.exit(1)


def load_run(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT bars_fingerprint, logic_version, symbol, start_ts, end_ts, status
            FROM signal_corpus_runs
            WHERE run_id = %s
        """, (run_id,))
        row = cur.fetchone()
        if not row:
            fail(f'Run {run_id} does not exist')
        
        if row[5] not in ('COMPLETE', 'LOCKED'):
            fail(f'Run {run_id} has status {row[5]} - must be COMPLETE or LOCKED. Run: python scripts/phase_c_validate_and_lock_run.py {run_id}')
        
        return {
            'bars_fingerprint': row[0],
            'logic_version': row[1],
            'symbol': row[2],
            'start_ts': row[3],
            'end_ts': row[4],
            'status': row[5]
        }


def load_snapshot(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT total_triangles, bull_count, bear_count, 
                   ym_counts_hash, direction_counts_hash, core_fingerprint_hash
            FROM signal_corpus_snapshot
            WHERE run_id = %s
        """, (run_id,))
        row = cur.fetchone()
        if not row:
            fail(f'Snapshot for run {run_id} not found. Run: python scripts/phase_c_validate_and_lock_run.py {run_id}')
        
        return {
            'total_triangles': row[0],
            'bull_count': row[1],
            'bear_count': row[2],
            'ym_counts_hash': row[3],
            'direction_counts_hash': row[4],
            'core_fingerprint_hash': row[5]
        }


def get_row_diffs(conn, run_id_a, run_id_b):
    with conn.cursor() as cur:
        cur.execute("""
            (SELECT symbol, ts, direction FROM signal_corpus_triangles WHERE run_id = %s
             EXCEPT
             SELECT symbol, ts, direction FROM signal_corpus_triangles WHERE run_id = %s)
            UNION ALL
            (SELECT symbol, ts, direction FROM signal_corpus_triangles WHERE run_id = %s
             EXCEPT
             SELECT symbol, ts, direction FROM signal_corpus_triangles WHERE run_id = %s)
            ORDER BY ts, direction
            LIMIT 20
        """, (run_id_a, run_id_b, run_id_b, run_id_a))
        return cur.fetchall()


def main():
    args = parse_args()
    run_id_a = args.run_id_a
    run_id_b = args.run_id_b
    
    conn = get_connection()
    
    try:
        print(f'Comparing runs: {run_id_a} vs {run_id_b}')
        
        run_a = load_run(conn, run_id_a)
        run_b = load_run(conn, run_id_b)
        
        if run_a['bars_fingerprint'] != run_b['bars_fingerprint']:
            fail(f'bars_fingerprint mismatch: {run_a["bars_fingerprint"]} != {run_b["bars_fingerprint"]}')
        
        if run_a['logic_version'] != run_b['logic_version']:
            fail(f'logic_version mismatch: {run_a["logic_version"]} != {run_b["logic_version"]}')
        
        if run_a['symbol'] != run_b['symbol']:
            fail(f'symbol mismatch: {run_a["symbol"]} != {run_b["symbol"]}')
        
        if run_a['start_ts'] != run_b['start_ts']:
            fail(f'start_ts mismatch: {run_a["start_ts"]} != {run_b["start_ts"]}')
        
        if run_a['end_ts'] != run_b['end_ts']:
            fail(f'end_ts mismatch: {run_a["end_ts"]} != {run_b["end_ts"]}')
        
        print('Run metadata: MATCH')
        print(f'  bars_fingerprint: {run_a["bars_fingerprint"]}')
        print(f'  logic_version: {run_a["logic_version"]}')
        print(f'  symbol: {run_a["symbol"]}')
        print(f'  range: {run_a["start_ts"]} to {run_a["end_ts"]}')
        
        snap_a = load_snapshot(conn, run_id_a)
        snap_b = load_snapshot(conn, run_id_b)
        
        mismatches = []
        
        if snap_a['total_triangles'] != snap_b['total_triangles']:
            mismatches.append(f'total_triangles: {snap_a["total_triangles"]} != {snap_b["total_triangles"]}')
        
        if snap_a['bull_count'] != snap_b['bull_count']:
            mismatches.append(f'bull_count: {snap_a["bull_count"]} != {snap_b["bull_count"]}')
        
        if snap_a['bear_count'] != snap_b['bear_count']:
            mismatches.append(f'bear_count: {snap_a["bear_count"]} != {snap_b["bear_count"]}')
        
        if snap_a['ym_counts_hash'] != snap_b['ym_counts_hash']:
            mismatches.append(f'ym_counts_hash: {snap_a["ym_counts_hash"]} != {snap_b["ym_counts_hash"]}')
        
        if snap_a['direction_counts_hash'] != snap_b['direction_counts_hash']:
            mismatches.append(f'direction_counts_hash: {snap_a["direction_counts_hash"]} != {snap_b["direction_counts_hash"]}')
        
        if snap_a['core_fingerprint_hash'] != snap_b['core_fingerprint_hash']:
            mismatches.append(f'core_fingerprint_hash: {snap_a["core_fingerprint_hash"]} != {snap_b["core_fingerprint_hash"]}')
        
        if mismatches:
            print('\nSnapshot comparison: FAIL')
            for mismatch in mismatches:
                print(f'  {mismatch}')
            
            print('\nFirst 20 row-level differences:')
            diffs = get_row_diffs(conn, run_id_a, run_id_b)
            if diffs:
                for symbol, ts, direction in diffs:
                    print(f'  {symbol} | {ts} | {direction}')
            else:
                print('  (No row-level differences found - hash collision or aggregation mismatch)')
            
            sys.exit(1)
        
        print('\nSnapshot comparison: PASS')
        print(f'  total_triangles: {snap_a["total_triangles"]}')
        print(f'  bull_count: {snap_a["bull_count"]}')
        print(f'  bear_count: {snap_a["bear_count"]}')
        print(f'  ym_counts_hash: {snap_a["ym_counts_hash"]}')
        print(f'  direction_counts_hash: {snap_a["direction_counts_hash"]}')
        print(f'  core_fingerprint_hash: {snap_a["core_fingerprint_hash"]}')
        
        print('\nREPRODUCIBILITY: PASS')
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()

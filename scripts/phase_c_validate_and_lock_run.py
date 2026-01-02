#!/usr/bin/env python3
"""
Phase C Corpus Validator - Validate corpus run integrity and optionally lock
Usage: python scripts/phase_c_validate_and_lock_run.py RUN_ID [--lock]
"""

import os
import sys
import argparse
import hashlib
import psycopg2


def parse_args():
    parser = argparse.ArgumentParser(description='Validate and optionally lock corpus run')
    parser.add_argument('run_id', help='Run ID (UUID)')
    parser.add_argument('--lock', action='store_true', help='Lock the run after validation')
    return parser.parse_args()


def get_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError('DATABASE_URL environment variable not set')
    return psycopg2.connect(database_url)


def compute_sha256(content):
    return hashlib.sha256(content.encode()).hexdigest()


def fail(message):
    print(f'VALIDATION FAILED: {message}')
    sys.exit(1)


def validate_run(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT status, start_ts, end_ts, symbol, bars_fingerprint, logic_version
            FROM signal_corpus_runs
            WHERE run_id = %s
        """, (run_id,))
        row = cur.fetchone()
        if not row:
            fail(f'Run {run_id} does not exist')
        
        status, start_ts, end_ts, symbol, bars_fingerprint, logic_version = row
        return {
            'status': status,
            'start_ts': start_ts,
            'end_ts': end_ts,
            'symbol': symbol,
            'bars_fingerprint': bars_fingerprint,
            'logic_version': logic_version
        }


def validate_batches(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*), COUNT(*) FILTER (WHERE status = 'COMPLETE')
            FROM signal_corpus_batches
            WHERE run_id = %s
        """, (run_id,))
        total, complete = cur.fetchone()
        
        if total == 0:
            fail('No batches found')
        
        if complete != total:
            fail(f'Not all batches complete: {complete}/{total}')
        
        return total


def validate_range(conn, run_id, start_ts, end_ts):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM signal_corpus_triangles
            WHERE run_id = %s AND (ts < %s OR ts >= %s)
        """, (run_id, start_ts, end_ts))
        out_of_range = cur.fetchone()[0]
        
        if out_of_range > 0:
            fail(f'{out_of_range} triangles outside range [{start_ts}, {end_ts})')


def compute_counts(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE direction = 'BULL') as bull,
                COUNT(*) FILTER (WHERE direction = 'BEAR') as bear,
                MIN(ts) as min_ts,
                MAX(ts) as max_ts
            FROM signal_corpus_triangles
            WHERE run_id = %s
        """, (run_id,))
        row = cur.fetchone()
        
        if row[0] == 0:
            fail('No triangles found in corpus - cannot validate empty corpus')
        
        return {
            'total_triangles': row[0],
            'bull_count': row[1],
            'bear_count': row[2],
            'min_ts': row[3],
            'max_ts': row[4]
        }


def compute_ym_counts_hash(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                TO_CHAR(DATE_TRUNC('month', ts), 'YYYY-MM') as ym,
                COUNT(*) as cnt
            FROM signal_corpus_triangles
            WHERE run_id = %s
            GROUP BY DATE_TRUNC('month', ts)
            ORDER BY DATE_TRUNC('month', ts) ASC
        """, (run_id,))
        rows = cur.fetchall()
        
        if not rows:
            return compute_sha256('')
        
        parts = [f'{ym}:{cnt}' for ym, cnt in rows]
        content = '|'.join(parts)
        return compute_sha256(content)


def compute_direction_counts_hash(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT direction, COUNT(*)
            FROM signal_corpus_triangles
            WHERE run_id = %s
            GROUP BY direction
            ORDER BY direction
        """, (run_id,))
        rows = cur.fetchall()
        
        parts = [f'{direction}:{cnt}' for direction, cnt in rows]
        content = '|'.join(parts)
        return compute_sha256(content)


def compute_core_fingerprint_hash(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT symbol, ts, direction
            FROM signal_corpus_triangles
            WHERE run_id = %s
            ORDER BY symbol, ts, direction
        """, (run_id,))
        rows = cur.fetchall()
        
        if not rows:
            return compute_sha256('')
        
        lines = [f'{symbol}|{ts.isoformat()}|{direction}' for symbol, ts, direction in rows]
        content = '\n'.join(lines)
        return compute_sha256(content)


def compute_integrity_failures(conn, run_id, start_ts, end_ts):
    failures = 0
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*)
            FROM signal_corpus_triangles
            WHERE run_id = %s AND (ts < %s OR ts >= %s)
        """, (run_id, start_ts, end_ts))
        failures += cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*)
            FROM signal_corpus_batches
            WHERE run_id = %s AND status != 'COMPLETE'
        """, (run_id,))
        failures += cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*)
            FROM signal_corpus_triangles
            WHERE run_id = %s AND direction NOT IN ('BULL', 'BEAR')
        """, (run_id,))
        failures += cur.fetchone()[0]
    
    return failures


def write_snapshot(conn, run_id, metrics, hashes):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO signal_corpus_snapshot 
            (run_id, total_triangles, bull_count, bear_count, min_ts, max_ts,
             ym_counts_hash, direction_counts_hash, core_fingerprint_hash, integrity_failures)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE SET
                captured_at = NOW(),
                total_triangles = EXCLUDED.total_triangles,
                bull_count = EXCLUDED.bull_count,
                bear_count = EXCLUDED.bear_count,
                min_ts = EXCLUDED.min_ts,
                max_ts = EXCLUDED.max_ts,
                ym_counts_hash = EXCLUDED.ym_counts_hash,
                direction_counts_hash = EXCLUDED.direction_counts_hash,
                core_fingerprint_hash = EXCLUDED.core_fingerprint_hash,
                integrity_failures = EXCLUDED.integrity_failures
        """, (run_id, metrics['total_triangles'], metrics['bull_count'], metrics['bear_count'],
              metrics['min_ts'], metrics['max_ts'], hashes['ym_counts_hash'],
              hashes['direction_counts_hash'], hashes['core_fingerprint_hash'], 
              metrics['integrity_failures']))
        conn.commit()
    return True


def lock_run(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE signal_corpus_runs
            SET status = 'LOCKED', locked_at = NOW()
            WHERE run_id = %s
        """, (run_id,))
        conn.commit()


def main():
    args = parse_args()
    run_id = args.run_id
    
    conn = get_connection()
    
    try:
        print(f'Validating run_id: {run_id}')
        
        run_info = validate_run(conn, run_id)
        print(f'Run status: {run_info["status"]}')
        print(f'Symbol: {run_info["symbol"]}')
        print(f'Range: {run_info["start_ts"]} to {run_info["end_ts"]}')
        print(f'Bars fingerprint: {run_info["bars_fingerprint"]}')
        print(f'Logic version: {run_info["logic_version"]}')
        
        batch_count = validate_batches(conn, run_id)
        print(f'Batches: {batch_count} (all COMPLETE)')
        
        validate_range(conn, run_id, run_info['start_ts'], run_info['end_ts'])
        print('Range validation: PASS')
        
        counts = compute_counts(conn, run_id)
        print(f'Total triangles: {counts["total_triangles"]}')
        print(f'Bull count: {counts["bull_count"]}')
        print(f'Bear count: {counts["bear_count"]}')
        print(f'Min ts: {counts["min_ts"]}')
        print(f'Max ts: {counts["max_ts"]}')
        
        ym_hash = compute_ym_counts_hash(conn, run_id)
        direction_hash = compute_direction_counts_hash(conn, run_id)
        core_hash = compute_core_fingerprint_hash(conn, run_id)
        
        print(f'YM counts hash: {ym_hash}')
        print(f'Direction counts hash: {direction_hash}')
        print(f'Core fingerprint hash: {core_hash}')
        
        integrity_failures = compute_integrity_failures(conn, run_id, 
                                                       run_info['start_ts'], run_info['end_ts'])
        
        if integrity_failures > 0:
            fail(f'Integrity failures detected: {integrity_failures}')
        
        print(f'Integrity failures: {integrity_failures}')
        
        metrics = {
            'total_triangles': counts['total_triangles'],
            'bull_count': counts['bull_count'],
            'bear_count': counts['bear_count'],
            'min_ts': counts['min_ts'],
            'max_ts': counts['max_ts'],
            'integrity_failures': integrity_failures
        }
        
        hashes = {
            'ym_counts_hash': ym_hash,
            'direction_counts_hash': direction_hash,
            'core_fingerprint_hash': core_hash
        }
        
        snapshot_written = write_snapshot(conn, run_id, metrics, hashes)
        if not snapshot_written:
            fail('Failed to write snapshot')
        
        print('Snapshot written to signal_corpus_snapshot')
        
        if args.lock:
            if run_info['status'] != 'COMPLETE':
                fail(f'Cannot lock run with status {run_info["status"]} - must be COMPLETE')
            
            if integrity_failures != 0:
                fail(f'Cannot lock run with {integrity_failures} integrity failures')
            
            if run_info['status'] == 'LOCKED':
                print(f'Run {run_id} already LOCKED')
            else:
                if not snapshot_written:
                    fail('Cannot lock run - snapshot write failed')
                
                lock_run(conn, run_id)
                print(f'LOCKED run_id={run_id}')
        
        print('VALIDATION PASSED')
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()

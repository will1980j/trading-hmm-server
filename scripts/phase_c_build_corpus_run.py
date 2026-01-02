#!/usr/bin/env python3
"""
Phase C Corpus Builder - Generate run-scoped triangle corpus from clean OHLCV data
Usage: python scripts/phase_c_build_corpus_run.py SYMBOL START_DATE END_DATE --logic-version LOGIC --batch-days N [--warmup W] [--preload-start-ts ISO]
"""

import os
import sys
import argparse
import hashlib
import pytz
from datetime import datetime, timedelta
import psycopg2

from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg
from market_parity.htf_bias import HTFBiasEngine
from market_parity.engulfing import Bar, detect_engulfing
from market_parity.signal_generation import generate_signals


def parse_args():
    parser = argparse.ArgumentParser(description='Build Phase C signal corpus')
    parser.add_argument('symbol', help='Symbol (e.g., GLBX.MDP3:NQ)')
    parser.add_argument('start_date', help='Start date YYYY-MM-DD')
    parser.add_argument('end_date', help='End date YYYY-MM-DD')
    parser.add_argument('--logic-version', required=True, help='Logic version identifier')
    parser.add_argument('--batch-days', type=int, default=7, help='Batch size in days (default: 7)')
    parser.add_argument('--warmup', type=int, default=5, help='Warmup days (default: 5)')
    parser.add_argument('--preload-start-ts', help='Preload start timestamp ISO format (default: start_date - warmup days at 23:00Z)')
    parser.add_argument('--resume-run-id', help='Resume existing run ID instead of creating new run')
    return parser.parse_args()


def get_connection():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError('DATABASE_URL environment variable not set')
    return psycopg2.connect(database_url)


def compute_sha256(*parts):
    content = '|'.join(str(p) for p in parts)
    return hashlib.sha256(content.encode()).hexdigest()


def verify_clean_table(conn, symbol, start_ts, end_ts):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT MIN(ts), MAX(ts), COUNT(*)
            FROM market_bars_ohlcv_1m_clean
            WHERE symbol = %s AND ts >= %s AND ts < %s
        """, (symbol, start_ts, end_ts))
        row = cur.fetchone()
        if not row or row[2] == 0:
            raise ValueError(f'No data in market_bars_ohlcv_1m_clean for {symbol} in range {start_ts} to {end_ts}')
        return row[0], row[1], row[2]


def create_run(conn, symbol, timeframe, start_ts, end_ts, bars_min_ts, bars_max_ts, bars_rowcount, 
               bars_fingerprint, logic_version, git_sha, config_fingerprint):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO signal_corpus_runs 
            (symbol, timeframe, start_ts, end_ts, bars_table, bars_min_ts, bars_max_ts, 
             bars_rowcount, bars_fingerprint, logic_version, git_sha, config_fingerprint, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING run_id
        """, (symbol, timeframe, start_ts, end_ts, 'market_bars_ohlcv_1m_clean',
              bars_min_ts, bars_max_ts, bars_rowcount, bars_fingerprint, 
              logic_version, git_sha, config_fingerprint, 'RUNNING'))
        run_id = cur.fetchone()[0]
        conn.commit()
        return run_id


def create_batches(conn, run_id, start_ts, end_ts, batch_days):
    """Create batches with half-open intervals [batch_start, batch_end)"""
    batches = []
    current = start_ts
    while current < end_ts:
        batch_end = min(current + timedelta(days=batch_days), end_ts)
        batches.append((current, batch_end))
        current = batch_end
    
    with conn.cursor() as cur:
        values = [(run_id, bs, be, 'PENDING') for bs, be in batches]
        for val in values:
            cur.execute("""
                INSERT INTO signal_corpus_batches (run_id, batch_start, batch_end, status)
                VALUES (%s, %s, %s, %s)
            """, val)
        conn.commit()
    
    return batches


def load_existing_run(conn, run_id, symbol, start_ts, end_ts, logic_version):
    """Load and verify existing run for resume"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT symbol, start_ts, end_ts, logic_version, status
            FROM signal_corpus_runs
            WHERE run_id = %s
        """, (run_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f'Run {run_id} does not exist')
        
        run_symbol, run_start_ts, run_end_ts, run_logic_version, run_status = row
        
        if run_status == 'LOCKED':
            raise ValueError(f'Run {run_id} is LOCKED - cannot resume')
        
        if run_symbol != symbol:
            raise ValueError(f'Symbol mismatch: run has {run_symbol}, provided {symbol}')
        
        if run_start_ts != start_ts:
            raise ValueError(f'start_ts mismatch: run has {run_start_ts}, provided {start_ts}')
        
        if run_end_ts != end_ts:
            raise ValueError(f'end_ts mismatch: run has {run_end_ts}, provided {end_ts}')
        
        if run_logic_version != logic_version:
            raise ValueError(f'logic_version mismatch: run has {run_logic_version}, provided {logic_version}')
        
        return run_id


def get_pending_batches(conn, run_id):
    """Get pending batches for resume"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT batch_start, batch_end
            FROM signal_corpus_batches
            WHERE run_id = %s AND status = 'PENDING'
            ORDER BY batch_start ASC
        """, (run_id,))
        return cur.fetchall()


def mark_batch_failed(conn, run_id, batch_start, batch_end, error_msg):
    """Mark batch as failed"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE signal_corpus_batches
            SET status = 'FAILED', error = %s, finished_at = NOW()
            WHERE run_id = %s AND batch_start = %s AND batch_end = %s
        """, (error_msg, run_id, batch_start, batch_end))
        conn.commit()


def mark_run_failed(conn, run_id):
    """Mark run as failed"""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE signal_corpus_runs
            SET status = 'FAILED'
            WHERE run_id = %s
        """, (run_id,))
        conn.commit()


def fetch_bars(conn, symbol, start_ts, end_ts):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT ts, open, high, low, close, volume
            FROM market_bars_ohlcv_1m_clean
            WHERE symbol = %s AND ts >= %s AND ts < %s
            ORDER BY ts ASC
        """, (symbol, start_ts, end_ts))
        return cur.fetchall()


def process_batch(conn, run_id, symbol, batch_start, batch_end, warmup_days, logic_version):
    """Process one batch [batch_start, batch_end) using bar-by-bar computation"""
    
    preload_date = (batch_start - timedelta(days=warmup_days)).date()
    preload_start = datetime.combine(preload_date, datetime.min.time()).replace(hour=23, minute=0, second=0, tzinfo=pytz.UTC)
    
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE signal_corpus_batches
            SET status = 'RUNNING', started_at = NOW()
            WHERE run_id = %s AND batch_start = %s AND batch_end = %s
        """, (run_id, batch_start, batch_end))
        conn.commit()
    
    bars = fetch_bars(conn, symbol, preload_start, batch_end)
    
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE signal_corpus_batches
            SET bars_rowcount = %s
            WHERE run_id = %s AND batch_start = %s AND batch_end = %s
        """, (len(bars), run_id, batch_start, batch_end))
        conn.commit()
    
    if not bars:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE signal_corpus_batches
                SET status = 'COMPLETE', signals_emitted = 0, finished_at = NOW()
                WHERE run_id = %s AND batch_start = %s AND batch_end = %s
            """, (run_id, batch_start, batch_end))
            conn.commit()
        return 0
    
    bias_engine = BiasEngineFvgIfvg()
    htf_engine = HTFBiasEngine()
    
    htf_aligned_only = False
    require_engulfing = False
    require_sweep_engulfing = False
    
    bias_prev = "Neutral"
    
    triangles_to_insert = []
    
    for i, bar in enumerate(bars):
        ts, o, h, l, c, v = bar
        o_f, h_f, l_f, c_f = float(o), float(h), float(l), float(c)
        v_f = float(v) if v is not None else 0.0
        
        bar_dict = {'ts': ts, 'open': o_f, 'high': h_f, 'low': l_f, 'close': c_f}
        
        bias = bias_engine.update(bar_dict, debug=False)
        
        htf_biases = htf_engine.update_ltf_bar(bar_dict)
        htf_5m_bias = htf_biases['m5_bias']
        htf_15m_bias = htf_biases['m15_bias']
        htf_1h_bias = htf_biases['h1_bias']
        
        htf_bullish = (htf_5m_bias == 'Bullish' and htf_15m_bias == 'Bullish' and htf_1h_bias == 'Bullish')
        htf_bearish = (htf_5m_bias == 'Bearish' and htf_15m_bias == 'Bearish' and htf_1h_bias == 'Bearish')
        
        if i > 0:
            prev_bar_data = bars[i-1]
            prev_o, prev_h, prev_l, prev_c = float(prev_bar_data[1]), float(prev_bar_data[2]), float(prev_bar_data[3]), float(prev_bar_data[4])
            
            prev_bar_obj = Bar(prev_o, prev_h, prev_l, prev_c)
            curr_bar_obj = Bar(o_f, h_f, l_f, c_f)
            engulfing = detect_engulfing(prev_bar_obj, curr_bar_obj)
            
            signal_result = generate_signals(
                bias=bias,
                bias_prev=bias_prev,
                htf_bullish=htf_bullish,
                htf_bearish=htf_bearish,
                bullish_engulfing=engulfing.bullish,
                bearish_engulfing=engulfing.bearish,
                bullish_sweep_engulfing=engulfing.bullish_sweep,
                bearish_sweep_engulfing=engulfing.bearish_sweep,
                htf_aligned_only=htf_aligned_only,
                require_engulfing=require_engulfing,
                require_sweep_engulfing=require_sweep_engulfing
            )
            
            if ts >= batch_start and ts < batch_end:
                if signal_result['show_bull_triangle']:
                    triangles_to_insert.append((run_id, symbol, ts, 'BULL', 'market_bars_ohlcv_1m_clean', logic_version))
                if signal_result['show_bear_triangle']:
                    triangles_to_insert.append((run_id, symbol, ts, 'BEAR', 'market_bars_ohlcv_1m_clean', logic_version))
        
        bias_prev = bias
    
    inserted = 0
    if triangles_to_insert:
        with conn.cursor() as cur:
            for triangle in triangles_to_insert:
                cur.execute("""
                    INSERT INTO signal_corpus_triangles 
                    (run_id, symbol, ts, direction, source_table, logic_version)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id, symbol, ts, direction) DO NOTHING
                    RETURNING 1
                """, triangle)
                if cur.fetchone():
                    inserted += 1
            conn.commit()
    
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE signal_corpus_batches
            SET status = 'COMPLETE', signals_emitted = %s, finished_at = NOW()
            WHERE run_id = %s AND batch_start = %s AND batch_end = %s
        """, (inserted, run_id, batch_start, batch_end))
        conn.commit()
    
    return inserted


def complete_run(conn, run_id):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE signal_corpus_runs
            SET status = 'COMPLETE', completed_at = NOW()
            WHERE run_id = %s
        """, (run_id,))
        conn.commit()


def main():
    args = parse_args()
    
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    
    start_ts = start_date.replace(hour=0, minute=0, second=0, tzinfo=pytz.UTC)
    end_ts = end_date.replace(hour=23, minute=59, second=59, tzinfo=pytz.UTC)
    
    if args.preload_start_ts:
        preload_str = args.preload_start_ts.replace('Z', '+00:00')
        preload_start_ts = datetime.fromisoformat(preload_str)
        if preload_start_ts.tzinfo is None:
            preload_start_ts = preload_start_ts.replace(tzinfo=pytz.UTC)
    else:
        preload_date = (start_date - timedelta(days=args.warmup)).date()
        preload_start_ts = datetime.combine(preload_date, datetime.min.time()).replace(hour=23, minute=0, second=0, tzinfo=pytz.UTC)
    
    git_sha = os.environ.get('GIT_SHA', 'unknown')
    config_fingerprint = compute_sha256(args.logic_version, args.warmup, args.batch_days, 
                                       preload_start_ts.isoformat(), start_ts.isoformat(), end_ts.isoformat())
    
    conn = get_connection()
    
    try:
        bars_min_ts, bars_max_ts, bars_rowcount = verify_clean_table(conn, args.symbol, preload_start_ts, end_ts)
        bars_fingerprint = compute_sha256(args.symbol, 'market_bars_ohlcv_1m_clean', 
                                         bars_min_ts.isoformat(), bars_max_ts.isoformat(), bars_rowcount)
        
        if args.resume_run_id:
            run_id = load_existing_run(conn, args.resume_run_id, args.symbol, start_ts, end_ts, args.logic_version)
            print(f'Resuming run_id: {run_id}')
            batches = get_pending_batches(conn, run_id)
            print(f'Found {len(batches)} pending batches')
        else:
            run_id = create_run(conn, args.symbol, '1m', start_ts, end_ts, bars_min_ts, bars_max_ts, 
                               bars_rowcount, bars_fingerprint, args.logic_version, git_sha, config_fingerprint)
            print(f'Created run_id: {run_id}')
            batches = create_batches(conn, run_id, start_ts, end_ts, args.batch_days)
            print(f'Created {len(batches)} batches')
        
        cumulative = 0
        for batch_start, batch_end in batches:
            max_retries = 5
            inserted = None
            
            for attempt in range(max_retries):
                try:
                    inserted = process_batch(conn, run_id, args.symbol, batch_start, batch_end, 
                                           args.warmup, args.logic_version)
                    break
                except psycopg2.OperationalError as e:
                    if attempt < max_retries - 1:
                        print(f'Connection error (attempt {attempt + 1}/{max_retries}), reconnecting...')
                        try:
                            conn.close()
                        except:
                            pass
                        conn = get_connection()
                    else:
                        error_msg = f'Max retries exceeded: {str(e)}'
                        print(f'FAILED batch {batch_start} to {batch_end}: {error_msg}')
                        mark_batch_failed(conn, run_id, batch_start, batch_end, error_msg)
                        mark_run_failed(conn, run_id)
                        print(f'Run {run_id} marked FAILED')
                        sys.exit(1)
            
            if inserted is not None:
                cumulative += inserted
                print(f'Batch {batch_start} to {batch_end}: inserted {inserted}, cumulative {cumulative}')
        
        complete_run(conn, run_id)
        print(f'Run {run_id} COMPLETE with {cumulative} total triangles')
        
    finally:
        conn.close()


if __name__ == '__main__':
    main()

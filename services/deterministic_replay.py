"""Deterministic replay with active_dataset_versions scoping"""

import os, psycopg2, hashlib, json

def replay_bars(dataset_version_id: str, symbol: str, start_date: str, end_date: str) -> dict:
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM data_ingest_runs WHERE dataset_version_id = %s", (dataset_version_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise ValueError(f'Dataset version not found: {dataset_version_id}')
    
    cursor.execute("SELECT dataset_version_id FROM active_dataset_versions WHERE symbol = %s", (symbol,))
    active_row = cursor.fetchone()
    
    if not active_row:
        cursor.close()
        conn.close()
        raise ValueError(f'Symbol {symbol} not in active_dataset_versions')
    
    active_version = active_row[0]
    
    if active_version != dataset_version_id:
        cursor.close()
        conn.close()
        raise ValueError(f'Version mismatch: requested {dataset_version_id}, active is {active_version}')
    
    cursor.execute("""
        SELECT ts, open, high, low, close, volume FROM market_bars_ohlcv_1m
        WHERE symbol = %s AND ts >= %s::timestamptz AND ts <= %s::timestamptz
        ORDER BY ts ASC
    """, (symbol, start_date, end_date))
    
    bars = cursor.fetchall()
    cursor.close()
    conn.close()
    
    hasher = hashlib.sha256()
    for bar in bars:
        ts_iso = bar[0].isoformat()
        o = f'{float(bar[1]):.6f}'
        h = f'{float(bar[2]):.6f}'
        l = f'{float(bar[3]):.6f}'
        c = f'{float(bar[4]):.6f}'
        v = int(bar[5]) if bar[5] else 0
        bar_str = f'{ts_iso}|{o}|{h}|{l}|{c}|{v}'
        hasher.update(bar_str.encode())
    
    return {
        'dataset_version_id': dataset_version_id,
        'version_scoped': True,
        'symbol': symbol,
        'date_range': f'{start_date} to {end_date}',
        'bar_count': len(bars),
        'output_hash': hasher.hexdigest()
    }

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 5:
        print('Usage: python services/deterministic_replay.py <version_id> <symbol> <start> <end>')
        exit(1)
    result = replay_bars(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(json.dumps(result, indent=2))

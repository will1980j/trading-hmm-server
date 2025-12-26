"""Gap detection - expected vs actual bars"""

import os, psycopg2, sys
from datetime import datetime
from zoneinfo import ZoneInfo
sys.path.append('.')
from config.trading_calendar import expected_bar_timestamps_utc

def detect_gaps(symbol: str, start_date: str, end_date: str) -> dict:
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError('DATABASE_URL not set')
    
    utc_tz = ZoneInfo('UTC')
    start_utc = datetime.fromisoformat(start_date).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc_tz)
    end_utc = datetime.fromisoformat(end_date).replace(hour=23, minute=59, second=0, microsecond=0, tzinfo=utc_tz)
    
    expected = set(expected_bar_timestamps_utc(start_utc, end_utc))
    expected_count = len(expected)
    
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ts FROM market_bars_ohlcv_1m
        WHERE symbol = %s AND ts >= %s AND ts <= %s
        ORDER BY ts ASC
    """, (symbol, start_utc, end_utc))
    
    actual = set()
    for row in cursor.fetchall():
        ts = row[0]
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=utc_tz)
        actual.add(ts)
    
    cursor.close()
    conn.close()
    
    missing = expected - actual
    missing_sorted = sorted(list(missing))
    
    return {
        'symbol': symbol,
        'date_range': f'{start_date} to {end_date}',
        'expected_count': expected_count,
        'actual_count': len(actual),
        'missing_count': len(missing),
        'missing_sample': [ts.isoformat() for ts in missing_sorted[:50]],
        'completeness_pct': round((len(actual) / expected_count * 100), 2) if expected_count > 0 else 0
    }

if __name__ == '__main__':
    import json
    result = detect_gaps('GLBX.MDP3:NQ', '2024-01-02', '2024-01-03')
    print(json.dumps(result, indent=2))

#!/usr/bin/env python3
"""Write remaining Phase A files to disk"""

files = []

# File 2: config/cme_holidays.json
with open('config/cme_holidays.json', 'w') as f:
    f.write('''{
  "source": "CME Group official holidays",
  "last_updated": "2025-12-26",
  "holidays": [
    "2019-01-01", "2019-01-21", "2019-02-18", "2019-04-19", "2019-05-27",
    "2019-07-04", "2019-09-02", "2019-11-28", "2019-12-25",
    "2020-01-01", "2020-01-20", "2020-02-17", "2020-04-10", "2020-05-25",
    "2020-07-03", "2020-09-07", "2020-11-26", "2020-12-25",
    "2021-01-01", "2021-01-18", "2021-02-15", "2021-04-02", "2021-05-31",
    "2021-07-05", "2021-09-06", "2021-11-25", "2021-12-24",
    "2022-01-17", "2022-02-21", "2022-04-15", "2022-05-30",
    "2022-07-04", "2022-09-05", "2022-11-24", "2022-12-26",
    "2023-01-02", "2023-01-16", "2023-02-20", "2023-04-07", "2023-05-29",
    "2023-07-04", "2023-09-04", "2023-11-23", "2023-12-25",
    "2024-01-01", "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27",
    "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25",
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
    "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25",
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25"
  ]
}
''')
files.append('config/cme_holidays.json')

# File 3: services/gap_detector_phase_a.py
with open('services/gap_detector_phase_a.py', 'w') as f:
    f.write('''"""Gap detection - expected vs actual bars"""

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
''')
files.append('services/gap_detector_phase_a.py')

# Continue with remaining files...
print('✅ Created files:')
for f in files:
    size = open(f, 'rb').read()
    print(f'   WROTE: {f} ({len(size)} bytes)')

#!/usr/bin/env python3
"""Create all Phase A lock files"""

from pathlib import Path

files_created = []

# Ensure directories exist
Path('config').mkdir(exist_ok=True)
Path('services').mkdir(exist_ok=True)
Path('database').mkdir(exist_ok=True)
Path('scripts').mkdir(exist_ok=True)
Path('tests').mkdir(exist_ok=True)

# File 1: config/trading_calendar.py
content1 = '''"""
CME Equity Index Futures Trading Calendar
Trading day: 17:00 CT to 16:00 CT next day with maintenance break
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from pathlib import Path

def load_holidays():
    holiday_file = Path(__file__).parent / 'cme_holidays.json'
    if not holiday_file.exists():
        return []
    with open(holiday_file, 'r') as f:
        data = json.load(f)
    return data.get('holidays', [])

def is_holiday(date_ct: datetime) -> bool:
    holidays = load_holidays()
    date_str = date_ct.strftime('%Y-%m-%d')
    return date_str in holidays

def is_market_open(dt_utc: datetime) -> bool:
    ct_tz = ZoneInfo('US/Central')
    dt_ct = dt_utc.astimezone(ct_tz)
    
    if is_holiday(dt_ct):
        return False
    
    weekday = dt_ct.weekday()
    hour = dt_ct.hour
    
    if weekday == 4 and hour >= 16:
        return False
    if weekday == 5:
        return False
    if weekday == 6 and hour < 17:
        return False
    if hour == 16:
        return False
    
    return True

def expected_bar_timestamps_utc(start_utc: datetime, end_utc: datetime, freq='1min'):
    if freq != '1min':
        raise ValueError('Only 1min frequency supported')
    
    current = start_utc
    while current <= end_utc:
        if is_market_open(current):
            yield current
        current += timedelta(minutes=1)
'''

with open('config/trading_calendar.py', 'w', encoding='utf-8') as f:
    f.write(content1)
files_created.append(('config/trading_calendar.py', len(content1)))

# File 2: config/cme_holidays.json
content2 = '''{
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
'''

with open('config/cme_holidays.json', 'w', encoding='utf-8') as f:
    f.write(content2)
files_created.append(('config/cme_holidays.json', len(content2)))

# File 3: services/gap_detector_phase_a.py
content3 = '''"""
Gap detection service - computes expected vs actual bars
"""

import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
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
        SELECT ts
        FROM market_bars_ohlcv_1m
        WHERE symbol = %s
          AND ts >= %s
          AND ts <= %s
        ORDER BY ts ASC
    """, (symbol, start_utc, end_utc))
    
    actual_rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    actual = set()
    for row in actual_rows:
        ts = row[0]
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=utc_tz)
        actual.add(ts)
    
    actual_count = len(actual)
    missing = expected - actual
    missing_sorted = sorted(list(missing))
    
    return {
        'symbol': symbol,
        'date_range': f'{start_date} to {end_date}',
        'expected_count': expected_count,
        'actual_count': actual_count,
        'missing_count': len(missing),
        'missing_sample': [ts.isoformat() for ts in missing_sorted[:50]],
        'completeness_pct': round((actual_count / expected_count * 100), 2) if expected_count > 0 else 0
    }

if __name__ == '__main__':
    import json
    result = detect_gaps('GLBX.MDP3:NQ', '2024-01-02', '2024-01-03')
    print(json.dumps(result, indent=2))
'''

with open('services/gap_detector_phase_a.py', 'w', encoding='utf-8') as f:
    f.write(content3)
files_created.append(('services/gap_detector_phase_a.py', len(content3)))

# File 4: services/deterministic_replay.py
content4 = '''"""
Deterministic replay service
Emits bars for dataset version + date range with hash validation
"""

import os
import psycopg2
import hashlib
import json

def introspect_schema():
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'market_bars_ohlcv_1m'
          AND column_name = 'dataset_version_id'
    """)
    
    has_col = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    
    return has_col

def replay_bars(dataset_version_id: str, symbol: str, start_date: str, end_date: str) -> dict:
    database_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, vendor, dataset, file_sha256
        FROM data_ingest_runs
        WHERE dataset_version_id = %s
    """, (dataset_version_id,))
    
    run = cursor.fetchone()
    if not run:
        cursor.close()
        conn.close()
        raise ValueError(f'Dataset version not found: {dataset_version_id}')
    
    has_version_col = introspect_schema()
    
    if not has_version_col:
        cursor.close()
        conn.close()
        raise ValueError('market_bars_ohlcv_1m.dataset_version_id column missing')
    
    cursor.execute("""
        SELECT ts, open, high, low, close, volume
        FROM market_bars_ohlcv_1m
        WHERE dataset_version_id = %s
          AND symbol = %s
          AND ts >= %s::timestamptz
          AND ts <= %s::timestamptz
        ORDER BY ts ASC
    """, (dataset_version_id, symbol, start_date, end_date))
    
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
    
    output_hash = hasher.hexdigest()
    
    return {
        'dataset_version_id': dataset_version_id,
        'version_scoped': True,
        'symbol': symbol,
        'date_range': f'{start_date} to {end_date}',
        'bar_count': len(bars),
        'output_hash': output_hash
    }

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 5:
        print('Usage: python services/deterministic_replay.py <version_id> <symbol> <start> <end>')
        exit(1)
    
    result = replay_bars(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(json.dumps(result, indent=2))
'''

with open('services/deterministic_replay.py', 'w', encoding='utf-8') as f:
    f.write(content4)
files_created.append(('services/deterministic_replay.py', len(content4)))

print('✅ Created 4 files')
for path, size in files_created:
    print(f'   WROTE: {path} ({size} bytes)')
"
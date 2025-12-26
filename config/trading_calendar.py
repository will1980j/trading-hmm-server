"""
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

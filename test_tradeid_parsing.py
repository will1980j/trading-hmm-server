#!/usr/bin/env python3
"""Test the trade_id parsing logic locally"""

# Test trade IDs from Railway's database
test_trade_ids = [
    '20251130_195200000_BEARISH',
    '20251201_001100000_BULLISH',
    'RAILWAY_TEST_20251201_999999_BULLISH',
    'TEST_20251201_123456_BULLISH',
]

print("=== TESTING TRADE_ID PARSING ===\n")

for trade_id in test_trade_ids:
    print(f"Trade ID: {trade_id}")
    
    signal_date = None
    signal_time = None
    
    try:
        parts = trade_id.split('_')
        print(f"  Parts: {parts}")
        if len(parts) >= 2:
            date_str = parts[0]  # YYYYMMDD
            time_str = parts[1][:6]  # HHMMSS (strip trailing 000)
            print(f"  date_str: '{date_str}', time_str: '{time_str}'")
            
            # Check if date_str looks like a date (8 digits)
            if len(date_str) == 8 and date_str.isdigit():
                signal_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                signal_time = f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
            else:
                print(f"  WARNING: date_str '{date_str}' doesn't look like YYYYMMDD")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print(f"  Result: signal_date={signal_date}, signal_time={signal_time}")
    print()

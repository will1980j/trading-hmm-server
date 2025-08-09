#!/usr/bin/env python3
"""
Upload 96 trades to Railway database
"""

import requests
import json

# Your 96 trades data
trades_data = [
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 2},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 23},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 7},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 8},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 7},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "LONDON", "breakeven": True, "rScore": 9},
    {"date": "2024-08-06", "bias": "SHORT", "session": "LONDON", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 2},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 5},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 4},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 3},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 35},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK AM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK AM", "breakeven": True, "rScore": 2},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK AM", "breakeven": True, "rScore": 20},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK AM", "breakeven": True, "rScore": 4},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK AM", "breakeven": True, "rScore": 31},
    {"date": "2024-08-06", "bias": "LONG", "session": "NY LUNCH", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NY LUNCH", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NY LUNCH", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NY LUNCH", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": True, "rScore": 46},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": True, "rScore": 3},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": True, "rScore": 2},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-06", "bias": "LONG", "session": "NEW YORK PM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 2},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "LONDON", "breakeven": True, "rScore": 1},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 6},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 2},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 146},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 6},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 28},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "LONDON", "breakeven": True, "rScore": 43},
    {"date": "2024-08-07", "bias": "LONG", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "NY PRE MARKET", "breakeven": True, "rScore": 7},
    {"date": "2024-08-07", "bias": "LONG", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "LONG", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NY PRE MARKET", "breakeven": True, "rScore": 2},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": True, "rScore": 3},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": True, "rScore": 9},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": True, "rScore": 2},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK AM", "breakeven": True, "rScore": 3},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NY LUNCH", "breakeven": True, "rScore": 1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NY LUNCH", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NY LUNCH", "breakeven": True, "rScore": 8},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": True, "rScore": 6},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": False, "rScore": -1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": True, "rScore": 2},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": True, "rScore": 3},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": True, "rScore": 1},
    {"date": "2024-08-07", "bias": "SHORT", "session": "NEW YORK PM", "breakeven": False, "rScore": -1}
]

def upload_trades():
    url = "https://web-production-cd33.up.railway.app/webhook"
    
    uploaded_count = 0
    failed_count = 0
    
    for i, trade in enumerate(trades_data):
        try:
            payload = {
                "symbol": "NQ1!",
                "signal_type": trade["bias"],
                "entry_price": 0,
                "confidence": abs(trade["rScore"]) / 10.0 if trade["rScore"] != 0 else 0.5,
                "reason": f"{trade['session']} - {trade['rScore']}R - {trade['date']}"
            }
            
            response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                uploaded_count += 1
                if (i + 1) % 10 == 0:
                    print(f"Uploaded {i + 1}/96 trades...")
            else:
                failed_count += 1
                
        except Exception as e:
            failed_count += 1
    
    print(f"SUCCESS: Uploaded {uploaded_count}/96 trades, {failed_count} failed")

if __name__ == "__main__":
    print("Uploading 96 trades to database...")
    upload_trades()
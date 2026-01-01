#!/usr/bin/env python3
"""
Signal Metrics V1 Backfill - Compute MFE/MAE from Databento OHLCV
"""
import os, sys, psycopg2, argparse
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--symbol', default='GLBX.MDP3:NQ')
parser.add_argument('--limit', type=int, default=5000)
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--trade-id')
args = parser.parse_args()

conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cursor = conn.cursor()

# Select eligible trades
where = "WHERE entry_price IS NOT NULL AND stop_loss IS NOT NULL AND entry_bar_open_ts IS NOT NULL AND exit_bar_open_ts IS NOT NULL"
if args.trade_id:
    where += f" AND trade_id = '{args.trade_id}'"

cursor.execute(f"""
    WITH lifecycle AS (
        SELECT trade_id, 
               MAX(symbol) FILTER (WHERE symbol IS NOT NULL) as symbol,
               (ARRAY_AGG(direction ORDER BY id DESC) FILTER (WHERE direction IS NOT NULL))[1] as direction,
               MIN(entry_bar_open_ts) FILTER (WHERE entry_bar_open_ts IS NOT NULL) as entry_bar_open_ts,
               MAX(exit_bar_open_ts) FILTER (WHERE exit_bar_open_ts IS NOT NULL) as exit_bar_open_ts,
               (ARRAY_AGG(entry_price ORDER BY id DESC) FILTER (WHERE entry_price IS NOT NULL))[1] as entry_price,
               (ARRAY_AGG(stop_loss ORDER BY id DESC) FILTER (WHERE stop_loss IS NOT NULL))[1] as stop_loss
        FROM automated_signals
        GROUP BY trade_id
    )
    SELECT trade_id, symbol, direction, entry_bar_open_ts, exit_bar_open_ts, entry_price, stop_loss
    FROM lifecycle
    {where}
    LIMIT {args.limit}
""")

trades = cursor.fetchall()
print(f"Eligible trades: {len(trades)}")

if args.dry_run:
    for t in trades[:5]:
        print(f"  {t[0]}: entry={t[5]} stop={t[6]} window={t[3]} to {t[4]}")
    cursor.close()
    conn.close()
    sys.exit(0)

computed = 0
skipped = 0
for trade in trades:
    trade_id, symbol, direction, entry_ts, exit_ts, entry_price, stop_loss = trade
    
    # Validation with explicit skip reasons
    if entry_ts is None:
        print(f"SKIP {trade_id} reason=missing_entry_ts")
        skipped += 1
        continue
    
    if exit_ts is None:
        print(f"SKIP {trade_id} reason=missing_exit_ts")
        skipped += 1
        continue
    
    if entry_price is None:
        print(f"SKIP {trade_id} reason=missing_entry_price")
        skipped += 1
        continue
    
    if stop_loss is None:
        print(f"SKIP {trade_id} reason=missing_stop_loss")
        skipped += 1
        continue
    
    # Normalize direction
    if direction == 'LONG':
        direction = 'Bullish'
    elif direction == 'SHORT':
        direction = 'Bearish'
    
    if direction not in ['Bullish', 'Bearish']:
        print(f"SKIP {trade_id} reason=invalid_direction ({direction})")
        skipped += 1
        continue
    
    # Fetch bars
    print(f"FETCH {trade_id}: entry_bar_open_ts={entry_ts}, exit_bar_open_ts={exit_ts}")
    cursor.execute("SELECT ts, high, low FROM market_bars_ohlcv_1m_clean WHERE symbol = %s AND ts >= %s AND ts <= %s ORDER BY ts", (symbol, entry_ts, exit_ts))
    bars = cursor.fetchall()
    print(f"  bars_found_count={len(bars)}")
    
    if len(bars) == 0:
        print(f"SKIP {trade_id} reason=no_bars_found")
        skipped += 1
        continue
    
    # Compute metrics
    entry_price = float(entry_price)
    stop_loss = float(stop_loss)
    risk = abs(entry_price - stop_loss)
    
    if risk <= 0:
        print(f"SKIP {trade_id} reason=invalid_risk_distance ({risk})")
        skipped += 1
        continue
    
    if direction == 'Bullish':
        highest = entry_price
        lowest = entry_price
        mae = 0.0
        be_triggered = False
        be_trigger_ts = None
        
        for i, bar in enumerate(bars):
            bar_ts, high, low = bar[0], float(bar[1]), float(bar[2])
            
            # Check stop hit
            stop_hit = low <= stop_loss
            
            if not stop_hit:
                highest = max(highest, high)
                lowest = min(lowest, low)
                mae = min(mae, (lowest - entry_price) / risk)
                
                # BE check
                if not be_triggered and highest >= entry_price + risk:
                    be_triggered = True
                    be_trigger_ts = bar_ts
        
        mfe_no_be = (highest - entry_price) / risk
        mfe_be = min(mfe_no_be, (highest - entry_price) / risk) if be_triggered else mfe_no_be
    else:
        highest = entry_price
        lowest = entry_price
        mae = 0.0
        be_triggered = False
        be_trigger_ts = None
        
        for i, bar in enumerate(bars):
            bar_ts, high, low = bar[0], float(bar[1]), float(bar[2])
            
            stop_hit = high >= stop_loss
            
            if not stop_hit:
                highest = max(highest, high)
                lowest = min(lowest, low)
                mae = min(mae, (entry_price - highest) / risk)
                
                if not be_triggered and lowest <= entry_price - risk:
                    be_triggered = True
                    be_trigger_ts = bar_ts
        
        mfe_no_be = (entry_price - lowest) / risk
        mfe_be = min(mfe_no_be, (entry_price - lowest) / risk) if be_triggered else mfe_no_be
    
    # Upsert
    try:
        cursor.execute("""
            INSERT INTO signal_metrics_v1 
            (trade_id, symbol, direction_norm, entry_bar_open_ts, exit_bar_open_ts, entry_price, stop_loss, risk_distance,
             no_be_mfe, be_mfe, mae_global_r, highest_high, lowest_low, be_triggered, be_trigger_bar_open_ts,
             computed_window_start_ts, computed_window_end_ts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (trade_id) DO UPDATE SET
                no_be_mfe = EXCLUDED.no_be_mfe,
                be_mfe = EXCLUDED.be_mfe,
                mae_global_r = EXCLUDED.mae_global_r,
                highest_high = EXCLUDED.highest_high,
                lowest_low = EXCLUDED.lowest_low,
                be_triggered = EXCLUDED.be_triggered,
                be_trigger_bar_open_ts = EXCLUDED.be_trigger_bar_open_ts,
                computed_at = NOW()
        """, (trade_id, symbol, direction, entry_ts, exit_ts, entry_price, stop_loss, risk,
              mfe_no_be, mfe_be, mae, highest, lowest, be_triggered, be_trigger_ts, entry_ts, exit_ts))
        
        computed += 1
        print(f"✅ {trade_id}: no_be_mfe={mfe_no_be:.2f}R be_mfe={mfe_be:.2f}R mae={mae:.2f}R")
        if computed % 100 == 0:
            print(f"  Progress: {computed}/{len(trades)}")
    except Exception as e:
        print(f"SKIP {trade_id} reason=db_error:{str(e)}")
        skipped += 1

conn.commit()
print(f"✅ Computed {computed} metrics, Skipped {skipped}")
cursor.close()
conn.close()

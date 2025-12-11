"""
Orphaned Signal Reconciliation Service

Runs in background to update signals that aren't being tracked by the indicator.
Queries database for signals with ENTRY but no recent MFE_UPDATE, calculates
current MFE from market price, and inserts synthetic MFE_UPDATE events.
"""

import psycopg2
import os
import json
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_current_price():
    """Get current NQ price (placeholder - replace with actual price feed)"""
    # TODO: Integrate with Polygon or TradingView price feed
    # For now, return None to skip price-based MFE calculation
    return None

def reconcile_orphaned_signals():
    """Find and update orphaned signals"""
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    cur = conn.cursor()
    
    # Find signals with ENTRY but no MFE_UPDATE in last 10 minutes
    cur.execute("""
        SELECT DISTINCT e.trade_id, e.direction, e.entry_price, e.stop_loss, e.timestamp
        FROM automated_signals e
        WHERE e.event_type = 'ENTRY'
        AND e.trade_id NOT IN (
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE event_type LIKE 'EXIT_%'
        )
        AND e.trade_id NOT IN (
            SELECT DISTINCT trade_id
            FROM automated_signals
            WHERE event_type = 'MFE_UPDATE'
            AND timestamp > NOW() - INTERVAL '10 minutes'
        )
        AND e.timestamp > NOW() - INTERVAL '24 hours'
        LIMIT 50
    """)
    
    orphaned = cur.fetchall()
    print(f"Found {len(orphaned)} orphaned signals")
    
    updated_count = 0
    for row in orphaned:
        trade_id, direction, entry_price, stop_loss, entry_ts = row
        
        if not entry_price or not stop_loss:
            continue
        
        # Calculate risk
        risk = abs(float(entry_price) - float(stop_loss))
        if risk == 0:
            continue
        
        # Get current price (placeholder - would use real price feed)
        current_price = get_current_price()
        if not current_price:
            # Use entry price as fallback (MFE = 0)
            current_price = float(entry_price)
        
        # Calculate MFE (simplified - assumes no extreme tracking)
        if direction in ('LONG', 'Bullish'):
            mfe = (current_price - float(entry_price)) / risk
        else:
            mfe = (float(entry_price) - current_price) / risk
        
        mfe = max(0.0, mfe)  # MFE can't be negative
        
        # Insert synthetic MFE_UPDATE
        cur.execute("""
            INSERT INTO automated_signals (
                trade_id, event_type, be_mfe, no_be_mfe, mae_global_r,
                current_price, timestamp, raw_payload
            ) VALUES (%s, 'MFE_UPDATE', %s, %s, 0.0, %s, NOW(), %s)
        """, (
            trade_id,
            mfe,
            mfe,
            current_price,
            json.dumps({"reconciled": True, "source": "orphan_reconciler"})
        ))
        
        updated_count += 1
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ Updated {updated_count} orphaned signals")
    return updated_count

def run_reconciler_loop():
    """Run reconciler every 5 minutes"""
    print("🔄 Orphaned Signal Reconciler started")
    while True:
        try:
            reconcile_orphaned_signals()
        except Exception as e:
            print(f"❌ Reconciler error: {e}")
        
        time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    # Run once for testing
    reconcile_orphaned_signals()

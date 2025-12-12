"""
Monitor Hybrid Sync System Self-Healing
Tracks signal coverage and gap reduction over time
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def monitor_healing():
    """Monitor the self-healing process"""
    
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    
    print("=" * 80)
    print("HYBRID SYNC SYSTEM - SELF-HEALING MONITOR")
    print("=" * 80)
    print(f"Time: {datetime.now()}")
    print()
    
    # Total active signals
    cur.execute("""
        SELECT COUNT(DISTINCT trade_id) 
        FROM automated_signals 
        WHERE event_type = 'ENTRY'
        AND trade_id NOT IN (
            SELECT DISTINCT trade_id 
            FROM automated_signals 
            WHERE event_type LIKE 'EXIT_%'
        )
    """)
    total_active = cur.fetchone()[0]
    
    # Signals with recent MFE updates (last 5 minutes)
    cur.execute("""
        SELECT COUNT(DISTINCT trade_id)
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
        AND timestamp > NOW() - INTERVAL '5 minutes'
    """)
    recently_updated = cur.fetchone()[0]
    
    # Signals with any MFE update ever
    cur.execute("""
        SELECT COUNT(DISTINCT e.trade_id)
        FROM automated_signals e
        WHERE e.event_type = 'ENTRY'
        AND e.trade_id NOT IN (SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%')
        AND EXISTS (
            SELECT 1 FROM automated_signals m
            WHERE m.trade_id = e.trade_id
            AND m.event_type = 'MFE_UPDATE'
        )
    """)
    ever_updated = cur.fetchone()[0]
    
    # Signals with 0.00R MFE (orphaned)
    cur.execute("""
        SELECT COUNT(DISTINCT e.trade_id)
        FROM automated_signals e
        WHERE e.event_type = 'ENTRY'
        AND e.trade_id NOT IN (SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%')
        AND NOT EXISTS (
            SELECT 1 FROM automated_signals m
            WHERE m.trade_id = e.trade_id
            AND m.event_type = 'MFE_UPDATE'
            AND (m.be_mfe != 0 OR m.no_be_mfe != 0)
        )
    """)
    orphaned = cur.fetchone()[0]
    
    # Signals with missing entry data
    cur.execute("""
        SELECT COUNT(DISTINCT trade_id)
        FROM automated_signals
        WHERE event_type = 'ENTRY'
        AND (entry_price IS NULL OR stop_loss IS NULL)
    """)
    missing_entry_data = cur.fetchone()[0]
    
    # Signals with no MAE
    cur.execute("""
        SELECT COUNT(DISTINCT e.trade_id)
        FROM automated_signals e
        WHERE e.event_type = 'ENTRY'
        AND e.trade_id NOT IN (SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%')
        AND NOT EXISTS (
            SELECT 1 FROM automated_signals m
            WHERE m.trade_id = e.trade_id
            AND m.mae_global_r IS NOT NULL
            AND m.mae_global_r != 0
        )
    """)
    no_mae = cur.fetchone()[0]
    
    # Calculate metrics
    coverage_pct = (ever_updated / total_active * 100) if total_active > 0 else 0
    recent_pct = (recently_updated / total_active * 100) if total_active > 0 else 0
    orphaned_pct = (orphaned / total_active * 100) if total_active > 0 else 0
    
    print(f"📊 SIGNAL COVERAGE")
    print(f"  Total Active Signals: {total_active}")
    print(f"  Ever Updated: {ever_updated} ({coverage_pct:.1f}%)")
    print(f"  Recently Updated (5 min): {recently_updated} ({recent_pct:.1f}%)")
    print()
    
    print(f"⚠️ GAPS DETECTED")
    print(f"  Orphaned (0.00R MFE): {orphaned} ({orphaned_pct:.1f}%)")
    print(f"  Missing Entry Data: {missing_entry_data}")
    print(f"  No MAE: {no_mae}")
    print()
    
    # Health score
    if orphaned_pct < 5:
        health = "🟢 EXCELLENT"
    elif orphaned_pct < 15:
        health = "🟡 GOOD"
    elif orphaned_pct < 30:
        health = "🟠 FAIR"
    else:
        health = "🔴 POOR"
    
    print(f"🏥 SYSTEM HEALTH: {health}")
    print(f"  Coverage: {coverage_pct:.1f}%")
    print(f"  Orphaned: {orphaned_pct:.1f}%")
    print()
    
    # Recent batch activity
    cur.execute("""
        SELECT 
            DATE_TRUNC('minute', timestamp) as minute,
            COUNT(DISTINCT trade_id) as signals_updated
        FROM automated_signals
        WHERE event_type = 'MFE_UPDATE'
        AND timestamp > NOW() - INTERVAL '10 minutes'
        GROUP BY DATE_TRUNC('minute', timestamp)
        ORDER BY minute DESC
        LIMIT 10
    """)
    
    batch_activity = cur.fetchall()
    if batch_activity:
        print(f"📈 RECENT BATCH ACTIVITY (Last 10 minutes)")
        for minute, count in batch_activity:
            print(f"  {minute.strftime('%H:%M')}: {count} signals updated")
    else:
        print(f"⚠️ NO BATCH ACTIVITY in last 10 minutes")
    
    print()
    
    # List orphaned signals (first 10)
    if orphaned > 0:
        cur.execute("""
            SELECT e.trade_id, e.signal_date, e.signal_time, e.session
            FROM automated_signals e
            WHERE e.event_type = 'ENTRY'
            AND e.trade_id NOT IN (SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%')
            AND NOT EXISTS (
                SELECT 1 FROM automated_signals m
                WHERE m.trade_id = e.trade_id
                AND m.event_type = 'MFE_UPDATE'
                AND (m.be_mfe != 0 OR m.no_be_mfe != 0)
            )
            ORDER BY e.timestamp DESC
            LIMIT 10
        """)
        
        orphaned_list = cur.fetchall()
        print(f"🔍 ORPHANED SIGNALS (First 10 of {orphaned}):")
        for trade_id, sig_date, sig_time, session in orphaned_list:
            print(f"  {trade_id} ({sig_date} {sig_time}, {session})")
    
    print()
    print("=" * 80)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    monitor_healing()

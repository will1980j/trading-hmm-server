#!/usr/bin/env python3
"""
H1.4 CHUNK 1: V2 DATA AVAILABILITY AUDIT (READ-ONLY)
Comprehensive audit of V2 automated signals data infrastructure
NO MODIFICATIONS - Pure discovery and reporting
"""

import os
import psycopg2
from datetime import datetime
import json

DATABASE_URL = os.getenv('DATABASE_URL')

def audit_v2_data():
    """Perform comprehensive V2 data audit"""
    
    print("=" * 80)
    print("H1.4 CHUNK 1: V2 DATA AVAILABILITY AUDIT")
    print("=" * 80)
    print()
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # ========================================================================
    # 1. TABLE EXISTENCE CHECK
    # ========================================================================
    print("1️⃣ TABLE EXISTENCE CHECK")
    print("-" * 80)
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%signal%' OR table_name LIKE '%automated%'
        ORDER BY table_name
    """)
    tables = cur.fetchall()
    print(f"Found {len(tables)} signal-related tables:")
    for table in tables:
        print(f"  ✓ {table[0]}")
    print()
    
    # ========================================================================
    # 2. AUTOMATED_SIGNALS SCHEMA AUDIT
    # ========================================================================
    print("2️⃣ AUTOMATED_SIGNALS SCHEMA AUDIT")
    print("-" * 80)
    
    cur.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'automated_signals'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    
    print(f"Table: automated_signals")
    print(f"Columns: {len(columns)}")
    print()
    print(f"{'Column Name':<25} {'Type':<20} {'Nullable':<10} {'Default':<20}")
    print("-" * 80)
    for col in columns:
        col_name, data_type, max_len, nullable, default = col
        type_str = f"{data_type}({max_len})" if max_len else data_type
        default_str = str(default)[:18] if default else ""
        print(f"{col_name:<25} {type_str:<20} {nullable:<10} {default_str:<20}")
    print()
    
    # ========================================================================
    # 3. DATA VOLUME CHECK
    # ========================================================================
    print("3️⃣ DATA VOLUME CHECK")
    print("-" * 80)
    
    cur.execute("SELECT COUNT(*) FROM automated_signals")
    total_rows = cur.fetchone()[0]
    print(f"Total rows: {total_rows:,}")
    
    if total_rows > 0:
        # Event type distribution
        cur.execute("""
            SELECT event_type, COUNT(*) as count
            FROM automated_signals
            GROUP BY event_type
            ORDER BY count DESC
        """)
        event_types = cur.fetchall()
        print()
        print("Event Type Distribution:")
        for event_type, count in event_types:
            pct = (count / total_rows) * 100
            print(f"  {event_type:<20} {count:>6,} ({pct:>5.1f}%)")
        
        # Recent data check
        cur.execute("""
            SELECT 
                MIN(created_at) as oldest,
                MAX(created_at) as newest,
                COUNT(DISTINCT trade_id) as unique_trades
            FROM automated_signals
        """)
        oldest, newest, unique_trades = cur.fetchone()
        print()
        print(f"Date Range:")
        print(f"  Oldest: {oldest}")
        print(f"  Newest: {newest}")
        print(f"  Unique Trades: {unique_trades:,}")
    print()
    
    # ========================================================================
    # 4. LIFECYCLE COMPLETENESS CHECK
    # ========================================================================
    print("4️⃣ LIFECYCLE COMPLETENESS CHECK")
    print("-" * 80)
    
    if total_rows > 0:
        # Check for complete lifecycles
        cur.execute("""
            WITH trade_events AS (
                SELECT 
                    trade_id,
                    COUNT(*) as event_count,
                    STRING_AGG(DISTINCT event_type, ', ' ORDER BY event_type) as events,
                    BOOL_OR(event_type = 'SIGNAL_CREATED') as has_entry,
                    BOOL_OR(event_type LIKE 'EXIT_%') as has_exit,
                    BOOL_OR(event_type = 'MFE_UPDATE') as has_mfe,
                    BOOL_OR(event_type = 'BE_TRIGGERED') as has_be
                FROM automated_signals
                GROUP BY trade_id
            )
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN has_entry THEN 1 ELSE 0 END) as with_entry,
                SUM(CASE WHEN has_exit THEN 1 ELSE 0 END) as with_exit,
                SUM(CASE WHEN has_mfe THEN 1 ELSE 0 END) as with_mfe,
                SUM(CASE WHEN has_be THEN 1 ELSE 0 END) as with_be,
                SUM(CASE WHEN has_entry AND has_exit THEN 1 ELSE 0 END) as complete_lifecycle
            FROM trade_events
        """)
        stats = cur.fetchone()
        total_trades, with_entry, with_exit, with_mfe, with_be, complete = stats
        
        print(f"Trade Lifecycle Analysis:")
        print(f"  Total Unique Trades: {total_trades:,}")
        print(f"  With SIGNAL_CREATED: {with_entry:,} ({(with_entry/total_trades*100):.1f}%)")
        print(f"  With EXIT event: {with_exit:,} ({(with_exit/total_trades*100):.1f}%)")
        print(f"  With MFE_UPDATE: {with_mfe:,} ({(with_mfe/total_trades*100):.1f}%)")
        print(f"  With BE_TRIGGERED: {with_be:,} ({(with_be/total_trades*100):.1f}%)")
        print(f"  Complete Lifecycle: {complete:,} ({(complete/total_trades*100):.1f}%)")
    print()
    
    # ========================================================================
    # 5. FIELD AVAILABILITY CHECK
    # ========================================================================
    print("5️⃣ FIELD AVAILABILITY CHECK")
    print("-" * 80)
    
    if total_rows > 0:
        # Check which fields have data
        critical_fields = [
            'direction', 'entry_price', 'stop_loss', 'session', 
            'bias', 'mfe', 'be_mfe', 'no_be_mfe', 'signal_date', 
            'signal_time', 'telemetry'
        ]
        
        print("Field Population Analysis:")
        for field in critical_fields:
            try:
                cur.execute(f"""
                    SELECT 
                        COUNT(*) as total,
                        COUNT({field}) as populated,
                        COUNT(*) - COUNT({field}) as null_count
                    FROM automated_signals
                """)
                total, populated, null_count = cur.fetchone()
                pct = (populated / total * 100) if total > 0 else 0
                status = "✓" if pct > 90 else "⚠" if pct > 50 else "✗"
                print(f"  {status} {field:<20} {populated:>6,}/{total:<6,} ({pct:>5.1f}%)")
            except Exception as e:
                print(f"  ✗ {field:<20} COLUMN NOT FOUND")
    print()
    
    # ========================================================================
    # 6. SAMPLE DATA INSPECTION
    # ========================================================================
    print("6️⃣ SAMPLE DATA INSPECTION")
    print("-" * 80)
    
    if total_rows > 0:
        cur.execute("""
            SELECT 
                trade_id,
                event_type,
                direction,
                entry_price,
                stop_loss,
                session,
                created_at
            FROM automated_signals
            ORDER BY created_at DESC
            LIMIT 5
        """)
        samples = cur.fetchall()
        
        print("Most Recent 5 Events:")
        for sample in samples:
            trade_id, event_type, direction, entry, sl, session, created = sample
            print(f"  {trade_id} | {event_type:<15} | {direction or 'N/A':<8} | {session or 'N/A':<10} | {created}")
    print()
    
    # ========================================================================
    # 7. TELEMETRY CHECK
    # ========================================================================
    print("7️⃣ TELEMETRY AVAILABILITY CHECK")
    print("-" * 80)
    
    try:
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(telemetry) as with_telemetry,
                COUNT(CASE WHEN telemetry IS NOT NULL AND telemetry != '{}' THEN 1 END) as with_data
            FROM automated_signals
        """)
        total, with_tel, with_data = cur.fetchone()
        
        print(f"Telemetry Status:")
        print(f"  Total Events: {total:,}")
        print(f"  With Telemetry Column: {with_tel:,}")
        print(f"  With Telemetry Data: {with_data:,}")
        
        if with_data > 0:
            cur.execute("""
                SELECT telemetry
                FROM automated_signals
                WHERE telemetry IS NOT NULL AND telemetry != '{}'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            sample_tel = cur.fetchone()[0]
            print()
            print("Sample Telemetry Structure:")
            print(json.dumps(sample_tel, indent=2)[:500] + "...")
    except Exception as e:
        print(f"  ✗ Telemetry column not available: {e}")
    print()
    
    # ========================================================================
    # 8. TIME ANALYSIS COMPATIBILITY CHECK
    # ========================================================================
    print("8️⃣ TIME ANALYSIS COMPATIBILITY CHECK")
    print("-" * 80)
    
    required_for_time_analysis = {
        'signal_date': 'Date field for daily grouping',
        'signal_time': 'Time field for hourly/session grouping',
        'session': 'Session classification (ASIA, LONDON, NY AM, etc.)',
        'direction': 'Trade direction (Bullish/Bearish)',
        'mfe': 'Maximum Favorable Excursion (R-multiple)',
        'be_mfe': 'MFE with break-even strategy',
        'no_be_mfe': 'MFE without break-even strategy'
    }
    
    print("Required Fields for Time Analysis Migration:")
    for field, description in required_for_time_analysis.items():
        try:
            cur.execute(f"""
                SELECT COUNT({field}) 
                FROM automated_signals 
                WHERE {field} IS NOT NULL
            """)
            count = cur.fetchone()[0]
            status = "✓ READY" if count > 0 else "✗ MISSING"
            print(f"  {status:<10} {field:<15} - {description}")
        except:
            print(f"  ✗ MISSING  {field:<15} - {description}")
    print()
    
    # ========================================================================
    # 9. SUMMARY & RECOMMENDATIONS
    # ========================================================================
    print("9️⃣ SUMMARY & RECOMMENDATIONS")
    print("-" * 80)
    
    print("V2 Data Readiness Assessment:")
    print()
    
    if total_rows == 0:
        print("  ⚠️  NO DATA FOUND - V2 system not actively collecting data")
        print()
        print("  Next Steps:")
        print("    1. Verify TradingView indicator is sending webhooks")
        print("    2. Check webhook endpoint is receiving data")
        print("    3. Verify database connection and insert logic")
    elif total_rows < 100:
        print(f"  ⚠️  LIMITED DATA - Only {total_rows} events found")
        print()
        print("  Next Steps:")
        print("    1. Allow more time for data collection")
        print("    2. Verify webhook is consistently firing")
        print("    3. Check for any data insertion errors")
    else:
        print(f"  ✓ SUFFICIENT DATA - {total_rows:,} events across {unique_trades:,} trades")
        print()
        print("  Migration Readiness:")
        
        # Check each requirement
        checks = []
        try:
            cur.execute("SELECT COUNT(*) FROM automated_signals WHERE signal_date IS NOT NULL")
            has_date = cur.fetchone()[0] > 0
            checks.append(("Date field", has_date))
        except:
            checks.append(("Date field", False))
        
        try:
            cur.execute("SELECT COUNT(*) FROM automated_signals WHERE signal_time IS NOT NULL")
            has_time = cur.fetchone()[0] > 0
            checks.append(("Time field", has_time))
        except:
            checks.append(("Time field", False))
        
        try:
            cur.execute("SELECT COUNT(*) FROM automated_signals WHERE session IS NOT NULL")
            has_session = cur.fetchone()[0] > 0
            checks.append(("Session field", has_session))
        except:
            checks.append(("Session field", False))
        
        try:
            cur.execute("SELECT COUNT(*) FROM automated_signals WHERE mfe IS NOT NULL OR be_mfe IS NOT NULL OR no_be_mfe IS NOT NULL")
            has_mfe = cur.fetchone()[0] > 0
            checks.append(("MFE fields", has_mfe))
        except:
            checks.append(("MFE fields", False))
        
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"    {status} {check_name}")
        
        all_passed = all(passed for _, passed in checks)
        print()
        if all_passed:
            print("  ✅ READY FOR MIGRATION - All required fields present")
        else:
            print("  ⚠️  PARTIAL READINESS - Some fields missing")
            print("     Migration possible but may require schema updates")
    
    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    audit_v2_data()

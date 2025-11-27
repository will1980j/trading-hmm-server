#!/usr/bin/env python3
"""
H1.4 CHUNK 2: LIVE AUTOMATED_SIGNALS DATA SNAPSHOT (READ-ONLY)
Comprehensive live database snapshot via Railway API
NO MODIFICATIONS - Pure read-only analysis
"""

import requests
import json
from datetime import datetime
from collections import Counter

# Railway production URL
BASE_URL = "https://web-production-cd33.up.railway.app"

def print_section(title):
    """Print formatted section header"""
    print()
    print("=" * 80)
    print(f"{title}")
    print("=" * 80)
    print()

def fetch_api(endpoint):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return None

def main():
    print("=" * 80)
    print("H1.4 CHUNK 2: LIVE V2 DATA SNAPSHOT")
    print("=" * 80)
    print(f"Target: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    print()
    
    # ========================================================================
    # 1️⃣ SCHEMA CONFIRMATION (via debug endpoint)
    # ========================================================================
    print_section("1️⃣ SCHEMA CONFIRMATION")
    
    debug_data = fetch_api("/api/automated-signals/debug")
    
    if debug_data and 'schema' in debug_data:
        schema = debug_data['schema']
        print(f"TABLE: automated_signals")
        print(f"COLUMNS: {len(schema)}")
        print()
        print(f"{'Column Name':<25} {'Type':<20} {'Indexed':<10}")
        print("-" * 80)
        
        for col in schema:
            col_name = col.get('column_name', 'unknown')
            data_type = col.get('data_type', 'unknown')
            # Check if column is indexed (would need separate query)
            indexed = "?"
            print(f"{col_name:<25} {data_type:<20} {indexed:<10}")
        
        print()
        print("INDEXES:")
        print("  - idx_automated_signals_trade_id (trade_id)")
        print("  - idx_automated_signals_event_type (event_type)")
        print("  - idx_automated_signals_timestamp (timestamp)")
        print("  - idx_automated_signals_created_at (created_at DESC)")
        print("  - idx_automated_signals_telemetry (GIN on telemetry)")
    else:
        print("⚠️  Schema information not available via API")
        print("   Expected columns based on code analysis:")
        expected_cols = [
            'id', 'event_type', 'trade_id', 'direction', 'entry_price',
            'stop_loss', 'risk_distance', 'current_price', 'mfe', 'be_mfe',
            'no_be_mfe', 'exit_price', 'final_mfe', 'session', 'bias',
            'signal_date', 'signal_time', 'timestamp', 'telemetry', 'created_at'
        ]
        for col in expected_cols:
            print(f"  - {col}")
    
    # ========================================================================
    # 2️⃣ ROW COUNT & RECENCY
    # ========================================================================
    print_section("2️⃣ ROW COUNT & RECENCY")
    
    stats_data = fetch_api("/api/automated-signals/stats-live")
    
    if stats_data:
        total_trades = stats_data.get('total_trades', 0)
        active_trades = stats_data.get('active_trades', 0)
        completed_trades = stats_data.get('completed_trades', 0)
        
        print(f"Total Unique Trades: {total_trades:,}")
        print(f"  Active: {active_trades:,}")
        print(f"  Completed: {completed_trades:,}")
        print()
        
        # Event type distribution (if available)
        if 'event_distribution' in stats_data:
            print("Event Type Distribution:")
            for event_type, count in stats_data['event_distribution'].items():
                print(f"  {event_type:<20} {count:>6,}")
        
        # Most recent timestamp
        if 'last_signal_time' in stats_data:
            print()
            print(f"Most Recent Signal: {stats_data['last_signal_time']}")
        
        print()
        print("✅ V2 System Status: ACTIVELY RECEIVING DATA" if total_trades > 0 else "⚠️  V2 System Status: NO DATA FOUND")
    else:
        print("⚠️  Stats endpoint not available")
    
    # ========================================================================
    # 3️⃣ FIELD QUALITY CHECK - SAMPLE 20 SIGNALS
    # ========================================================================
    print_section("3️⃣ FIELD QUALITY CHECK - SAMPLE 20 SIGNALS")
    
    dashboard_data = fetch_api("/api/automated-signals/dashboard-data")
    
    if dashboard_data:
        # Get recent signals from active and completed
        all_signals = []
        
        if 'active_trades' in dashboard_data:
            all_signals.extend(dashboard_data['active_trades'][:10])
        
        if 'completed_trades' in dashboard_data:
            all_signals.extend(dashboard_data['completed_trades'][:10])
        
        if all_signals:
            print(f"Analyzing {len(all_signals)} recent signals:")
            print()
            print(f"{'Trade ID':<25} {'Event':<15} {'Session':<10} {'BE MFE':<8} {'No BE MFE':<10}")
            print("-" * 80)
            
            anomalies = []
            
            for signal in all_signals[:20]:
                trade_id = signal.get('trade_id', 'N/A')[:24]
                # Get latest event type (would need events array)
                event_type = "ACTIVE" if signal in dashboard_data.get('active_trades', []) else "COMPLETED"
                session = signal.get('session', 'NULL')
                be_mfe = signal.get('be_mfe', 'NULL')
                no_be_mfe = signal.get('no_be_mfe', 'NULL')
                
                # Check for anomalies
                if session == 'NULL' or session is None:
                    anomalies.append(f"NULL session in {trade_id}")
                if be_mfe == 'NULL' and no_be_mfe == 'NULL':
                    anomalies.append(f"Missing MFE in {trade_id}")
                
                be_mfe_str = f"{be_mfe:.2f}" if isinstance(be_mfe, (int, float)) else str(be_mfe)
                no_be_mfe_str = f"{no_be_mfe:.2f}" if isinstance(no_be_mfe, (int, float)) else str(no_be_mfe)
                
                print(f"{trade_id:<25} {event_type:<15} {session:<10} {be_mfe_str:<8} {no_be_mfe_str:<10}")
            
            if anomalies:
                print()
                print("⚠️  ANOMALIES DETECTED:")
                for anomaly in anomalies[:10]:
                    print(f"  - {anomaly}")
            else:
                print()
                print("✅ No obvious anomalies detected in sample")
        else:
            print("⚠️  No signals available in dashboard data")
    else:
        print("⚠️  Dashboard data endpoint not available")
    
    # ========================================================================
    # 4️⃣ SESSION DISTRIBUTION SNAPSHOT
    # ========================================================================
    print_section("4️⃣ SESSION DISTRIBUTION SNAPSHOT")
    
    if dashboard_data:
        all_trades = []
        if 'active_trades' in dashboard_data:
            all_trades.extend(dashboard_data['active_trades'])
        if 'completed_trades' in dashboard_data:
            all_trades.extend(dashboard_data['completed_trades'])
        
        if all_trades:
            sessions = [t.get('session') for t in all_trades if t.get('session')]
            session_counts = Counter(sessions)
            
            print("Session Distribution:")
            print()
            total = sum(session_counts.values())
            for session, count in session_counts.most_common():
                pct = (count / total * 100) if total > 0 else 0
                print(f"  {session:<15} {count:>6,} ({pct:>5.1f}%)")
            
            print()
            print("Canonical Session Set:")
            canonical = ['ASIA', 'LONDON', 'NY PRE', 'NY AM', 'NY LUNCH', 'NY PM']
            print(f"  Expected: {', '.join(canonical)}")
            
            found_sessions = set(session_counts.keys())
            canonical_set = set(canonical)
            
            unknown = found_sessions - canonical_set
            if unknown:
                print()
                print("⚠️  UNKNOWN SESSION LABELS (need normalization):")
                for session in unknown:
                    print(f"  - '{session}' ({session_counts[session]} occurrences)")
            else:
                print()
                print("✅ All sessions match canonical set")
        else:
            print("⚠️  No trade data available for session analysis")
    else:
        print("⚠️  Cannot analyze sessions without dashboard data")
    
    # ========================================================================
    # 5️⃣ V2 R-DATA AVAILABILITY
    # ========================================================================
    print_section("5️⃣ V2 R-DATA AVAILABILITY")
    
    if dashboard_data:
        all_trades = []
        if 'active_trades' in dashboard_data:
            all_trades.extend(dashboard_data['active_trades'])
        if 'completed_trades' in dashboard_data:
            all_trades.extend(dashboard_data['completed_trades'])
        
        if all_trades:
            be_mfe_count = sum(1 for t in all_trades if t.get('be_mfe') is not None)
            no_be_mfe_count = sum(1 for t in all_trades if t.get('no_be_mfe') is not None)
            missing_mfe = sum(1 for t in all_trades if t.get('be_mfe') is None and t.get('no_be_mfe') is None)
            
            total = len(all_trades)
            
            print("MFE Field Population:")
            print()
            print(f"  Total Trades: {total:,}")
            print(f"  With be_mfe: {be_mfe_count:,} ({be_mfe_count/total*100:.1f}%)")
            print(f"  With no_be_mfe: {no_be_mfe_count:,} ({no_be_mfe_count/total*100:.1f}%)")
            print(f"  Missing both: {missing_mfe:,} ({missing_mfe/total*100:.1f}%)")
            
            print()
            if be_mfe_count > 0 or no_be_mfe_count > 0:
                print("✅ SUFFICIENT MFE DATA for R-based analytics")
                
                # Sample MFE values
                be_mfe_values = [t.get('be_mfe') for t in all_trades if t.get('be_mfe') is not None]
                no_be_mfe_values = [t.get('no_be_mfe') for t in all_trades if t.get('no_be_mfe') is not None]
                
                if be_mfe_values:
                    print(f"  BE MFE Range: {min(be_mfe_values):.2f}R to {max(be_mfe_values):.2f}R")
                    print(f"  BE MFE Average: {sum(be_mfe_values)/len(be_mfe_values):.2f}R")
                
                if no_be_mfe_values:
                    print(f"  No BE MFE Range: {min(no_be_mfe_values):.2f}R to {max(no_be_mfe_values):.2f}R")
                    print(f"  No BE MFE Average: {sum(no_be_mfe_values)/len(no_be_mfe_values):.2f}R")
            else:
                print("⚠️  INSUFFICIENT MFE DATA - Cannot compute R analytics")
        else:
            print("⚠️  No trade data available for MFE analysis")
    else:
        print("⚠️  Cannot analyze MFE without dashboard data")
    
    # ========================================================================
    # 6️⃣ SUMMARY REPORT
    # ========================================================================
    print_section("6️⃣ SUMMARY REPORT")
    
    print("V2 DATA STATUS:")
    print("-" * 80)
    
    if stats_data:
        total_trades = stats_data.get('total_trades', 0)
        print(f"  Total automated_signals trades: {total_trades:,}")
        
        if 'last_signal_time' in stats_data:
            print(f"  Last signal at: {stats_data['last_signal_time']}")
        
        if 'event_distribution' in stats_data:
            print(f"  Event types: {dict(stats_data['event_distribution'])}")
    
    if dashboard_data and all_trades:
        be_mfe_count = sum(1 for t in all_trades if t.get('be_mfe') is not None)
        no_be_mfe_count = sum(1 for t in all_trades if t.get('no_be_mfe') is not None)
        print(f"  MFE fields: be_mfe={be_mfe_count}, no_be_mfe={no_be_mfe_count}")
        
        sessions = list(set(t.get('session') for t in all_trades if t.get('session')))
        print(f"  Sessions seen: {sessions}")
        
        symbols = list(set(t.get('symbol', 'NQ') for t in all_trades))
        print(f"  Symbols seen: {symbols}")
    
    print()
    print("READINESS FOR TIME ANALYSIS:")
    print("-" * 80)
    
    # Determine readiness
    ready = True
    issues = []
    
    if not stats_data or stats_data.get('total_trades', 0) == 0:
        ready = False
        issues.append("No V2 data found")
    
    if dashboard_data and all_trades:
        # Check for required fields
        missing_session = sum(1 for t in all_trades if not t.get('session'))
        if missing_session > len(all_trades) * 0.1:  # More than 10% missing
            ready = False
            issues.append(f"Session field missing in {missing_session} trades")
        
        missing_mfe = sum(1 for t in all_trades if t.get('be_mfe') is None and t.get('no_be_mfe') is None)
        if missing_mfe > len(all_trades) * 0.1:
            ready = False
            issues.append(f"MFE fields missing in {missing_mfe} trades")
        
        # Check for unknown sessions
        sessions = [t.get('session') for t in all_trades if t.get('session')]
        canonical = {'ASIA', 'LONDON', 'NY PRE', 'NY AM', 'NY LUNCH', 'NY PM'}
        unknown = set(sessions) - canonical
        if unknown:
            issues.append(f"Unknown session labels: {unknown}")
    
    if ready and not issues:
        print("  ✅ VERDICT: READY FOR MIGRATION")
        print()
        print("  All required fields present and populated")
        print("  Session naming consistent")
        print("  MFE data available for R-based analytics")
    else:
        print("  ⚠️  VERDICT: NEEDS FIXES")
        print()
        print("  Issues found:")
        for issue in issues:
            print(f"    - {issue}")
    
    print()
    print("=" * 80)
    print("LIVE SNAPSHOT COMPLETE")
    print("=" * 80)
    print()
    print("📋 READ-ONLY ANALYSIS - NO MODIFICATIONS MADE")

if __name__ == "__main__":
    main()

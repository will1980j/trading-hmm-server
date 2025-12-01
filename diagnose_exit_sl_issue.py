"""
Diagnose EXIT_SL transmission and trade completion status
Critical investigation: Why are so many trades showing No BE = ACTIVE when SL should have been hit?
"""
import requests
from datetime import datetime
import pytz

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("EXIT_SL TRANSMISSION & TRADE COMPLETION DIAGNOSTIC")
print("=" * 80)

# Get dashboard data
print("\n1. Fetching current dashboard data...")
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=10)
    data = resp.json()
    
    active_trades = data.get('active_trades', [])
    completed_trades = data.get('completed_trades', [])
    
    print(f"✅ Active trades: {len(active_trades)}")
    print(f"✅ Completed trades: {len(completed_trades)}")
    
    # Analyze active trades - check their event_type
    print("\n" + "=" * 80)
    print("ACTIVE TRADES ANALYSIS")
    print("=" * 80)
    
    if active_trades:
        print(f"\nAnalyzing {len(active_trades)} active trades:")
        
        exit_be_count = 0
        entry_only_count = 0
        other_count = 0
        
        for trade in active_trades[:10]:  # Show first 10
            trade_id = trade.get('trade_id', 'UNKNOWN')
            event_type = trade.get('event_type', 'UNKNOWN')
            direction = trade.get('direction', 'UNKNOWN')
            signal_date = trade.get('signal_date', 'UNKNOWN')
            signal_time = trade.get('signal_time', 'UNKNOWN')
            
            print(f"\n  Trade: {trade_id}")
            print(f"    Event Type: {event_type}")
            print(f"    Direction: {direction}")
            print(f"    Date/Time: {signal_date} {signal_time}")
            
            if event_type == 'EXIT_BE':
                exit_be_count += 1
                print(f"    ⚠️  Status: EXIT_BE (BE=1 completed, No BE should still be ACTIVE)")
            elif event_type == 'ENTRY':
                entry_only_count += 1
                print(f"    ✅ Status: ENTRY only (legitimately active)")
            else:
                other_count += 1
                print(f"    ❓ Status: {event_type}")
        
        print(f"\n  Summary of active trades:")
        print(f"    EXIT_BE (BE=1 done, No BE active): {exit_be_count}")
        print(f"    ENTRY only (both strategies active): {entry_only_count}")
        print(f"    Other event types: {other_count}")
        
        if exit_be_count > 0:
            print(f"\n  ⚠️  {exit_be_count} trades have EXIT_BE but no EXIT_SL")
            print(f"     This is CORRECT if No BE strategy hasn't hit SL yet")
            print(f"     This is WRONG if SL was actually hit but EXIT_SL wasn't sent")
    
    # Analyze completed trades
    print("\n" + "=" * 80)
    print("COMPLETED TRADES ANALYSIS")
    print("=" * 80)
    
    if completed_trades:
        print(f"\nAnalyzing {len(completed_trades)} completed trades:")
        
        exit_sl_count = 0
        exit_be_only_count = 0
        
        for trade in completed_trades[:10]:  # Show first 10
            trade_id = trade.get('trade_id', 'UNKNOWN')
            event_type = trade.get('event_type', 'UNKNOWN')
            
            if event_type in ['EXIT_SL', 'EXIT_STOP_LOSS']:
                exit_sl_count += 1
            elif event_type == 'EXIT_BE':
                exit_be_only_count += 1
                print(f"\n  ⚠️  Trade {trade_id}: Marked COMPLETED but only has EXIT_BE (no EXIT_SL)")
        
        print(f"\n  Summary of completed trades:")
        print(f"    EXIT_SL (properly completed): {exit_sl_count}")
        print(f"    EXIT_BE only (should be ACTIVE?): {exit_be_only_count}")
        
        if exit_be_only_count > 0:
            print(f"\n  🚨 ISSUE FOUND: {exit_be_only_count} trades marked COMPLETED with only EXIT_BE")
            print(f"     These should be ACTIVE (No BE strategy still running)")
    
    # Check for missing EXIT_SL events
    print("\n" + "=" * 80)
    print("EXIT_SL EVENT VERIFICATION")
    print("=" * 80)
    
    print("\nChecking if EXIT_SL events are being received...")
    
    # Get recent webhook stats
    resp2 = requests.get(f"{BASE_URL}/api/automated-signals/stats-live", timeout=10)
    stats = resp2.json()
    
    total_signals = stats.get('total_signals', 0)
    completed_count = stats.get('completed_count', 0)
    active_count = stats.get('active_count', 0)
    
    print(f"  Total signals: {total_signals}")
    print(f"  Completed count: {completed_count}")
    print(f"  Active count: {active_count}")
    
    if total_signals > 0:
        completion_rate = (completed_count / total_signals) * 100
        print(f"  Completion rate: {completion_rate:.1f}%")
        
        if completion_rate < 20:
            print(f"\n  🚨 LOW COMPLETION RATE - Possible EXIT_SL transmission issue!")
            print(f"     Expected: 50-70% completion rate")
            print(f"     Actual: {completion_rate:.1f}%")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("INVESTIGATION QUESTIONS")
print("=" * 80)
print("""
1. Are EXIT_SL webhooks being sent from TradingView indicator?
   - Check TradingView alert log for EXIT_SL events
   - Verify indicator sends EXIT_SL when stop loss is hit

2. Is the backend receiving EXIT_SL webhooks?
   - Check Railway logs for EXIT_SL webhook reception
   - Verify /api/automated-signals/webhook endpoint processes EXIT_SL

3. Is EXIT_SL being stored in database correctly?
   - Query automated_signals table for event_type = 'EXIT_SL'
   - Verify EXIT_SL events exist for trades that should be completed

4. Is dashboard query logic correct?
   - Verify active_trades query excludes trades with EXIT_SL
   - Verify completed_trades query includes trades with EXIT_SL

NEXT STEPS:
- If EXIT_SL events are missing → Fix TradingView indicator
- If EXIT_SL events exist but not processed → Fix backend webhook handler
- If EXIT_SL events stored but dashboard wrong → Fix dashboard query logic
""")

"""
Verify EXIT_SL transmission using ONLY the Railway API endpoints (NO direct database queries)
"""
import requests

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("EXIT_SL VERIFICATION - API ONLY (NO DATABASE QUERIES)")
print("=" * 80)

# Step 1: Get dashboard data via API
print("\n1. Checking dashboard data via API...")
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=10)
    data = resp.json()
    
    active = data.get('active_trades', [])
    completed = data.get('completed_trades', [])
    
    print(f"✅ Active trades: {len(active)}")
    print(f"✅ Completed trades: {len(completed)}")
    
    # Analyze completed trades - check event_type
    exit_sl_count = 0
    exit_be_count = 0
    
    print(f"\nCompleted trades event types:")
    for trade in completed:
        event_type = trade.get('event_type', 'UNKNOWN')
        if event_type in ['EXIT_SL', 'EXIT_STOP_LOSS']:
            exit_sl_count += 1
        elif event_type in ['EXIT_BE', 'EXIT_BREAK_EVEN']:
            exit_be_count += 1
            print(f"  ⚠️  {trade['trade_id']}: {event_type} (should be ACTIVE, not COMPLETED)")
    
    print(f"\n📊 Completed trades breakdown:")
    print(f"  EXIT_SL (both strategies done): {exit_sl_count}")
    print(f"  EXIT_BE (only BE=1 done): {exit_be_count}")
    
    if exit_be_count > 0:
        print(f"\n🚨 ISSUE: {exit_be_count} trades with EXIT_BE marked as COMPLETED")
        print(f"   These should be ACTIVE (No BE strategy still running)")
    
    if exit_sl_count == 0:
        print(f"\n🚨 CRITICAL: NO EXIT_SL events in completed trades!")
        print(f"   Either EXIT_SL webhooks aren't being sent, or they're not being stored")
    
    # Show sample active trades
    print(f"\nSample active trades (first 5):")
    for trade in active[:5]:
        print(f"  {trade['trade_id']}: {trade.get('event_type', 'UNKNOWN')} - {trade.get('direction', 'UNKNOWN')}")
    
except Exception as e:
    print(f"❌ API Error: {e}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if exit_sl_count == 0 and exit_be_count > 0:
    print("""
🚨 ROOT CAUSE IDENTIFIED:
- EXIT_BE events are being received and stored
- EXIT_SL events are NOT being received or stored
- Dashboard incorrectly marks EXIT_BE trades as COMPLETED

ISSUE: EXIT_SL webhooks are not transmitting from TradingView indicator

SOLUTION NEEDED:
1. Verify TradingView indicator sends EXIT_SL when original stop loss is hit
2. Check TradingView alert log for EXIT_SL alerts
3. If EXIT_SL alerts exist → backend reception issue
4. If EXIT_SL alerts missing → indicator transmission issue
""")
elif exit_sl_count > 0:
    print(f"""
✅ EXIT_SL events are being received and stored correctly

Current state:
- {exit_sl_count} trades properly completed with EXIT_SL
- {exit_be_count} trades with EXIT_BE only (No BE still active)
- {len(active)} trades currently active

The dashboard query fix will correctly classify these trades.
""")

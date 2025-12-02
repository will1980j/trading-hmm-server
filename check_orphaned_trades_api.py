"""
Check for orphaned trades using ONLY Railway API endpoints
Orphaned = trades from previous days that never got EXIT_SL
"""
import requests
from datetime import datetime, timedelta
import pytz

BASE_URL = "https://web-production-f8c3.up.railway.app"

print("=" * 80)
print("ORPHANED TRADES CHECK - API ONLY")
print("=" * 80)

# Get current NY Eastern time
eastern = pytz.timezone('America/New_York')
now_et = datetime.now(eastern)
today_str = now_et.strftime('%Y-%m-%d')

print(f"\nCurrent NY Time: {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"Today's date: {today_str}")

# Get all active trades
try:
    resp = requests.get(f"{BASE_URL}/api/automated-signals/dashboard-data", timeout=10)
    data = resp.json()
    
    active = data.get('active_trades', [])
    
    print(f"\n✅ Total active trades: {len(active)}")
    
    # Categorize by date
    today_active = []
    old_active = []
    very_old_active = []
    
    for trade in active:
        signal_date = trade.get('signal_date', '')
        trade_id = trade.get('trade_id', 'UNKNOWN')
        event_type = trade.get('event_type', 'UNKNOWN')
        
        if signal_date == today_str:
            today_active.append(trade)
        elif signal_date:
            # Calculate age
            try:
                trade_date = datetime.strptime(signal_date, '%Y-%m-%d')
                age_days = (now_et.date() - trade_date.date()).days
                
                if age_days >= 2:
                    very_old_active.append((trade, age_days))
                else:
                    old_active.append((trade, age_days))
            except:
                old_active.append((trade, 0))
    
    print(f"\n📊 Active Trades Breakdown:")
    print(f"  Today ({today_str}): {len(today_active)}")
    print(f"  Yesterday: {len(old_active)}")
    print(f"  2+ days old (ORPHANED): {len(very_old_active)}")
    
    if very_old_active:
        print(f"\n🚨 ORPHANED TRADES FOUND ({len(very_old_active)} trades):")
        for trade, age in very_old_active[:20]:
            print(f"\n  Trade: {trade['trade_id']}")
            print(f"    Age: {age} days old")
            print(f"    Date: {trade.get('signal_date', 'UNKNOWN')}")
            print(f"    Event: {trade.get('event_type', 'UNKNOWN')}")
            print(f"    Direction: {trade.get('direction', 'UNKNOWN')}")
            print(f"    ⚠️  This trade should have completed by now!")
    
    if old_active:
        print(f"\n⚠️  YESTERDAY'S ACTIVE TRADES ({len(old_active)} trades):")
        for trade, age in old_active[:10]:
            print(f"  {trade['trade_id']}: {age} day(s) old - {trade.get('event_type', 'UNKNOWN')}")
    
    if today_active:
        print(f"\n✅ TODAY'S ACTIVE TRADES ({len(today_active)} trades):")
        for trade in today_active[:10]:
            print(f"  {trade['trade_id']}: {trade.get('event_type', 'UNKNOWN')} - {trade.get('direction', 'UNKNOWN')}")
    
    # Summary
    print(f"\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if len(very_old_active) > 0:
        print(f"""
🚨 ORPHANED TRADES DETECTED: {len(very_old_active)} trades

These trades are 2+ days old and still marked ACTIVE.
This means EXIT_SL webhooks were never received for these trades.

POSSIBLE CAUSES:
1. TradingView indicator wasn't running when SL was hit
2. EXIT_SL webhooks failed to transmit
3. Trades are legitimately still running (unlikely after 2+ days)

RECOMMENDATION:
- Review these trades manually on TradingView chart
- If SL was hit → these are orphaned, should be deleted
- If still running → legitimate active trades (rare)
- Consider adding auto-cleanup for trades older than X days
""")
    else:
        print(f"""
✅ NO ORPHANED TRADES DETECTED

All active trades are from today or yesterday.
The {len(active)} active trades appear legitimate.
""")
    
    # Calculate what the count SHOULD be after deployment
    expected_active_after_deploy = len(today_active) + len(old_active) + len(very_old_active)
    
    # Get completed trades to see how many have EXIT_BE
    completed = data.get('completed_trades', [])
    exit_be_in_completed = sum(1 for t in completed if t.get('event_type') in ['EXIT_BE', 'EXIT_BREAK_EVEN'])
    
    print(f"\n📊 EXPECTED AFTER DEPLOYMENT:")
    print(f"  Current active: {len(active)}")
    print(f"  EXIT_BE trades moving to active: {exit_be_in_completed}")
    print(f"  Total active after deploy: {len(active) + exit_be_in_completed}")
    print(f"  Completed (EXIT_SL only): {len(completed) - exit_be_in_completed}")
    
except Exception as e:
    print(f"❌ Error: {e}")

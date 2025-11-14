"""
Diagnose why dashboard is not receiving signals
"""
import os
import psycopg2
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get('DATABASE_URL')

def check_recent_signals():
    """Check for any recent signals in database"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("=" * 80)
    print("CHECKING RECENT SIGNALS IN DATABASE")
    print("=" * 80)
    
    # Check last 24 hours
    cur.execute("""
        SELECT 
            trade_id,
            event_type,
            direction,
            entry_price,
            stop_loss,
            be_mfe,
            no_be_mfe,
            signal_date,
            signal_time,
            timestamp
        FROM automated_signals
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    
    results = cur.fetchall()
    
    if results:
        print(f"\n✅ Found {len(results)} signals in last 24 hours:\n")
        for row in results:
            trade_id, event_type, direction, entry, sl, be_mfe, no_be_mfe, sig_date, sig_time, ts = row
            print(f"Trade: {trade_id}")
            print(f"  Event: {event_type}")
            print(f"  Direction: {direction}")
            print(f"  Entry: {entry}, SL: {sl}")
            print(f"  BE MFE: {be_mfe}, No BE MFE: {no_be_mfe}")
            print(f"  Time: {sig_date} {sig_time}")
            print(f"  Timestamp: {ts}")
            print()
    else:
        print("\n❌ NO SIGNALS found in last 24 hours!")
        
        # Check if there are ANY signals at all
        cur.execute("SELECT COUNT(*) FROM automated_signals")
        total_count = cur.fetchone()[0]
        print(f"\nTotal signals in database: {total_count}")
        
        if total_count > 0:
            # Show most recent signal
            cur.execute("""
                SELECT trade_id, event_type, timestamp
                FROM automated_signals
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            last_signal = cur.fetchone()
            print(f"\nMost recent signal:")
            print(f"  Trade ID: {last_signal[0]}")
            print(f"  Event: {last_signal[1]}")
            print(f"  Timestamp: {last_signal[2]}")
    
    cur.close()
    conn.close()

def check_webhook_endpoint():
    """Check if webhook endpoint is accessible"""
    import requests
    
    print("\n" + "=" * 80)
    print("CHECKING WEBHOOK ENDPOINT")
    print("=" * 80)
    
    webhook_url = "https://web-production-cd33.up.railway.app/api/automated-signals/webhook"
    
    try:
        # Try to access the endpoint (should return 405 for GET)
        response = requests.get(webhook_url, timeout=10)
        print(f"\n✅ Webhook endpoint is accessible")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"\n❌ Cannot access webhook endpoint: {e}")

def check_tradingview_alert_setup():
    """Check TradingView alert configuration"""
    print("\n" + "=" * 80)
    print("TRADINGVIEW ALERT CHECKLIST")
    print("=" * 80)
    
    print("\n📋 Verify these settings in TradingView:")
    print("\n1. Alert Condition:")
    print("   - Set to: 'Any alert() function call'")
    print("   - NOT set to specific condition")
    
    print("\n2. Webhook URL:")
    print("   - https://web-production-cd33.up.railway.app/api/automated-signals/webhook")
    
    print("\n3. Alert Message:")
    print("   - Should be: {{strategy.order.alert_message}}")
    print("   - Or leave blank (indicator handles message)")
    
    print("\n4. Alert Frequency:")
    print("   - Set to: 'Once Per Bar Close'")
    
    print("\n5. Indicator Settings:")
    print("   - Track BE=1 MFE: Should be ON")
    print("   - Show MFE Labels: Can be OFF (doesn't affect webhooks)")

def check_indicator_version():
    """Check if indicator has been updated in TradingView"""
    print("\n" + "=" * 80)
    print("INDICATOR VERSION CHECK")
    print("=" * 80)
    
    print("\n⚠️  CRITICAL: Have you updated the indicator in TradingView?")
    print("\nThe fixes we made today:")
    print("  1. Array out of bounds fix (backward loop)")
    print("  2. BE MFE enforcement rule (7 points)")
    print("\nThese fixes are ONLY in the local file!")
    print("\n📝 To deploy:")
    print("  1. Open TradingView")
    print("  2. Open Pine Editor")
    print("  3. Copy entire content of: complete_automated_trading_system.pine")
    print("  4. Paste into Pine Editor")
    print("  5. Click 'Save'")
    print("  6. Add to chart")
    print("  7. Recreate alert with webhook URL")

def main():
    print("\n🔍 DASHBOARD NO SIGNALS DIAGNOSTIC\n")
    
    # Check database
    check_recent_signals()
    
    # Check webhook endpoint
    check_webhook_endpoint()
    
    # Check TradingView setup
    check_tradingview_alert_setup()
    
    # Check indicator version
    check_indicator_version()
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print("\n💡 Most Common Issues:")
    print("  1. Indicator not updated in TradingView (still using old version)")
    print("  2. Alert not configured with webhook URL")
    print("  3. Alert frequency set wrong (should be 'Once Per Bar Close')")
    print("  4. No signals generated (market conditions)")
    print("  5. Indicator crashed (check TradingView logs)")

if __name__ == '__main__':
    main()

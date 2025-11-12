"""
Diagnose why confirmed signals aren't reaching the Railway site
"""
import psycopg2
from datetime import datetime, timedelta
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/trading_platform')

def check_recent_webhooks():
    """Check if ANY webhooks have been received recently"""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check last 24 hours of webhook activity
    print("\n" + "="*80)
    print("CHECKING WEBHOOK RECEPTION - LAST 24 HOURS")
    print("="*80)
    
    # Check automated_signals table
    cur.execute("""
        SELECT 
            event_type,
            trade_id,
            direction,
            signal_date,
            signal_time,
            timestamp,
            entry_price,
            stop_loss
        FROM automated_signals
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    
    results = cur.fetchall()
    
    if not results:
        print("\n❌ NO WEBHOOKS RECEIVED IN LAST 24 HOURS")
        print("\nThis means:")
        print("1. TradingView alerts are not firing")
        print("2. Webhook URL is incorrect")
        print("3. Railway endpoint is not receiving requests")
        print("4. Indicator alert() function is not being called")
    else:
        print(f"\n✓ Found {len(results)} webhook events in last 24 hours:")
        print("\n" + "-"*80)
        for row in results:
            event_type, trade_id, direction, sig_date, sig_time, timestamp, entry, stop = row
            print(f"Event: {event_type}")
            print(f"Trade ID: {trade_id}")
            print(f"Direction: {direction}")
            print(f"Signal Time: {sig_date} {sig_time}")
            print(f"Received: {timestamp}")
            print(f"Entry: {entry}, Stop: {stop}")
            print("-"*80)
    
    # Check webhook stats endpoint data
    print("\n" + "="*80)
    print("CHECKING WEBHOOK STATISTICS")
    print("="*80)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total_webhooks,
            COUNT(DISTINCT trade_id) as unique_trades,
            MIN(timestamp) as first_webhook,
            MAX(timestamp) as last_webhook
        FROM automated_signals
    """)
    
    stats = cur.fetchone()
    total, unique, first, last = stats
    
    print(f"\nTotal webhook events: {total}")
    print(f"Unique trades: {unique}")
    print(f"First webhook: {first}")
    print(f"Last webhook: {last}")
    
    if last:
        time_since_last = datetime.now() - last.replace(tzinfo=None)
        print(f"Time since last webhook: {time_since_last}")
        
        if time_since_last > timedelta(hours=1):
            print("\n⚠️ WARNING: No webhooks received in over 1 hour")
            print("This suggests the indicator is not sending alerts")
    
    # Check event type distribution
    print("\n" + "="*80)
    print("EVENT TYPE DISTRIBUTION")
    print("="*80)
    
    cur.execute("""
        SELECT 
            event_type,
            COUNT(*) as count
        FROM automated_signals
        GROUP BY event_type
        ORDER BY count DESC
    """)
    
    event_types = cur.fetchall()
    for event_type, count in event_types:
        print(f"{event_type}: {count}")
    
    cur.close()
    conn.close()

def check_tradingview_alert_setup():
    """Provide checklist for TradingView alert setup"""
    print("\n" + "="*80)
    print("TRADINGVIEW ALERT SETUP CHECKLIST")
    print("="*80)
    
    print("""
1. ALERT CREATION:
   - Right-click on chart → Add Alert
   - Condition: "complete_automated_trading_system" (indicator name)
   - Alert name: "Automated Trading Signals"
   
2. WEBHOOK URL:
   - URL: https://web-production-cd33.up.railway.app/api/automated-signals/webhook
   - Method: POST (automatic)
   
3. MESSAGE:
   - Use: {{strategy.order.alert_message}}
   - OR leave blank (indicator sends its own message)
   
4. SETTINGS:
   - Frequency: "Once Per Bar Close"
   - Expiration: "Open-ended"
   - ✓ Webhook URL checkbox MUST be checked
   
5. VERIFY:
   - Alert appears in alerts list
   - Webhook URL is visible in alert details
   - Alert is ACTIVE (not paused)
   
6. TEST:
   - Wait for next signal confirmation
   - Check Railway logs for webhook reception
   - Check database for new entries
""")

def check_railway_endpoint():
    """Check if Railway endpoint is accessible"""
    print("\n" + "="*80)
    print("RAILWAY ENDPOINT CHECK")
    print("="*80)
    
    import requests
    
    webhook_url = "https://web-production-cd33.up.railway.app/api/automated-signals/webhook"
    health_url = "https://web-production-cd33.up.railway.app/api/webhook-health"
    
    print(f"\nWebhook URL: {webhook_url}")
    print(f"Health URL: {health_url}")
    
    try:
        # Check health endpoint
        response = requests.get(health_url, timeout=10)
        print(f"\n✓ Health endpoint accessible: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"\n❌ Health endpoint error: {e}")
    
    try:
        # Test webhook endpoint with sample payload
        test_payload = {
            "type": "ENTRY",
            "signal_id": "TEST_20241113_120000_BULLISH",
            "date": "2024-11-13",
            "time": "12:00:00",
            "bias": "Bullish",
            "session": "NY AM",
            "entry_price": 4500.0,
            "sl_price": 4475.0,
            "risk_distance": 25.0,
            "be_price": 4500.0,
            "target_1r": 4525.0,
            "target_2r": 4550.0,
            "target_3r": 4575.0,
            "be_hit": False,
            "be_mfe": 0.0,
            "no_be_mfe": 0.0,
            "status": "active",
            "timestamp": 1699891200000
        }
        
        print("\n\nTesting webhook endpoint with sample payload...")
        response = requests.post(webhook_url, json=test_payload, timeout=10)
        print(f"✓ Webhook endpoint accessible: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"\n❌ Webhook endpoint error: {e}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("AUTOMATED SIGNALS WEBHOOK DIAGNOSTIC")
    print("="*80)
    
    check_recent_webhooks()
    check_tradingview_alert_setup()
    check_railway_endpoint()
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)

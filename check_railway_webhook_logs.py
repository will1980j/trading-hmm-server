"""
Check Railway logs to see if webhooks are being received
"""
import requests
import json

def check_recent_webhook_activity():
    """Check if webhooks are reaching the server"""
    print("=" * 80)
    print("CHECKING WEBHOOK ACTIVITY ON RAILWAY")
    print("=" * 80)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Try to send a test webhook to see if it's received
    print("\n1. Sending test webhook...")
    test_payload = {
        "type": "ENTRY",
        "signal_id": "TEST_20251114_141600_BEARISH",
        "direction": "Bearish",
        "entry_price": 24968.0,
        "stop_loss": 24986.75,
        "risk_distance": 18.75,
        "num_contracts": 1,
        "session": "LONDON",
        "htf_bias": "Bearish",
        "timestamp": 1731584000000
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/automated-signals/webhook",
            json=test_payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("\n   ✅ Webhook endpoint is working!")
            
            # Now check if it was stored
            print("\n2. Checking if test signal was stored...")
            stats_response = requests.get(f"{base_url}/api/automated-signals/stats-live", timeout=10)
            if stats_response.status_code == 200:
                data = stats_response.json()
                print(f"   Total signals in database: {data.get('total_signals', 0)}")
                
                if data.get('total_signals', 0) > 0:
                    print("\n   ✅ Test signal was stored successfully!")
                    print("\n   🎯 WEBHOOK SYSTEM IS WORKING!")
                    print("\n   ⚠️  Issue: TradingView alerts may not be configured correctly")
                    print("\n   Check TradingView alert settings:")
                    print("      - Webhook URL must be exact")
                    print("      - Alert message should be: {{strategy.order.alert_message}}")
                    print("      - Or leave message blank")
                else:
                    print("\n   ❌ Test signal was NOT stored!")
                    print("\n   Issue: Webhook received but not saved to database")
        else:
            print(f"\n   ❌ Webhook endpoint returned error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"\n   ❌ Failed to send test webhook: {e}")

def analyze_alert_log_format():
    """Analyze the alert log format from the screenshot"""
    print("\n" + "=" * 80)
    print("ANALYZING ALERT LOG FORMAT")
    print("=" * 80)
    
    print("\n📋 From your screenshot, alerts are sending:")
    print('   {"type":"MFE_UPDATE","signal_id":"20251114_041600000_BEARISH",...}')
    print('   {"type":"ENTRY","signal_id":"20251114_041600000_BEARISH",...}')
    
    print("\n✅ Format looks correct!")
    print("\n🔍 Possible issues:")
    print("   1. Webhook URL in TradingView alert is wrong")
    print("   2. Alert message field has extra text (should be blank or {{strategy.order.alert_message}})")
    print("   3. Network/firewall blocking webhooks")
    print("   4. Railway deployment issue")

def main():
    print("\n🔍 RAILWAY WEBHOOK DIAGNOSTIC\n")
    
    check_recent_webhook_activity()
    analyze_alert_log_format()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. If test webhook worked:")
    print("   → Problem is with TradingView alert configuration")
    print("   → Double-check webhook URL in alert settings")
    print("   → Make sure alert message is: {{strategy.order.alert_message}}")
    print("\n2. If test webhook failed:")
    print("   → Problem is with Railway backend")
    print("   → Check Railway deployment logs")
    print("   → Verify database connection")

if __name__ == '__main__':
    main()

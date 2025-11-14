"""
Check what's actually in the TradingView alert log
"""
import requests

def check_recent_activity():
    """Check if any webhooks hit the server recently"""
    print("=" * 80)
    print("CHECKING RECENT WEBHOOK ACTIVITY")
    print("=" * 80)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Check dashboard for any new signals
    print("\n1. Checking dashboard for signals...")
    response = requests.get(f"{base_url}/api/automated-signals/dashboard-data", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        active = data.get('active_trades', [])
        completed = data.get('completed_trades', [])
        
        print(f"   Active: {len(active)}")
        print(f"   Completed: {len(completed)}")
        
        if active:
            print("\n   Most recent active trade:")
            latest = active[0]
            print(f"   Trade ID: {latest.get('trade_id')}")
            print(f"   Direction: {latest.get('bias')}")
            print(f"   Entry: {latest.get('entry_price')}")
            print(f"   Time: {latest.get('signal_date')} {latest.get('signal_time')}")
    
    print("\n" + "=" * 80)
    print("WHAT TO CHECK IN TRADINGVIEW")
    print("=" * 80)
    
    print("\n📋 In TradingView Alert Log:")
    print("   1. Click Alert icon (bell)")
    print("   2. Click 'Log' tab")
    print("   3. Find your most recent alert")
    print("   4. Click on it")
    print("   5. Look for:")
    print("      - ✅ 'Webhook sent successfully'")
    print("      - ❌ 'Webhook failed' or error message")
    print("      - ❌ 'No webhook configured'")
    
    print("\n📝 Check the webhook payload:")
    print("   - Should start with: {\"type\":\"ENTRY\"...")
    print("   - Should have: signal_id, entry_price, sl_price, etc.")
    print("   - Should NOT have extra text before/after JSON")
    
    print("\n🔍 Common issues:")
    print("   1. Alert log shows 'Webhook failed' → URL is wrong")
    print("   2. Alert log shows success but no dashboard → Payload format wrong")
    print("   3. No webhook in log → Webhook URL not configured")

def main():
    check_recent_activity()
    
    print("\n" + "=" * 80)
    print("NEXT STEP")
    print("=" * 80)
    print("\nPlease check your TradingView Alert Log and tell me:")
    print("  1. Does it say 'Webhook sent successfully'?")
    print("  2. What does the payload look like?")
    print("  3. Any error messages?")

if __name__ == '__main__':
    main()

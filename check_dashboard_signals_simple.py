"""
Simple check for dashboard signals via API
"""
import requests
import json

def check_dashboard_data():
    """Check dashboard data via API"""
    print("=" * 80)
    print("CHECKING AUTOMATED SIGNALS DASHBOARD")
    print("=" * 80)
    
    base_url = "https://web-production-cd33.up.railway.app"
    
    # Check stats endpoint
    print("\n1. Checking Stats Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/automated-signals/stats-live", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n   📊 Stats:")
            print(f"      Active Trades: {data.get('active_count', 0)}")
            print(f"      Completed Trades: {data.get('completed_count', 0)}")
            print(f"      Total Signals: {data.get('total_signals', 0)}")
            print(f"      Win Rate: {data.get('win_rate', 0)}%")
            print(f"      Avg MFE: {data.get('avg_mfe', 0)}")
            
            if data.get('total_signals', 0) == 0:
                print("\n   ❌ NO SIGNALS IN DATABASE!")
            else:
                print(f"\n   ✅ Found {data.get('total_signals', 0)} signals")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check dashboard data endpoint
    print("\n2. Checking Dashboard Data Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/automated-signals/dashboard-data", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            active = data.get('active_trades', [])
            completed = data.get('completed_trades', [])
            
            print(f"\n   📊 Dashboard Data:")
            print(f"      Active Trades: {len(active)}")
            print(f"      Completed Trades: {len(completed)}")
            
            if len(active) > 0:
                print(f"\n   ✅ Active Trades:")
                for trade in active[:3]:  # Show first 3
                    print(f"      - {trade.get('trade_id')}: {trade.get('direction')} @ {trade.get('entry_price')}")
            
            if len(completed) > 0:
                print(f"\n   ✅ Completed Trades:")
                for trade in completed[:3]:  # Show first 3
                    print(f"      - {trade.get('trade_id')}: {trade.get('direction')} @ {trade.get('entry_price')}")
            
            if len(active) == 0 and len(completed) == 0:
                print("\n   ❌ NO TRADES IN DASHBOARD!")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Check webhook health
    print("\n3. Checking Webhook Health...")
    try:
        response = requests.get(f"{base_url}/api/webhook-health", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n   📊 Webhook Health:")
            print(f"      Status: {data.get('status', 'unknown')}")
            print(f"      Last Signal: {data.get('last_signal_time', 'never')}")
        else:
            print(f"   ⚠️  Endpoint not available")
    except Exception as e:
        print(f"   ⚠️  Not available: {e}")

def check_tradingview_setup():
    """Provide TradingView setup checklist"""
    print("\n" + "=" * 80)
    print("TRADINGVIEW SETUP CHECKLIST")
    print("=" * 80)
    
    print("\n❓ Have you updated the indicator in TradingView?")
    print("\n   The fixes we made today are ONLY in the local file!")
    print("   You must copy/paste the updated code to TradingView.")
    
    print("\n📋 Steps to Deploy Updated Indicator:")
    print("\n   1. Open complete_automated_trading_system.pine in editor")
    print("   2. Select ALL code (Ctrl+A)")
    print("   3. Copy (Ctrl+C)")
    print("   4. Open TradingView Pine Editor")
    print("   5. Paste code (Ctrl+V)")
    print("   6. Click 'Save'")
    print("   7. Add to chart")
    print("   8. Create/Update alert:")
    print("      - Condition: 'Any alert() function call'")
    print("      - Webhook URL: https://web-production-cd33.up.railway.app/api/automated-signals/webhook")
    print("      - Frequency: 'Once Per Bar Close'")
    
    print("\n⚠️  CRITICAL: If you haven't done this, the dashboard won't receive signals!")

def main():
    print("\n🔍 DASHBOARD SIGNALS DIAGNOSTIC\n")
    
    check_dashboard_data()
    check_tradingview_setup()
    
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    
    print("\n💡 If dashboard shows 0 signals:")
    print("   1. Update indicator in TradingView (most common issue)")
    print("   2. Verify alert is configured with webhook URL")
    print("   3. Check that market is open and generating signals")
    print("   4. Look for errors in TradingView Pine Editor logs")
    print("   5. Verify 'Track BE=1 MFE' is enabled in indicator settings")

if __name__ == '__main__':
    main()

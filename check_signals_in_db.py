"""
Check what signals are actually in the database
"""
import requests

def check_signals():
    print("🔍 Checking signals in database...")
    print("=" * 60)
    
    # This endpoint requires auth, but let's try
    try:
        # Try to get recent signals
        response = requests.get(
            "https://web-production-cd33.up.railway.app/api/live-signals?timeframe=1m",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            signals = data.get('signals', [])
            
            print(f"✅ Found {len(signals)} signals in database")
            
            if signals:
                print("\n📊 Recent signals:")
                for signal in signals[:10]:
                    print(f"   {signal.get('bias')} at {signal.get('price')} - {signal.get('timestamp')}")
            else:
                print("\n⚠️ No signals in database yet")
                print("\n💡 This means:")
                print("   1. TradingView alert hasn't fired yet")
                print("   2. OR alert is not configured correctly")
                
        elif response.status_code == 302 or response.status_code == 401:
            print("🔒 Endpoint requires authentication")
            print("💡 Open ML dashboard in browser to check signals")
            
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("\n🎯 To verify TradingView alert:")
    print("   1. Open TradingView")
    print("   2. Click Alert button (clock icon)")
    print("   3. Check your alert has GREEN dot (active)")
    print("   4. Verify webhook URL is correct")
    print("   5. Wait for a triangle to appear on chart")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_signals()

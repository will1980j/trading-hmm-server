"""
Complete test sequence after Railway restart
"""
import requests
import time

def wait_for_server():
    """Wait for Railway to come back online"""
    print("⏳ Waiting for Railway to restart...")
    max_attempts = 30
    
    for i in range(max_attempts):
        try:
            response = requests.get(
                "https://web-production-cd33.up.railway.app/health",
                timeout=5
            )
            if response.status_code == 200:
                print(f"\n✅ Server is back online! (took {i*2}s)")
                return True
        except:
            pass
        
        print(f"   Attempt {i+1}/{max_attempts}...", end='\r')
        time.sleep(2)
    
    print("\n❌ Server didn't come back online")
    return False

def test_webhook():
    """Test webhook with simple signal"""
    print("\n🧪 Testing webhook...")
    
    signal = {
        "symbol": "NQ1!",
        "timeframe": "1m",
        "signal_type": "BIAS_CHANGE",
        "bias": "Bullish",
        "price": 21000.50,
        "strength": 85,
        "htf_aligned": True,
        "htf_status": "ALIGNED"
    }
    
    try:
        response = requests.post(
            "https://web-production-cd33.up.railway.app/api/live-signals",
            json=signal,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ WEBHOOK WORKING!")
            data = response.json()
            print(f"   Signal ID: {data.get('signal_id')}")
            print(f"   Bias: {data.get('bias')}")
            return True
        else:
            print(f"❌ Failed: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_ml_dashboard():
    """Check if signal appears in ML dashboard"""
    print("\n📊 Checking ML dashboard...")
    
    try:
        response = requests.get(
            "https://web-production-cd33.up.railway.app/api/webhook-stats",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard accessible")
            
            if data.get('last_24h'):
                for item in data['last_24h']:
                    print(f"   {item['bias']}: {item['count']} signals")
            
            return True
        else:
            print(f"⚠️ Dashboard returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("POST-RESTART TEST SEQUENCE")
    print("=" * 60)
    
    # Step 1: Wait for server
    if not wait_for_server():
        print("\n💡 Server didn't restart. Check Railway dashboard.")
        exit(1)
    
    # Step 2: Test webhook
    print("\n" + "=" * 60)
    if not test_webhook():
        print("\n💡 Webhook still failing. May need Option B (code fix).")
        exit(1)
    
    # Step 3: Check dashboard
    print("\n" + "=" * 60)
    check_ml_dashboard()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n🎯 Next steps:")
    print("   1. Open: https://web-production-cd33.up.railway.app/ml-dashboard")
    print("   2. Wait for TradingView signal to fire")
    print("   3. Watch signals appear in real-time!")
    print("\n" + "=" * 60)

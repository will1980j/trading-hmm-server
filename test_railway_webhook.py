"""
Test Railway webhook endpoint after deployment
Run this after Railway finishes deploying
"""
import requests
import json
from datetime import datetime

def test_webhook():
    """Test the webhook endpoint with a sample signal"""
    
    url = "https://web-production-cd33.up.railway.app/api/live-signals"
    
    # Sample signal matching TradingView format
    signal = {
        "symbol": "NQ1!",
        "timeframe": "1m",
        "signal_type": "BIAS_CHANGE",
        "bias": "Bullish",
        "price": 21000.50,
        "strength": 85,
        "htf_aligned": True,
        "htf_status": "ALIGNED"  # Shortened to fit database column
    }
    
    print("🧪 Testing Railway webhook endpoint...")
    print(f"📤 Sending: {signal['bias']} signal at {signal['price']}")
    
    try:
        response = requests.post(
            url,
            json=signal,
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Body: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Webhook is working!")
            print("🎯 Signal should now appear in ML Intelligence Hub")
            print("🔗 Check: https://web-production-cd33.up.railway.app/ml-dashboard")
            return True
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            print("💡 Check Railway logs for errors")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏱️ TIMEOUT - Railway might still be deploying")
        print("💡 Wait 1-2 minutes and try again")
        return False
        
    except requests.exceptions.ConnectionError:
        print("\n🔌 CONNECTION ERROR - Railway might be restarting")
        print("💡 Wait 1-2 minutes and try again")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def check_health():
    """Check if Railway server is up"""
    print("\n🏥 Checking Railway health...")
    
    try:
        response = requests.get(
            "https://web-production-cd33.up.railway.app/health",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is UP")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server is DOWN or deploying: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Railway Webhook Test")
    print("=" * 60)
    
    # First check if server is up
    if check_health():
        print("\n" + "=" * 60)
        # Then test webhook
        test_webhook()
    else:
        print("\n💡 Railway is still deploying. Wait 1-2 minutes and run this again.")
    
    print("\n" + "=" * 60)

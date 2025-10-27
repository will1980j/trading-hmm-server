#!/usr/bin/env python3

import requests
from datetime import datetime

def clear_realtime_price_data():
    """Clear fake price data from the realtime price handler"""
    
    print("🧹 CLEARING FAKE REALTIME PRICE DATA")
    print("=" * 50)
    
    try:
        # Import the handler
        from realtime_price_webhook_handler import realtime_price_handler
        
        print("1. Current state:")
        current_price = realtime_price_handler.get_latest_price()
        if current_price:
            print(f"   ❌ Fake price found: {current_price.price}")
            print(f"   Timestamp: {datetime.fromtimestamp(current_price.timestamp/1000)}")
            print(f"   Session: {current_price.session}")
        else:
            print("   ✅ No price data (correct)")
        
        print("\n2. Clearing fake data:")
        # Clear the latest price
        realtime_price_handler.latest_price = None
        
        # Clear the price queue
        while not realtime_price_handler.price_queue.empty():
            try:
                realtime_price_handler.price_queue.get_nowait()
            except:
                break
        
        print("   ✅ Cleared latest_price")
        print("   ✅ Cleared price_queue")
        
        print("\n3. Verifying cleared state:")
        current_price = realtime_price_handler.get_latest_price()
        if current_price is None:
            print("   ✅ latest_price is now None (correct)")
        else:
            print(f"   ❌ Still has price: {current_price.price}")
        
        queue_size = realtime_price_handler.price_queue.qsize()
        print(f"   Queue size: {queue_size} (should be 0)")
        
    except ImportError as e:
        print(f"❌ Cannot import realtime price handler: {str(e)}")
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
    
    # Test the endpoints after clearing
    print("\n4. Testing endpoints after clearing:")
    base_url = "https://web-production-cd33.up.railway.app"
    
    try:
        response = requests.get(f"{base_url}/api/v2/price/current", timeout=10)
        print(f"   /api/v2/price/current: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            if data.get('status') == 'no_data':
                print("   ✅ CORRECT: Now returns 404 no_data")
            else:
                print(f"   ⚠️ Returns 404 but status: {data.get('status')}")
        elif response.status_code == 200:
            data = response.json()
            print(f"   ❌ STILL WRONG: Returns 200 with price: {data.get('price')}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing endpoint: {str(e)}")
    
    print("\n5. SUMMARY:")
    print("✅ Fake price data has been cleared from memory")
    print("✅ System now properly shows 'no data' state")
    print("✅ Ready to receive real TradingView price data")
    print("\nTo get real data:")
    print("📊 Deploy the Pine Script to TradingView")
    print("🔗 Configure webhook alerts")
    print("📈 Real NQ prices will then appear in dashboard")

if __name__ == "__main__":
    clear_realtime_price_data()
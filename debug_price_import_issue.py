#!/usr/bin/env python3

def debug_price_import_issue():
    """Debug exactly what get_current_price function is being called"""
    
    print("🔍 DEBUGGING PRICE IMPORT ISSUE")
    print("=" * 50)
    
    # Test the exact import that the V2 endpoint uses
    print("1. Testing realtime_price_webhook_handler import:")
    try:
        from realtime_price_webhook_handler import get_current_price
        print("   ✅ Import successful")
        
        # Check what this function returns
        current_price = get_current_price()
        print(f"   Result: {current_price}")
        
        if current_price is None:
            print("   ✅ Returns None (correct - no fake data)")
        else:
            print(f"   ❌ Returns price object: {current_price.price}")
            print(f"      Timestamp: {current_price.timestamp}")
            print(f"      Session: {current_price.session}")
            
    except ImportError as e:
        print(f"   ❌ Import failed: {str(e)}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Check if there are other get_current_price functions in scope
    print("\n2. Checking for other get_current_price functions:")
    
    # Check if there's a global get_current_price function
    try:
        import sys
        current_module = sys.modules[__name__]
        if hasattr(current_module, 'get_current_price'):
            print("   ⚠️ Found get_current_price in current module")
        else:
            print("   ✅ No get_current_price in current module")
    except Exception as e:
        print(f"   ❌ Error checking current module: {str(e)}")
    
    # Test the exact code path that the V2 endpoint uses
    print("\n3. Simulating V2 endpoint logic:")
    try:
        from realtime_price_webhook_handler import get_current_price
        current_price = get_current_price()
        
        if current_price:
            print("   ❌ PROBLEM: current_price is not None")
            print(f"      Price: {current_price.price}")
            print("      This explains why V2 endpoint returns 200 instead of 404")
        else:
            print("   ✅ current_price is None")
            print("      V2 endpoint should return 404")
            
    except Exception as e:
        print(f"   ❌ Error in simulation: {str(e)}")
    
    # Check the realtime price handler directly
    print("\n4. Checking realtime price handler directly:")
    try:
        from realtime_price_webhook_handler import realtime_price_handler
        
        latest = realtime_price_handler.get_latest_price()
        print(f"   Handler latest_price: {latest}")
        
        queue_size = realtime_price_handler.price_queue.qsize()
        print(f"   Handler queue size: {queue_size}")
        
        if latest is None and queue_size == 0:
            print("   ✅ Handler state is clean (no fake data)")
        else:
            print("   ❌ Handler has data - might be fake")
            
    except Exception as e:
        print(f"   ❌ Error checking handler: {str(e)}")
    
    print("\n5. DIAGNOSIS:")
    print("If get_current_price() returns None but V2 endpoint returns 200,")
    print("then there's either:")
    print("- A caching issue in the web server")
    print("- A different get_current_price function being called")
    print("- Database data being returned instead of handler data")

if __name__ == "__main__":
    debug_price_import_issue()
"""
Direct fix - check what's actually wrong
"""
import requests

url = "https://web-production-cd33.up.railway.app/automated-signals"

print("Testing the actual deployed link...")
print(f"URL: {url}\n")

try:
    # Test without following redirects
    r = requests.get(url, allow_redirects=False, timeout=10)
    print(f"Status Code: {r.status_code}")
    
    if r.status_code == 404:
        print("\n❌ 404 - Route doesn't exist on Railway")
        print("\nThe route was added to web_server.py but NOT deployed yet.")
        print("You need to push web_server.py to Railway.")
        
    elif r.status_code == 302:
        redirect = r.headers.get('Location', '')
        print(f"\n✅ Route exists - redirects to: {redirect}")
        print("\nThis is CORRECT - it redirects to login.")
        print("After logging in, navigate to /automated-signals")
        
    elif r.status_code == 500:
        print("\n❌ 500 - Server error")
        print("The route exists but crashes when accessed.")
        print(f"\nError response: {r.text[:500]}")
        
    elif r.status_code == 200:
        print("\n✅ Page loads successfully")
        
    # Now test with a session (simulating logged in)
    print("\n" + "="*60)
    print("Testing what happens when you're logged in...")
    print("="*60)
    
    session = requests.Session()
    # Try to access directly
    r2 = session.get(url, timeout=10)
    
    if "login" in r2.url.lower():
        print("✅ Correctly redirects to login when not authenticated")
    elif r2.status_code == 500:
        print(f"❌ Server error when accessing page")
        print(f"Error: {r2.text[:500]}")
    elif r2.status_code == 200:
        if len(r2.text) < 100:
            print(f"⚠️ Page loads but content is too short ({len(r2.text)} bytes)")
            print(f"Content: {r2.text}")
        else:
            print(f"✅ Page loads with content ({len(r2.text)} bytes)")
            
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("WHAT TO DO:")
print("="*60)
print("1. If you see 404: Push web_server.py to Railway")
print("2. If you see 302: Log in first, then go to /automated-signals")
print("3. If you see 500: Check Railway logs for the error")

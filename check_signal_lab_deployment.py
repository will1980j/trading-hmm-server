"""
Check Signal Lab Dashboard deployment
"""
import requests

print("=" * 60)
print("CHECKING SIGNAL LAB DASHBOARD")
print("=" * 60)

url = "https://web-production-cd33.up.railway.app/signal-lab-dashboard"

print(f"\n🔍 Checking: {url}")
try:
    response = requests.get(url, timeout=10, allow_redirects=False)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 500:
        print("\n❌ 500 Internal Server Error")
        print("\nError details:")
        print(response.text[:1000])
        
        # Look for specific error patterns
        if "TemplateNotFound" in response.text:
            print("\n🚨 Template file not found!")
        elif "SyntaxError" in response.text:
            print("\n🚨 Python syntax error!")
        elif "ImportError" in response.text:
            print("\n🚨 Import error!")
            
    elif response.status_code == 302:
        print(f"✅ Redirect to: {response.headers.get('Location')}")
        print("(Probably redirecting to login)")
        
    elif response.status_code == 200:
        print("✅ Dashboard loaded successfully!")
        print(f"Content length: {len(response.text)} bytes")
        
except Exception as e:
    print(f"❌ Error: {e}")

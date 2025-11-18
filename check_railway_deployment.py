"""
Check Railway deployment status and logs
"""
import requests
import sys

print("=" * 60)
print("CHECKING RAILWAY DEPLOYMENT")
print("=" * 60)

# Try to access the site
url = "https://web-production-cd33.up.railway.app/"

print(f"\n🔍 Checking: {url}")
try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 500:
        print("\n❌ 500 Internal Server Error")
        print("\nResponse content:")
        print(response.text[:500])  # First 500 chars
        
        # Check if it's a Python error
        if "Traceback" in response.text or "Error" in response.text:
            print("\n🐍 Python error detected in response")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("NEXT STEPS")
print("=" * 60)
print("1. Check Railway dashboard for build logs")
print("2. Look for Python syntax errors or import issues")
print("3. Verify templates/signal_lab_dashboard.html deployed correctly")

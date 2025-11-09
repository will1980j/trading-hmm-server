"""Check if automated signals dashboard is live"""
import requests

url = "https://web-production-cd33.up.railway.app/automated-signals"

try:
    response = requests.get(url, allow_redirects=False, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 404:
        print("\n❌ DASHBOARD NOT FOUND (404)")
        print("\nThis means the route is NOT deployed to Railway yet.")
        print("\nYou need to:")
        print("1. Commit web_server.py and templates/*.html files")
        print("2. Push to GitHub")
        print("3. Wait for Railway to deploy")
        
    elif response.status_code == 302:
        print("\n✅ DASHBOARD EXISTS (redirecting to login)")
        print(f"Redirect to: {response.headers.get('Location', 'unknown')}")
        
    elif response.status_code == 200:
        print("\n✅ DASHBOARD ACCESSIBLE")
        
    else:
        print(f"\n⚠️ Unexpected status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out - Railway might be down")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - check Railway status")
except Exception as e:
    print(f"❌ Error: {e}")

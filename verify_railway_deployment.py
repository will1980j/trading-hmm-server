import requests
from requests.auth import HTTPBasicAuth

# Try to get the actual HTML content from Railway
url = "https://web-production-cd33.up.railway.app/automated-signals-option2"

session = requests.Session()

# First, try without auth to see what we get
response = session.get(url, allow_redirects=True)
print(f"Status: {response.status_code}")
print(f"Final URL: {response.url}")
print(f"\nFirst 1000 chars of response:")
print(response.text[:1000])

# Check for the distinctive markers
if "Minimalist Trader's Cockpit" in response.text:
    print("\n✅ CORRECT: Light theme Option 2 is deployed")
elif "background: #f8f9fa" in response.text:
    print("\n✅ CORRECT: Light background detected")
elif "background: #0f1419" in response.text or "background: #0a0e27" in response.text:
    print("\n❌ WRONG: Dark theme is deployed (Option 1 duplicate)")
else:
    print("\n⚠️ UNKNOWN: Can't determine which version")

# Check if it's the login page
if "login" in response.url.lower() or "Login" in response.text[:500]:
    print("\n⚠️ Redirected to login page - need to authenticate to see dashboard")

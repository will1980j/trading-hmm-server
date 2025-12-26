"""
Test to diagnose the 500 error on deployed homepage
"""

import requests

# Test if homepage returns 500
response = requests.get("https://web-production-f8c3.up.railway.app/homepage", allow_redirects=False)

print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")

if response.status_code == 500:
    print("\n❌ 500 ERROR CONFIRMED")
    print("\nResponse text (first 500 chars):")
    print(response.text[:500])
elif response.status_code == 302:
    print("\n⚠️  REDIRECT (probably to login)")
    print(f"Location: {response.headers.get('Location')}")
else:
    print(f"\n✅ Status {response.status_code}")

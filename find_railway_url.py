#!/usr/bin/env python3
"""
Find the correct Railway deployment URL
"""

import requests

# Common Railway URL patterns
possible_urls = [
    "https://trading-hmm-server-production.up.railway.app",
    "https://web-production-1234.up.railway.app", 
    "https://trading-hmm-server.up.railway.app",
    "https://trading-server-production.up.railway.app",
    "https://hmm-server-production.up.railway.app"
]

def test_url(url):
    """Test if a URL is responding"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code, response.text[:100]
    except Exception as e:
        return None, str(e)[:50]

print("Testing possible Railway URLs...")
print("=" * 40)

for url in possible_urls:
    status, response = test_url(url)
    if status:
        print(f"{url}: {status} - {response}")
        if status == 200:
            print(f"*** FOUND WORKING URL: {url} ***")
            break
    else:
        print(f"{url}: ERROR - {response}")

print("\nIf none work, check your Railway dashboard for the correct URL")
print("Look for: Project > Deployments > Domain")
"""
Find the correct dashboard URL
"""

import requests

# Try different possible URLs
urls = [
    "https://web-production-cd33.up.railway.app/automated-signals-dashboard",
    "https://web-production-cd33.up.railway.app/automated-signals",
    "https://web-production-cd33.up.railway.app/signal-lab-dashboard",
]

for url in urls:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            if 'Automated Signals' in response.text or 'Live Signals' in response.text:
                print(f"  ✅ FOUND IT!")
                
                # Quick check for our changes
                if 'trade-status-indicator' in response.text:
                    print("  ✅ Status indicator CSS present")
                else:
                    print("  ❌ Status indicator CSS missing")
                    
                if 'MFE (BE=1)' in response.text:
                    print("  ✅ MFE columns updated")
                else:
                    print("  ❌ MFE columns not updated")
                break
    except Exception as e:
        print(f"  Error: {e}")

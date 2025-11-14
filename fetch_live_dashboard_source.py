"""
Fetch the actual HTML source from Railway to see what should be there
"""

import requests

url = "https://web-production-cd33.up.railway.app/automated-signals"

response = requests.get(url)

if response.status_code == 200:
    html = response.text
    
    # Save it to a file so we can see what's actually deployed
    with open('LIVE_DASHBOARD_SOURCE.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Check for iframe
    if 'iframe' in html.lower():
        print("✅ Found iframe in live version")
        # Extract iframe lines
        lines = html.split('\n')
        for i, line in enumerate(lines):
            if 'iframe' in line.lower():
                print(f"\nLine {i}: {line}")
    else:
        print("❌ No iframe found in live version")
    
    # Check for diagnostics
    if 'diagnostic' in html.lower():
        print("✅ Found 'diagnostic' text in live version")
    else:
        print("❌ No 'diagnostic' text in live version")
        
    print(f"\nSaved full HTML to LIVE_DASHBOARD_SOURCE.html ({len(html)} bytes)")
else:
    print(f"Error: {response.status_code}")

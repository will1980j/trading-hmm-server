"""
Verify D3.js is deployed and check what's actually breaking
"""

import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

print("Checking deployed dashboard for D3.js...")
print("=" * 80)

response = requests.get(f"{BASE_URL}/automated-signals-dashboard")

if response.status_code == 200:
    html = response.text
    
    # Check for D3.js
    if 'd3.v7.min.js' in html or 'd3.min.js' in html or 'd3js.org' in html:
        print("✅ D3.js library IS deployed")
        
        # Find the exact script tag
        for line in html.split('\n'):
            if 'd3' in line.lower() and 'script' in line.lower():
                print(f"   Found: {line.strip()}")
    else:
        print("❌ D3.js library NOT deployed")
        print("   Railway hasn't picked up the change yet")
    
    # Check for modal
    if 'id="tradeDetailModal"' in html:
        print("✅ Trade detail modal IS deployed")
    else:
        print("❌ Trade detail modal NOT deployed")
    
    # Check for journey container
    if 'id="journeyViz"' in html:
        print("✅ Journey viz container IS deployed")
    else:
        print("❌ Journey viz container NOT deployed")
    
    # Check for functions
    if 'function showTradeDetail' in html or 'showTradeDetail(' in html:
        print("✅ showTradeDetail function IS deployed")
    else:
        print("❌ showTradeDetail function NOT deployed")
    
    if 'function renderTradeJourney' in html or 'renderTradeJourney(' in html:
        print("✅ renderTradeJourney function IS deployed")
    else:
        print("❌ renderTradeJourney function NOT deployed")
    
    # Check for clickable rows
    if 'clickable-row' in html:
        print("✅ Clickable row class IS deployed")
    else:
        print("❌ Clickable row class NOT deployed")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("1. Open browser console (F12)")
    print("2. Type: d3")
    print("3. If it shows an object, D3 is loaded")
    print("4. Click a trade row")
    print("5. Check console for errors")
    
else:
    print(f"❌ Failed to fetch dashboard: {response.status_code}")

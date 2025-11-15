"""
Check what's actually deployed on Railway
"""

import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

# Fetch the actual deployed HTML
response = requests.get(f"{BASE_URL}/automated-signals-dashboard")
html = response.text

print("Checking deployed dashboard...")
print("=" * 80)

# Check for D3.js
if 'd3.js' in html or 'd3.v7' in html:
    print("✅ D3.js library IS present")
else:
    print("❌ D3.js library NOT found")

# Check for journey visualization function
if 'renderTradeJourney' in html:
    print("✅ renderTradeJourney function IS present")
else:
    print("❌ renderTradeJourney function NOT found")

# Check for minimal journey function
if 'renderMinimalJourney' in html:
    print("✅ renderMinimalJourney function IS present")
else:
    print("❌ renderMinimalJourney function NOT found")

# Check for journey container
if 'journey-container' in html:
    print("✅ journey-container div IS present")
else:
    print("❌ journey-container div NOT found")

# Check for trade detail modal
if 'tradeDetailModal' in html:
    print("✅ Trade detail modal IS present")
else:
    print("❌ Trade detail modal NOT found")

# Check for onclick handler
if 'showTradeDetail' in html:
    print("✅ showTradeDetail function IS present")
else:
    print("❌ showTradeDetail function NOT found")

# Check if rows are clickable
if 'clickable-row' in html:
    print("✅ clickable-row class IS present")
else:
    print("❌ clickable-row class NOT found")

print("\n" + "=" * 80)
print("If everything shows ✅ but visualization is empty, the issue is in the JavaScript logic")

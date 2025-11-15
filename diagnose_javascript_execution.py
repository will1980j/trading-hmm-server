"""
Diagnose why the JavaScript visualization isn't executing
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://web-production-cd33.up.railway.app"

print("Fetching deployed dashboard HTML...")
print("=" * 80)

response = requests.get(f"{BASE_URL}/automated-signals-dashboard", allow_redirects=True)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for D3.js library
    d3_scripts = soup.find_all('script', src=lambda x: x and 'd3' in x.lower())
    print(f"D3.js script tags found: {len(d3_scripts)}")
    for script in d3_scripts:
        print(f"  - {script.get('src')}")
    
    # Check for modal container
    modal = soup.find('div', id='tradeDetailModal')
    print(f"\nTrade detail modal found: {'✅' if modal else '❌'}")
    
    # Check for journey container
    journey = soup.find('div', id='journeyViz')
    print(f"Journey viz container found: {'✅' if journey else '❌'}")
    
    # Check for clickable row class in table
    clickable_rows = soup.find_all('tr', class_='clickable-row')
    print(f"Clickable rows in HTML: {len(clickable_rows)}")
    
    # Check for showTradeDetail function
    scripts = soup.find_all('script')
    has_show_trade_detail = False
    has_render_journey = False
    has_d3_select = False
    
    for script in scripts:
        if script.string:
            if 'showTradeDetail' in script.string:
                has_show_trade_detail = True
            if 'renderTradeJourney' in script.string:
                has_render_journey = True
            if 'd3.select' in script.string:
                has_d3_select = True
    
    print(f"\nJavaScript functions found:")
    print(f"  showTradeDetail: {'✅' if has_show_trade_detail else '❌'}")
    print(f"  renderTradeJourney: {'✅' if has_render_journey else '❌'}")
    print(f"  d3.select usage: {'✅' if has_d3_select else '❌'}")
    
    # Check if rows have onclick handlers
    print(f"\n" + "=" * 80)
    print("CHECKING TABLE STRUCTURE:")
    
    # Find the completed trades table
    tables = soup.find_all('table')
    for i, table in enumerate(tables):
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            if rows:
                first_row = rows[0]
                print(f"\nTable {i+1} - First row attributes:")
                print(f"  Classes: {first_row.get('class')}")
                print(f"  onclick: {first_row.get('onclick')}")
                print(f"  data-trade-id: {first_row.get('data-trade-id')}")
                
                # Check if row has clickable-row class
                if 'clickable-row' in str(first_row.get('class', [])):
                    print("  ✅ Has clickable-row class")
                else:
                    print("  ❌ Missing clickable-row class")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS:")
    
    if not d3_scripts:
        print("❌ PROBLEM: D3.js library not loaded")
        print("   FIX: Add D3.js CDN script tag to HTML")
    
    if not modal:
        print("❌ PROBLEM: Modal container missing from HTML")
        print("   FIX: Add modal HTML structure")
    
    if not has_show_trade_detail:
        print("❌ PROBLEM: showTradeDetail function not found")
        print("   FIX: Add JavaScript function to handle clicks")
    
    if not has_render_journey:
        print("❌ PROBLEM: renderTradeJourney function not found")
        print("   FIX: Add D3.js visualization function")
    
    if len(clickable_rows) == 0:
        print("❌ PROBLEM: Table rows don't have clickable-row class")
        print("   FIX: Add class='clickable-row' to <tr> elements")
    
    if all([d3_scripts, modal, has_show_trade_detail, has_render_journey, clickable_rows]):
        print("✅ All components present - issue is in JavaScript execution")
        print("   Check browser console for JavaScript errors")

else:
    print(f"❌ Failed to fetch dashboard: {response.status_code}")

"""
Check what's actually deployed on Railway
"""

import requests

url = "https://web-production-cd33.up.railway.app/automated-signals-dashboard"

print("Fetching live dashboard HTML from Railway...")
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    
    # Check for the new status indicator column
    if 'trade-status-indicator' in html:
        print("✅ Status indicator CSS found in live HTML")
    else:
        print("❌ Status indicator CSS NOT found in live HTML")
    
    # Check for the new MFE columns
    if 'MFE (BE=1)' in html:
        print("✅ MFE (BE=1) column header found")
    else:
        print("❌ MFE (BE=1) column header NOT found")
    
    if 'MFE (No BE)' in html:
        print("✅ MFE (No BE) column header found")
    else:
        print("❌ MFE (No BE) column header NOT found")
    
    # Check for the status indicator column header
    if '<th>●</th>' in html:
        print("✅ Status indicator column header (●) found")
    else:
        print("❌ Status indicator column header (●) NOT found")
    
    # Check for be_mfe usage
    if 'signal.be_mfe' in html:
        print("✅ be_mfe field usage found")
    else:
        print("❌ be_mfe field usage NOT found")
    
    # Check colspan
    if 'colspan="9"' in html:
        print("✅ Colspan updated to 9")
    elif 'colspan="7"' in html:
        print("❌ Colspan still 7 (should be 9)")
    
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("="*80)
    
    if all([
        'trade-status-indicator' in html,
        'MFE (BE=1)' in html,
        'MFE (No BE)' in html,
        '<th>●</th>' in html,
        'signal.be_mfe' in html,
        'colspan="9"' in html
    ]):
        print("✅ ALL CHANGES ARE DEPLOYED ON RAILWAY!")
        print("\nIf you're still seeing issues:")
        print("1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)")
        print("2. Clear browser cache")
        print("3. Try incognito/private window")
    else:
        print("❌ CHANGES NOT FULLY DEPLOYED - Railway may still be building")
        print("\nWait 2-3 minutes and check Railway dashboard for build status")
        
else:
    print(f"Error: {response.status_code}")

"""
Verify what's actually deployed on Railway
"""

import requests

url = "https://web-production-cd33.up.railway.app/automated-signals"

print("Checking live deployment at /automated-signals...")
response = requests.get(url)

if response.status_code == 200:
    html = response.text
    
    print("\n" + "="*80)
    print("DEPLOYMENT CHECK:")
    print("="*80)
    
    checks = {
        'trade-status-indicator': 'Status indicator CSS',
        'MFE (BE=1)': 'MFE (BE=1) column header',
        'MFE (No BE)': 'MFE (No BE) column header',
        '<th>●</th>': 'Status indicator column (●)',
        'signal.be_mfe': 'be_mfe field usage',
        'colspan="9"': 'Colspan=9 (updated)',
        'both-active': 'Green dot CSS class',
        'be-triggered': 'Blue dot CSS class'
    }
    
    results = {}
    for check, description in checks.items():
        found = check in html
        results[check] = found
        status = "✅" if found else "❌"
        print(f"{status} {description}")
    
    print("\n" + "="*80)
    
    if all(results.values()):
        print("✅ ALL CHANGES DEPLOYED SUCCESSFULLY!")
        print("\nIf you're still seeing red dots:")
        print("1. The red dot at the TOP is the WebSocket connection status (normal)")
        print("2. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
        print("3. Clear browser cache completely")
        print("4. Try incognito/private browsing mode")
    else:
        print("❌ SOME CHANGES MISSING - May need to redeploy")
        print("\nMissing changes:")
        for check, found in results.items():
            if not found:
                print(f"  - {checks[check]}")

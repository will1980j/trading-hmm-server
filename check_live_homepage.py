"""
Check what's ACTUALLY on the live Railway deployment
"""
import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

print("\n" + "=" * 70)
print("CHECKING LIVE RAILWAY DEPLOYMENT")
print("=" * 70)

try:
    response = requests.get(f'{BASE_URL}/homepage', timeout=10)
    
    if response.status_code == 200:
        content = response.text
        
        print("\n🔍 WHAT'S ACTUALLY ON RAILWAY RIGHT NOW:\n")
        
        # Check featured section
        if "V2 Automation System" in content:
            print("❌ PROBLEM: Featured section still shows 'V2 Automation System'")
            print("   Should be: 'Automated Signals Dashboard'")
        elif "Automated Signals Dashboard" in content:
            print("✅ Featured section correctly shows 'Automated Signals Dashboard'")
        else:
            print("⚠️  Featured section not found")
        
        # Check featured link
        if 'href="/signal-lab-v2"' in content and 'View V2 Automated Signals' in content:
            print("❌ PROBLEM: Featured button links to /signal-lab-v2")
            print("   Should link to: /automated-signals")
        elif 'href="/automated-signals"' in content and 'View Automated Signals Dashboard' in content:
            print("✅ Featured button correctly links to /automated-signals")
        else:
            print("⚠️  Featured button not found")
        
        # Check navigation
        if 'href="/signal-lab-v2"' in content and '🤖 V2 Auto' in content:
            print("❌ PROBLEM: Navigation has '🤖 V2 Auto' link")
            print("   Should be: '📡 Automated Signals'")
        elif 'href="/automated-signals"' in content and 'Automated Signals' in content:
            print("✅ Navigation correctly has 'Automated Signals' link")
        else:
            print("⚠️  Navigation link not found")
        
        # Check tool cards
        v2_card_count = content.count('Signal Lab V2')
        auto_card_count = content.count('Automated Signals</h3>')
        
        print(f"\n📊 Card Count:")
        print(f"   'Signal Lab V2' cards: {v2_card_count}")
        print(f"   'Automated Signals' cards: {auto_card_count}")
        
        if v2_card_count > 0:
            print("❌ PROBLEM: Still has Signal Lab V2 card(s)")
        if auto_card_count > 0:
            print("✅ Has Automated Signals card(s)")
        
        print("\n" + "=" * 70)
        print("DIAGNOSIS:")
        print("=" * 70)
        
        has_v2 = ("V2 Automation System" in content or 
                  'href="/signal-lab-v2"' in content or 
                  v2_card_count > 0)
        
        if has_v2:
            print("\n❌ THE CHANGES HAVE NOT BEEN DEPLOYED TO RAILWAY YET")
            print("\n📋 What you need to do:")
            print("   1. Open GitHub Desktop")
            print("   2. You should see 'homepage.html' as modified")
            print("   3. Commit the changes")
            print("   4. Push to main branch")
            print("   5. Wait 2-3 minutes for Railway to deploy")
            print("   6. Hard refresh your browser (Ctrl+F5)")
        else:
            print("\n✅ Changes appear to be deployed!")
            print("   Try hard refresh (Ctrl+F5) in your browser")
        
    else:
        print(f"\n❌ Homepage returned status code: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error checking homepage: {e}")

print("\n" + "=" * 70)

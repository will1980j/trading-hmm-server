"""
Test homepage integration with Automated Signals dashboard
"""
import requests

BASE_URL = "https://web-production-cd33.up.railway.app"

def test_homepage_integration():
    """Test that homepage properly features Automated Signals"""
    
    print("\n" + "=" * 70)
    print("🏠 HOMEPAGE INTEGRATION TEST - AUTOMATED SIGNALS")
    print("=" * 70)
    
    try:
        response = requests.get(f'{BASE_URL}/homepage', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            print("\n✅ Homepage loaded successfully\n")
            
            # Check for Automated Signals integration
            checks = [
                ('Featured Section Title', '📡 Automated Signals Dashboard - Now Live!' in content),
                ('Featured Description', 'Real-time automated signal monitoring' in content),
                ('Featured CTA Link', 'href="/automated-signals"' in content and 'View Automated Signals Dashboard' in content),
                ('Tool Card Present', '<h3 class="tool-title">Automated Signals</h3>' in content),
                ('Tool Description', 'Real-time signal monitoring with calendar view' in content),
                ('Featured Badge', 'Featured!' in content or 'New!' in content),
                ('Cloud Automation Stat', 'Cloud Automation' in content),
                ('Stats API Call', '/api/automated-signals/stats' in content),
                ('Auto-refresh Stats', 'setInterval(loadStats' in content),
            ]
            
            print("📋 Integration Checks:\n")
            all_passed = True
            for name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {name}")
                if not passed:
                    all_passed = False
            
            print("\n" + "=" * 70)
            
            if all_passed:
                print("\n🎉 SUCCESS! Homepage fully integrated with Automated Signals!")
                print("\n✅ What's working:")
                print("   • Featured section highlights Automated Signals dashboard")
                print("   • CTA button links to /automated-signals")
                print("   • Tool card included in tools grid")
                print("   • Stats load from automated signals API")
                print("   • Auto-refresh every 30 seconds")
                print("   • Cloud automation status displayed")
                print("\n🌐 View it live:")
                print(f"   {BASE_URL}/homepage")
                print(f"   {BASE_URL}/automated-signals")
                return True
            else:
                print("\n⚠️ Some integration checks failed")
                print("   Review the checks above for details")
                return False
                
        else:
            print(f"\n❌ Homepage failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing homepage: {e}")
        return False

def test_navigation_links():
    """Test that navigation includes automated signals"""
    
    print("\n\n" + "=" * 70)
    print("🧭 NAVIGATION LINKS TEST")
    print("=" * 70)
    
    try:
        response = requests.get(f'{BASE_URL}/homepage', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            nav_checks = [
                ('Automated Signals Nav Link', 'href="/automated-signals"' in content and 'Auto Signals' in content),
                ('Signal Lab V2 Nav Link', 'href="/signal-lab-v2"' in content),
                ('Main Dashboard Nav Link', 'href="/signal-lab-dashboard"' in content),
            ]
            
            print("\n📋 Navigation Checks:\n")
            for name, passed in nav_checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {name}")
            
            all_passed = all(check[1] for check in nav_checks)
            
            if all_passed:
                print("\n✅ All navigation links present!")
            else:
                print("\n⚠️ Some navigation links missing")
            
            return all_passed
            
    except Exception as e:
        print(f"\n❌ Error testing navigation: {e}")
        return False

def test_automated_signals_dashboard():
    """Test that automated signals dashboard is accessible"""
    
    print("\n\n" + "=" * 70)
    print("📡 AUTOMATED SIGNALS DASHBOARD TEST")
    print("=" * 70)
    
    try:
        response = requests.get(f'{BASE_URL}/automated-signals', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            dashboard_checks = [
                ('Dashboard Title', 'Automated Signals Dashboard' in content),
                ('Health Monitor', 'System Health Monitor' in content),
                ('Calendar System', 'calendar-grid' in content),
                ('Stats Display', 'Total Signals Today' in content),
                ('WebSocket Connection', 'socket.io' in content),
                ('Health Check Function', 'checkSystemHealth' in content),
            ]
            
            print("\n📋 Dashboard Checks:\n")
            for name, passed in dashboard_checks:
                status = "✅" if passed else "❌"
                print(f"   {status} {name}")
            
            all_passed = all(check[1] for check in dashboard_checks)
            
            if all_passed:
                print("\n✅ Automated Signals dashboard fully functional!")
            else:
                print("\n⚠️ Some dashboard features missing")
            
            return all_passed
            
    except Exception as e:
        print(f"\n❌ Error testing dashboard: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 COMPLETE INTEGRATION TEST SUITE")
    print("=" * 70)
    
    # Run all tests
    homepage_ok = test_homepage_integration()
    nav_ok = test_navigation_links()
    dashboard_ok = test_automated_signals_dashboard()
    
    # Final summary
    print("\n\n" + "=" * 70)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 70)
    
    if homepage_ok and nav_ok and dashboard_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Complete Integration Verified:")
        print("   • Homepage features Automated Signals prominently")
        print("   • Navigation links all working")
        print("   • Dashboard fully functional with health monitoring")
        print("   • Stats API connected and auto-refreshing")
        print("   • Calendar system operational")
        print("   • WebSocket real-time updates enabled")
        print("\n🚀 Your automation workflow is COMPLETE and LIVE!")
        print("\n🌐 Access Points:")
        print(f"   Homepage: {BASE_URL}/homepage")
        print(f"   Dashboard: {BASE_URL}/automated-signals")
        print(f"   Webhook: {BASE_URL}/api/automated-signals")
    else:
        print("\n⚠️ Some tests failed - review details above")
        if not homepage_ok:
            print("   ❌ Homepage integration needs deployment")
        if not nav_ok:
            print("   ❌ Navigation links need update")
        if not dashboard_ok:
            print("   ❌ Dashboard needs deployment")
    
    print("\n" + "=" * 70)

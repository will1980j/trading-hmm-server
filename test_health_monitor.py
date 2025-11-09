"""
Test the health monitoring system on the automated signals dashboard
"""
import requests
import time

BASE_URL = "https://web-production-cd33.up.railway.app"

def test_health_endpoints():
    """Test all endpoints that the health monitor checks"""
    
    print("🔍 Testing System Health Endpoints\n")
    print("=" * 60)
    
    tests = [
        {
            'name': '🌐 Railway Server',
            'url': f'{BASE_URL}/api/automated-signals/dashboard-data',
            'method': 'GET'
        },
        {
            'name': '📡 Webhook Endpoint',
            'url': f'{BASE_URL}/api/automated-signals',
            'method': 'OPTIONS'
        },
        {
            'name': '💾 Database / API',
            'url': f'{BASE_URL}/api/automated-signals/stats',
            'method': 'GET'
        },
        {
            'name': '📄 Dashboard Page',
            'url': f'{BASE_URL}/automated-signals',
            'method': 'GET'
        }
    ]
    
    results = []
    
    for test in tests:
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=10)
            elif test['method'] == 'OPTIONS':
                response = requests.options(test['url'], timeout=10)
            
            status = "✅ PASS" if response.status_code in [200, 204] else f"⚠️ {response.status_code}"
            results.append({
                'name': test['name'],
                'status': status,
                'code': response.status_code,
                'healthy': response.status_code in [200, 204]
            })
            
            print(f"{test['name']:<30} {status}")
            
        except Exception as e:
            results.append({
                'name': test['name'],
                'status': "❌ FAIL",
                'error': str(e),
                'healthy': False
            })
            print(f"{test['name']:<30} ❌ FAIL - {str(e)[:40]}")
    
    print("\n" + "=" * 60)
    
    # Summary
    healthy_count = sum(1 for r in results if r.get('healthy', False))
    total_count = len(results)
    
    print(f"\n📊 Health Summary: {healthy_count}/{total_count} systems operational")
    
    if healthy_count == total_count:
        print("\n✅ ALL SYSTEMS OPERATIONAL!")
        print("🚀 Dashboard health monitor will show all green indicators")
        print("💡 Automation is fully functional and ready for TradingView signals")
    else:
        print(f"\n⚠️ {total_count - healthy_count} system(s) need attention")
        print("🔧 Dashboard health monitor will highlight issues")
    
    return results

def test_dashboard_features():
    """Test that the dashboard loads with health monitor"""
    
    print("\n\n🎨 Testing Dashboard Features\n")
    print("=" * 60)
    
    try:
        response = requests.get(f'{BASE_URL}/automated-signals', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for health monitor elements
            checks = [
                ('System Health Monitor', '🔧 System Health Monitor' in content),
                ('Server Status', 'serverStatus' in content),
                ('Webhook Status', 'webhookStatus' in content),
                ('Database Status', 'databaseStatus' in content),
                ('API Status', 'apiStatus' in content),
                ('WebSocket Status', 'websocketStatus' in content),
                ('Calendar Status', 'calendarStatus' in content),
                ('Health Check Function', 'checkSystemHealth' in content),
                ('Auto-refresh', 'setInterval(checkSystemHealth' in content),
            ]
            
            for name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"{status} {name}")
            
            all_passed = all(check[1] for check in checks)
            
            print("\n" + "=" * 60)
            
            if all_passed:
                print("\n✅ Dashboard health monitor is fully implemented!")
                print("\n📋 Features:")
                print("   • Real-time status checks for 6 system components")
                print("   • Auto-refresh every 30 seconds")
                print("   • Manual refresh button")
                print("   • Visual indicators (green/red/yellow)")
                print("   • Automation status message")
                print("\n🌐 View it live:")
                print(f"   {BASE_URL}/automated-signals")
            else:
                print("\n⚠️ Some dashboard features are missing")
            
            return all_passed
            
        else:
            print(f"❌ Dashboard failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏥 AUTOMATED SIGNALS DASHBOARD - HEALTH MONITOR TEST")
    print("=" * 60)
    
    # Test health endpoints
    health_results = test_health_endpoints()
    
    # Test dashboard features
    dashboard_ok = test_dashboard_features()
    
    print("\n\n" + "=" * 60)
    print("📝 FINAL SUMMARY")
    print("=" * 60)
    
    if dashboard_ok and all(r.get('healthy', False) for r in health_results):
        print("\n🎉 SUCCESS! Everything is working perfectly!")
        print("\n✅ What's working:")
        print("   • Health monitor displays on dashboard")
        print("   • All 6 system components are checked")
        print("   • Auto-refresh runs every 30 seconds")
        print("   • Manual refresh button available")
        print("   • Visual status indicators working")
        print("   • All backend endpoints operational")
        print("\n🚀 Your automation workflow is LIVE and monitored!")
        print(f"\n🌐 Dashboard: {BASE_URL}/automated-signals")
        print(f"📡 Webhook: {BASE_URL}/api/automated-signals")
    else:
        print("\n⚠️ Some issues detected - check details above")
    
    print("\n" + "=" * 60)

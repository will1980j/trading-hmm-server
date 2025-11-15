"""
Test Signal Integrity Verification System
"""

import requests
import json

def test_integrity_endpoint():
    """Test the signal integrity verification endpoint"""
    print("🔍 Testing Signal Integrity Verification System\n")
    
    # Test direct integrity endpoint
    print("1. Testing /api/automated-signals/verify-integrity...")
    try:
        response = requests.get('https://web-production-cd33.up.railway.app/api/automated-signals/verify-integrity')
        data = response.json()
        
        print(f"   Status: {data.get('status')}")
        print(f"   Signals Checked: {data.get('signals_checked')}")
        print(f"   Errors: {len(data.get('errors', []))}")
        print(f"   Warnings: {len(data.get('warnings', []))}")
        
        if data.get('errors'):
            print("\n   ❌ ERRORS FOUND:")
            for error in data['errors'][:5]:
                print(f"      • {error}")
        
        if data.get('warnings'):
            print("\n   ⚠️  WARNINGS:")
            for warning in data['warnings'][:5]:
                print(f"      • {warning}")
        
        if data.get('details'):
            print("\n   📋 SIGNAL DETAILS:")
            for signal in data['details']:
                print(f"\n      Signal: {signal['signal_id']}")
                print(f"      Status: {signal['status']}")
                print(f"      Checks: {len(signal['checks'])}")
                
                if signal['errors']:
                    print(f"      Errors: {signal['errors']}")
                if signal['warnings']:
                    print(f"      Warnings: {signal['warnings']}")
                
                # Show check details
                for check in signal['checks']:
                    status_icon = "✅" if check['status'] == "PASS" else "⚠️" if check['status'] == "WARNING" else "❌"
                    print(f"         {status_icon} {check['name']}: {check['details']}")
        
        print("\n✅ Integrity endpoint test complete\n")
        
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test system health endpoint (includes integrity)
    print("2. Testing /api/system-health (includes integrity)...")
    try:
        response = requests.get('https://web-production-cd33.up.railway.app/api/system-health')
        data = response.json()
        
        print(f"   Overall Status: {data.get('overall_status')}")
        
        if 'integrity' in data.get('components', {}):
            integrity = data['components']['integrity']
            print(f"\n   🔍 INTEGRITY COMPONENT:")
            print(f"      Status: {integrity.get('status')}")
            print(f"      Signals Verified: {integrity.get('signals_verified')}")
            print(f"      Errors Found: {integrity.get('errors_found')}")
            print(f"      Warnings Found: {integrity.get('warnings_found')}")
            
            if integrity.get('message'):
                print(f"      Message: {integrity['message']}")
            
            if integrity.get('issues'):
                print(f"      Issues:")
                for issue in integrity['issues']:
                    print(f"         • {issue}")
        
        print("\n✅ System health test complete\n")
        
    except Exception as e:
        print(f"   ❌ Error: {e}\n")

if __name__ == "__main__":
    test_integrity_endpoint()

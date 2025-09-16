#!/usr/bin/env python3
"""
Fix Signal Lab Auto-Population Issue
This script identifies and fixes why signals aren't populating Signal Lab
"""

import requests
import json

RAILWAY_URL = "https://web-production-cd33.up.railway.app"

def test_contract_detection():
    """Test what contract is currently active"""
    
    print("Testing Contract Detection")
    print("="*30)
    
    # Test different contract formats
    test_contracts = [
        "NQ1!",
        "NQZ24", 
        "NQU24",
        "NQH25"
    ]
    
    for contract in test_contracts:
        test_signal = {
            "bias": "Bullish",
            "price": 20150.25,
            "strength": 85,
            "symbol": contract,
            "htf_aligned": True,
            "timeframe": "1m"
        }
        
        print(f"\\nTesting contract: {contract}")
        
        try:
            response = requests.post(
                f"{RAILWAY_URL}/api/live-signals",
                json=test_signal,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', '')
                
                # Check for auto-population indicators
                if 'auto-populated' in message.lower() or 'signal lab' in message.lower():
                    print(f"  SUCCESS: {contract} triggered Signal Lab auto-population!")
                    return contract
                else:
                    print(f"  No auto-population for {contract}")
                    
                # Check for contract rollover messages
                if 'rollover' in message.lower():
                    print(f"  Contract rollover detected for {contract}")
                elif 'normalized' in message.lower():
                    print(f"  Symbol normalized for {contract}")
            else:
                print(f"  Error: {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    return None

def send_debug_signal():
    """Send a signal with debug info to see what's happening"""
    
    print("\\nSending Debug Signal")
    print("="*25)
    
    # Use the most likely contract format
    debug_signal = {
        "bias": "Bullish",
        "price": 20155.75,
        "strength": 90,
        "symbol": "NQ1!",
        "htf_aligned": True,
        "htf_status": "ALIGNED",
        "timeframe": "1m",
        "signal_type": "DEBUG_TEST",
        "debug": True
    }
    
    print(f"Debug signal: {json.dumps(debug_signal, indent=2)}")
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals",
            json=debug_signal,
            timeout=10
        )
        
        print(f"\\nResponse: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            # Print all response keys to see what's available
            print("\\nFull response keys:")
            for key, value in data.items():
                if key != 'message':
                    print(f"  {key}: {value}")
                    
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def check_server_logs():
    """Instructions for checking server logs"""
    
    print("\\n" + "="*50)
    print("DEBUGGING STEPS")
    print("="*50)
    
    print("\\n1. Check Railway Logs:")
    print("   - Go to Railway dashboard")
    print("   - Click on your deployment")
    print("   - Check 'Logs' tab for auto-population messages")
    print("   - Look for: 'Auto-populated Signal Lab' or 'Skipped Signal Lab'")
    
    print("\\n2. Common Issues:")
    print("   - Active NQ contract is not NQ1! (could be NQZ24, etc.)")
    print("   - Contract manager not finding active contract")
    print("   - Database connection issues")
    print("   - HTF alignment check failing")
    
    print("\\n3. Quick Fix:")
    print("   - Update TradingView alert to send specific contract")
    print("   - Or ensure contract manager is working properly")
    
    print("\\n4. Test URLs:")
    print(f"   - Health: {RAILWAY_URL}/health")
    print(f"   - Webhook: {RAILWAY_URL}/api/live-signals")

if __name__ == "__main__":
    print("Signal Lab Auto-Population Debug")
    print("="*35)
    
    # Test different contracts
    working_contract = test_contract_detection()
    
    if working_contract:
        print(f"\\nFOUND WORKING CONTRACT: {working_contract}")
        print("Update your TradingView alert to use this contract symbol")
    else:
        print("\\nNo contract triggered auto-population")
        print("The issue is likely in the auto-population logic")
    
    # Send debug signal
    send_debug_signal()
    
    # Show debugging steps
    check_server_logs()
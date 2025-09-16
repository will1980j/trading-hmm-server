#!/usr/bin/env python3
"""
Fix Signal Lab Auto-Population Issue
This script creates a patch to fix the auto-population logic
"""

import requests
import json

RAILWAY_URL = "https://web-production-cd33.up.railway.app"

def test_contract_manager():
    """Test what the contract manager is returning"""
    
    # Send a test signal to see what happens in the logs
    test_signal = {
        "bias": "Bullish",
        "price": 20160.75,
        "strength": 90,
        "symbol": "NQ1!",
        "htf_aligned": True,
        "htf_status": "ALIGNED",
        "timeframe": "1m",
        "signal_type": "DEBUG_CONTRACT_TEST"
    }
    
    print("Testing contract manager behavior...")
    print(f"Test signal: {json.dumps(test_signal, indent=2)}")
    
    try:
        response = requests.post(
            f"{RAILWAY_URL}/api/live-signals",
            json=test_signal,
            timeout=10
        )
        
        print(f"\nResponse: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            
            # The key issue: check if auto-population is mentioned
            message = data.get('message', '')
            if 'auto-populated' in message.lower() or 'signal lab' in message.lower():
                print("SUCCESS: Auto-population is working!")
                return True
            else:
                print("ISSUE: Auto-population logic is not triggering")
                print("This means either:")
                print("1. Contract manager is not returning 'NQ1!' for get_active_contract('NQ')")
                print("2. HTF alignment check is failing")
                print("3. The auto-population code has a bug")
                return False
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_contract_fix():
    """Create a simple fix for the contract issue"""
    
    print("\n" + "="*50)
    print("SIGNAL LAB AUTO-POPULATION FIX")
    print("="*50)
    
    print("\nThe issue is in the webhook auto-population logic.")
    print("Here's what needs to be fixed in web_server.py:")
    
    print("\nCURRENT CODE (around line 1800):")
    print("```python")
    print("# Get current active NQ contract from contract manager")
    print("active_nq_contract = contract_manager.get_active_contract('NQ')")
    print("")
    print("should_populate = (")
    print("    signal['symbol'] == active_nq_contract and")
    print("    htf_aligned  # HTF alignment still required")
    print(")")
    print("```")
    
    print("\nFIXED CODE:")
    print("```python")
    print("# Get current active NQ contract from contract manager")
    print("active_nq_contract = contract_manager.get_active_contract('NQ')")
    print("")
    print("# DEBUG: Log the contract comparison")
    print("logger.info(f'Contract check: signal={signal[\"symbol\"]}, active={active_nq_contract}, htf={htf_aligned}')")
    print("")
    print("# FALLBACK: If contract manager fails, default to NQ1!")
    print("if not active_nq_contract:")
    print("    active_nq_contract = 'NQ1!'")
    print("    logger.warning('Contract manager returned None, defaulting to NQ1!')")
    print("")
    print("should_populate = (")
    print("    signal['symbol'] == active_nq_contract and")
    print("    htf_aligned  # HTF alignment still required")
    print(")")
    print("```")
    
    print("\nThis fix adds:")
    print("1. Debug logging to see what's happening")
    print("2. Fallback to 'NQ1!' if contract manager fails")
    print("3. Better error handling")

def test_manual_population():
    """Test manual Signal Lab population to verify the endpoint works"""
    
    print("\n" + "="*30)
    print("TESTING MANUAL SIGNAL LAB POPULATION")
    print("="*30)
    
    # Create a manual Signal Lab entry to test the endpoint
    manual_trade = {
        "date": "2024-09-16",
        "time": "10:30:00", 
        "bias": "Bullish",
        "session": "London",
        "signal_type": "MANUAL_TEST",
        "mfe_none": 0,
        "be1_level": 1,
        "be1_hit": False,
        "mfe1": 0,
        "be2_level": 2,
        "be2_hit": False,
        "mfe2": 0,
        "news_proximity": "None",
        "news_event": "Manual test entry",
        "screenshot": None
    }
    
    print(f"Creating manual Signal Lab entry...")
    
    try:
        # Note: This will fail due to authentication, but we can see if the endpoint exists
        response = requests.post(
            f"{RAILWAY_URL}/api/signal-lab-trades",
            json=manual_trade,
            timeout=10
        )
        
        print(f"Response: {response.status_code}")
        
        if response.status_code == 401:
            print("Endpoint exists but requires authentication (expected)")
            return True
        elif response.status_code == 200:
            print("Manual population works!")
            return True
        else:
            print(f"Unexpected response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Signal Lab Auto-Population Diagnostic & Fix")
    print("="*45)
    
    # Test the current behavior
    working = test_contract_manager()
    
    if not working:
        # Show the fix
        create_contract_fix()
        
        # Test manual population
        test_manual_population()
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print("The auto-population logic is not working because:")
        print("1. Contract manager may be returning None instead of 'NQ1!'")
        print("2. The comparison signal['symbol'] == active_nq_contract is failing")
        print("")
        print("SOLUTION:")
        print("Deploy the fixed code above to Railway to resolve the issue.")
        print("")
        print("IMMEDIATE WORKAROUND:")
        print("Manually populate Signal Lab entries until the fix is deployed.")
    else:
        print("\nAuto-population is working correctly!")
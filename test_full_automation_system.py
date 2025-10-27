#!/usr/bin/env python3
"""
TEST FULL AUTOMATION SYSTEM
Tests the complete automation pipeline
"""

import requests
import json
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://web-production-cd33.up.railway.app"

def test_signal_detection():
    """Test signal detection webhook"""
    logging.info("Testing signal detection webhook...")
    
    # Sample signal data (matches TradingView format)
    signal_data = {
        "signal_id": f"test_signal_{int(time.time())}",
        "signal_type": "Bullish",
        "timestamp": int(time.time() * 1000),
        "session": "NY_AM",
        "signal_candle": {
            "open": 4150.25,
            "high": 4152.75,
            "low": 4149.50,
            "close": 4151.80,
            "volume": 1250000
        },
        "previous_candle": {
            "open": 4148.90,
            "high": 4150.10,
            "low": 4147.25,
            "close": 4149.75
        },
        "market_context": {
            "atr": 12.5,
            "volatility": 0.025,
            "signal_strength": 85.0
        },
        "fvg_data": {
            "bias": "Bullish",
            "htf_status": "1H:Bullish 15M:Bullish 5M:Bullish",
            "signal_type": "FVG",
            "htf_aligned": True,
            "engulfing": {
                "bullish": True,
                "bearish": False,
                "sweep_bullish": False,
                "sweep_bearish": False
            }
        },
        "methodology_data": {
            "requires_confirmation": True,
            "stop_loss_buffer": 25,
            "automation_stage": "SIGNAL_DETECTED"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/live-signals-v2",
            json=signal_data,
            timeout=10
        )
        
        logging.info(f"Signal detection response: {response.status_code}")
        if response.status_code == 200:
            logging.info(f"Response: {response.json()}")
            return True
        else:
            logging.error(f"Error: {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Signal detection test failed: {e}")
        return False

def test_automation_status():
    """Test automation status endpoint"""
    logging.info("Testing automation status endpoint...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/automation-status",
            timeout=10
        )
        
        logging.info(f"Automation status response: {response.status_code}")
        if response.status_code == 200:
            status_data = response.json()
            logging.info(f"Automation enabled: {status_data.get('automation_enabled')}")
            logging.info(f"Active trades: {status_data.get('active_trades')}")
            return True
        else:
            logging.error(f"Status error: {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Automation status test failed: {e}")
        return False

def test_confirmation_webhook():
    """Test confirmation detection webhook"""
    logging.info("Testing confirmation webhook...")
    
    confirmation_data = {
        "signal_id": f"test_signal_{int(time.time())}",
        "confirmation_type": "Bullish",
        "timestamp": int(time.time() * 1000),
        "session": "NY_AM",
        "confirmation_candle": {
            "open": 4152.00,
            "high": 4154.25,
            "low": 4151.75,
            "close": 4153.50
        },
        "entry_price": 4153.75,
        "stop_loss_price": 4128.50,
        "risk_distance": 25.25,
        "automation_stage": "CONFIRMATION_DETECTED"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/confirmations",
            json=confirmation_data,
            timeout=10
        )
        
        logging.info(f"Confirmation response: {response.status_code}")
        if response.status_code in [200, 404]:  # 404 is expected if signal doesn't exist
            logging.info(f"Response: {response.text}")
            return True
        else:
            logging.error(f"Error: {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Confirmation test failed: {e}")
        return False

def test_all_endpoints():
    """Test all automation endpoints"""
    logging.info("Testing all automation endpoints...")
    
    endpoints = [
        ("/api/live-signals-v2", "POST"),
        ("/api/confirmations", "POST"),
        ("/api/trade-activation", "POST"),
        ("/api/mfe-updates", "POST"),
        ("/api/trade-resolution", "POST"),
        ("/api/signal-cancellation", "POST"),
        ("/api/automation-status", "GET")
    ]
    
    results = {}
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=10)
            
            results[endpoint] = {
                "status_code": response.status_code,
                "accessible": response.status_code != 404
            }
            
            logging.info(f"{endpoint} ({method}): {response.status_code}")
            
        except Exception as e:
            results[endpoint] = {
                "status_code": "ERROR",
                "accessible": False,
                "error": str(e)
            }
            logging.error(f"{endpoint} failed: {e}")
    
    return results

def main():
    """Main test function"""
    logging.info("Starting Full Automation System Tests...")
    
    test_results = {
        "signal_detection": False,
        "automation_status": False,
        "confirmation_webhook": False,
        "all_endpoints": {}
    }
    
    # Test 1: Signal Detection
    test_results["signal_detection"] = test_signal_detection()
    
    # Test 2: Automation Status
    test_results["automation_status"] = test_automation_status()
    
    # Test 3: Confirmation Webhook
    test_results["confirmation_webhook"] = test_confirmation_webhook()
    
    # Test 4: All Endpoints
    test_results["all_endpoints"] = test_all_endpoints()
    
    # Summary
    logging.info("\n" + "="*50)
    logging.info("FULL AUTOMATION SYSTEM TEST RESULTS")
    logging.info("="*50)
    
    passed_tests = sum([
        test_results["signal_detection"],
        test_results["automation_status"],
        test_results["confirmation_webhook"]
    ])
    
    logging.info(f"Core Tests Passed: {passed_tests}/3")
    
    accessible_endpoints = sum([
        1 for endpoint_data in test_results["all_endpoints"].values()
        if endpoint_data.get("accessible", False)
    ])
    
    logging.info(f"Accessible Endpoints: {accessible_endpoints}/7")
    
    if passed_tests >= 2 and accessible_endpoints >= 5:
        logging.info("✅ AUTOMATION SYSTEM IS READY!")
        logging.info("\nNext Steps:")
        logging.info("1. Upload TradingView indicator")
        logging.info("2. Configure webhook URLs")
        logging.info("3. Enable full automation")
        logging.info("4. Monitor live signals")
        return True
    else:
        logging.error("❌ AUTOMATION SYSTEM NEEDS ATTENTION")
        logging.error("Check the errors above and fix issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
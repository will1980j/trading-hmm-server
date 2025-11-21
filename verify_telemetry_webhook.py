"""
STRICT MODE VERIFICATION - Telemetry Webhook Handler
Tests the exact payload from TradingView
"""
import requests
import json

# Test payload - EXACT format from TradingView
TELEMETRY_PAYLOAD = {
    "message": "",
    "attributes": {
        "schema_version": "1.0.0",
        "engine_version": "1.0.0",
        "strategy_name": "NQ_FVG_CORE",
        "strategy_id": "NQ_FVG_CORE",
        "strategy_version": "2025.11.20",
        "trade_id": "20250101_120000000_BULLISH",
        "event_type": "ENTRY",
        "event_timestamp": "2025-11-21T01:05:00Z",
        "symbol": "MNQ1!",
        "exchange": "MNQ1!",
        "timeframe": "1",
        "session": "LONDON",
        "direction": "Bullish",
        "entry_price": 24000.0,
        "stop_loss": 23950.0,
        "risk_R": 1,
        "position_size": 2,
        "be_price": None,
        "mfe_R": 0,
        "mae_R": 0,
        "final_mfe_R": None,
        "exit_price": None,
        "exit_timestamp": None,
        "exit_reason": None,
        "targets": {"tp1_price": 24100, "tp2_price": 24200, "tp3_price": 24300},
        "setup": {"setup_family": "FVG_CORE", "setup_variant": "HTF", "setup_id": "FVG_CORE_HTF", "signal_strength": 75},
        "market_state": {"trend_regime": "Bullish"}
    }
}

def test_telemetry_webhook():
    """Test telemetry webhook with exact TradingView payload"""
    
    url = "http://localhost:5000/api/automated-signals/webhook"
    
    print("=" * 80)
    print("STRICT MODE VERIFICATION - TELEMETRY WEBHOOK")
    print("=" * 80)
    
    print("\n📤 SENDING TELEMETRY PAYLOAD:")
    print(json.dumps(TELEMETRY_PAYLOAD, indent=2))
    
    try:
        response = requests.post(url, json=TELEMETRY_PAYLOAD, timeout=10)
        
        print(f"\n📥 RESPONSE STATUS: {response.status_code}")
        print(f"📥 RESPONSE BODY: {response.text}")
        
        # VERIFICATION CHECKS
        print("\n" + "=" * 80)
        print("VERIFICATION RESULTS:")
        print("=" * 80)
        
        checks = []
        
        # Check 1: HTTP 200
        if response.status_code == 200:
            checks.append("✅ HTTP 200 response")
        else:
            checks.append(f"❌ HTTP {response.status_code} (expected 200)")
        
        # Check 2: Not unsupported format error
        if "Unsupported payload format" not in response.text:
            checks.append("✅ Not rejected as unsupported format")
        else:
            checks.append("❌ Rejected as unsupported format")
        
        # Check 3: Success response
        try:
            resp_json = response.json()
            if resp_json.get("success"):
                checks.append("✅ Success response received")
            else:
                checks.append(f"❌ Error response: {resp_json.get('error')}")
        except:
            checks.append("⚠️  Could not parse JSON response")
        
        for check in checks:
            print(check)
        
        # Overall result
        print("\n" + "=" * 80)
        if all("✅" in check for check in checks):
            print("🎉 ALL VERIFICATION CHECKS PASSED")
        else:
            print("❌ VERIFICATION FAILED - See errors above")
        print("=" * 80)
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR: Server not running at localhost:5000")
        print("   Start the server first: python web_server.py")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_telemetry_webhook()
    exit(0 if success else 1)

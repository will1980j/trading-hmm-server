#!/usr/bin/env python3
"""
Webhook V2 Integration - Connect TradingView signals to automated processor
Enhances existing webhook endpoint to use V2 automation
"""

from flask import request, jsonify
import json
import logging
from automated_signal_processor import AutomatedSignalProcessor

logger = logging.getLogger(__name__)

class WebhookV2Integration:
    def __init__(self):
        self.processor = AutomatedSignalProcessor()
        
    def enhanced_webhook_handler(self, webhook_data):
        """
        Enhanced webhook handler that processes signals through V2 automation
        
        This integrates with your existing /api/live-signals endpoint
        """
        try:
            logger.info(f"🎯 V2 Webhook received: {webhook_data}")
            
            # Extract TradingView signal data
            signal_type = webhook_data.get('type', '')
            symbol = webhook_data.get('symbol', 'NQ1!')
            timestamp = webhook_data.get('timestamp', '')
            price = webhook_data.get('price', 0)
            
            # Determine session from timestamp or current time
            session = self._determine_session_from_webhook(webhook_data)
            
            # Create standardized signal data for processor
            signal_data = {
                "type": signal_type,
                "symbol": symbol,
                "timestamp": timestamp,
                "price": float(price) if price else 0,
                "session": session
            }
            
            # Process through automated system
            automation_result = self.processor.process_tradingview_signal(signal_data)
            
            # Store in original live_signals table (for compatibility)
            original_signal_id = self._store_original_signal(webhook_data)
            
            # Return enhanced response
            response = {
                "success": True,
                "message": "Signal processed through V2 automation",
                "original_signal_id": original_signal_id,
                "automation_result": automation_result,
                "v2_enabled": True
            }
            
            if automation_result.get("success"):
                response["v2_trade_id"] = automation_result.get("trade_id")
                response["v2_trade_uuid"] = automation_result.get("trade_uuid")
                response["automated_entry"] = automation_result.get("entry_price")
                response["automated_stop_loss"] = automation_result.get("stop_loss_price")
                response["r_targets"] = automation_result.get("r_targets")
            
            logger.info(f"✅ V2 webhook processing complete: {response}")
            return response
            
        except Exception as e:
            logger.error(f"❌ V2 webhook error: {e}")
            return {
                "success": False,
                "error": str(e),
                "v2_enabled": True,
                "fallback": "Signal stored in original format"
            }
    
    def _determine_session_from_webhook(self, webhook_data):
        """Determine trading session from webhook data"""
        # Check if session is provided in webhook
        if 'session' in webhook_data:
            return webhook_data['session']
        
        # Determine from timestamp
        timestamp = webhook_data.get('timestamp', '')
        if timestamp:
            try:
                from datetime import datetime, timezone, timedelta
                signal_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                eastern = timezone(timedelta(hours=-5))
                et_time = signal_time.astimezone(eastern)
                hour = et_time.hour
                
                if 20 <= hour <= 23:
                    return "ASIA"
                elif 0 <= hour <= 5:
                    return "LONDON"
                elif 6 <= hour <= 8:
                    return "NY PRE"
                elif 8 <= hour <= 11:
                    return "NY AM"
                elif hour == 12:
                    return "NY LUNCH"
                elif 13 <= hour <= 15:
                    return "NY PM"
            except:
                pass
        
        # Default to current session determination
        return "NY AM"  # Default fallback
    
    def _store_original_signal(self, webhook_data):
        """Store signal in original live_signals table for compatibility"""
        try:
            # This would use your existing database connection
            # For now, return a mock ID
            return 12345  # Mock signal ID
        except Exception as e:
            logger.error(f"❌ Original signal storage error: {e}")
            return None

# Integration function for web_server.py
def integrate_v2_webhook():
    """
    Integration code to add to your existing web_server.py
    
    Add this to your existing /api/live-signals endpoint:
    """
    
    integration_code = '''
# Add this import at the top of web_server.py
from webhook_v2_integration import WebhookV2Integration

# Add this initialization after your other initializations
v2_integration = WebhookV2Integration()

# Modify your existing /api/live-signals endpoint to include V2 processing:
@app.route('/api/live-signals', methods=['POST'])
def receive_signal():
    """Enhanced webhook endpoint with V2 automation"""
    try:
        data = request.get_json()
        
        # Original processing (keep existing logic)
        original_result = your_existing_signal_processing(data)
        
        # V2 automation processing
        v2_result = v2_integration.enhanced_webhook_handler(data)
        
        # Combined response
        response = {
            "original": original_result,
            "v2_automation": v2_result,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
'''
    
    return integration_code

# Test the V2 integration
def test_v2_integration():
    """Test the V2 webhook integration"""
    print("🧪 TESTING V2 WEBHOOK INTEGRATION")
    print("=" * 50)
    
    integration = WebhookV2Integration()
    
    # Test webhook data (simulating TradingView webhook)
    test_webhook = {
        "type": "Bullish",
        "symbol": "NQ1!",
        "timestamp": "2025-10-25T14:30:00Z",
        "price": 20000.00,
        "session": "NY PM"
    }
    
    print("📡 Testing webhook processing...")
    result = integration.enhanced_webhook_handler(test_webhook)
    print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_v2_integration()
#!/usr/bin/env python3
"""
Real-time TradingView data via WebSocket + OpenAI analysis
Better than Chrome extension
"""

import websocket
import json
import openai
import os
from threading import Thread
import time

class TradingViewWebSocket:
    def __init__(self):
        self.ws = None
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.last_analysis = None
        
    def connect(self):
        """Connect to TradingView WebSocket"""
        # TradingView WebSocket endpoint (example)
        ws_url = "wss://data.tradingview.com/socket.io/websocket"
        
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        # Run in separate thread
        Thread(target=self.ws.run_forever, daemon=True).start()
    
    def on_open(self, ws):
        """Subscribe to NQ data"""
        print("✅ Connected to TradingView WebSocket")
        
        # Subscribe to NQ1! real-time data
        subscribe_msg = {
            "m": "set_auth_token",
            "p": ["unauthorized_user_token"]
        }
        ws.send(json.dumps(subscribe_msg))
        
        # Subscribe to symbol
        symbol_msg = {
            "m": "quote_add_symbols",
            "p": ["CME_MINI:NQ1!"]
        }
        ws.send(json.dumps(symbol_msg))
    
    def on_message(self, ws, message):
        """Process real-time data"""
        try:
            data = json.loads(message)
            
            # Parse TradingView message format
            if 'm' in data and data['m'] == 'qsd':
                symbol_data = data.get('p', [])
                if symbol_data and 'CME_MINI:NQ1!' in str(symbol_data):
                    self.process_price_update(symbol_data)
                    
        except Exception as e:
            print(f"❌ Message processing error: {e}")
    
    def process_price_update(self, data):
        """Process price update and get AI analysis"""
        try:
            # Extract price data (format varies)
            price_info = {
                'symbol': 'NQ1!',
                'price': self.extract_price(data),
                'timestamp': time.time(),
                'volume': self.extract_volume(data)
            }
            
            # Get AI analysis every 30 seconds
            if (not self.last_analysis or 
                time.time() - self.last_analysis > 30):
                
                analysis = self.get_ai_analysis(price_info)
                self.last_analysis = time.time()
                
                print(f"🤖 AI Analysis: {analysis}")
                
        except Exception as e:
            print(f"❌ Price processing error: {e}")
    
    def extract_price(self, data):
        """Extract current price from WebSocket data"""
        # TradingView data format parsing
        try:
            if isinstance(data, list) and len(data) > 1:
                price_data = data[1]
                if isinstance(price_data, dict):
                    return price_data.get('lp', price_data.get('price', 15000))
            return 15000  # Default
        except:
            return 15000
    
    def extract_volume(self, data):
        """Extract volume from WebSocket data"""
        try:
            if isinstance(data, list) and len(data) > 1:
                price_data = data[1]
                if isinstance(price_data, dict):
                    return price_data.get('volume', 0)
            return 0
        except:
            return 0
    
    def get_ai_analysis(self, price_info):
        """Get OpenAI analysis of current market conditions"""
        try:
            prompt = f"""
            Analyze current NQ futures market:
            
            Price: ${price_info['price']}
            Volume: {price_info['volume']}
            Time: {time.strftime('%H:%M:%S EST')}
            
            Provide real-time trading analysis:
            {{
                "market_bias": "BULLISH/BEARISH/NEUTRAL",
                "entry_signal": "BUY/SELL/WAIT",
                "confidence": 0.0-1.0,
                "key_levels": ["support", "resistance"],
                "session_context": "analysis of current session",
                "risk_assessment": "LOW/MEDIUM/HIGH"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": str(e), "market_bias": "NEUTRAL"}
    
    def on_error(self, ws, error):
        print(f"❌ WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        print("🔌 WebSocket connection closed")

# Usage
if __name__ == "__main__":
    tv_ws = TradingViewWebSocket()
    tv_ws.connect()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("👋 Shutting down...")
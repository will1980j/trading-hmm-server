import asyncio
import websocket
import json
from datetime import datetime

class Level2DataProvider:
    def __init__(self):
        self.level2_data = {}
        
    async def connect_polygon(self, api_key):
        """Connect to Polygon.io Level 2 data"""
        ws_url = f"wss://socket.polygon.io/stocks?apikey={api_key}"
        
        def on_message(ws, message):
            data = json.loads(message)
            if data.get('ev') == 'Q':  # Quote data
                symbol = data.get('sym')
                self.level2_data[symbol] = {
                    'bid': data.get('bp'),
                    'ask': data.get('ap'), 
                    'bid_size': data.get('bs'),
                    'ask_size': data.get('as'),
                    'spread': data.get('ap') - data.get('bp'),
                    'timestamp': datetime.now().isoformat()
                }
        
        ws = websocket.WebSocketApp(ws_url, on_message=on_message)
        ws.run_forever()
    
    def get_signal_strength_with_level2(self, symbol, base_strength):
        """Enhance signal strength with Level 2 data"""
        if symbol not in self.level2_data:
            return base_strength
            
        l2 = self.level2_data[symbol]
        
        # Spread factor (tighter spread = stronger signal)
        spread_factor = 10 if l2['spread'] < 0.25 else 5 if l2['spread'] < 0.50 else 0
        
        # Size imbalance factor
        total_size = l2['bid_size'] + l2['ask_size']
        imbalance = abs(l2['bid_size'] - l2['ask_size']) / total_size if total_size > 0 else 0
        imbalance_factor = 15 if imbalance > 0.7 else 10 if imbalance > 0.5 else 0
        
        return min(100, base_strength + spread_factor + imbalance_factor)

# Global instance
level2_provider = Level2DataProvider()
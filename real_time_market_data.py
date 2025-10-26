"""
Real-Time Market Data Feed for V2 Automation
Provides live NASDAQ price data for confirmation monitoring and MFE tracking
"""

import asyncio
import websocket
import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional
import requests
from dataclasses import dataclass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Market data structure"""
    symbol: str
    price: float
    timestamp: int
    volume: int = 0
    bid: float = 0.0
    ask: float = 0.0

class MarketDataProvider:
    """Base class for market data providers"""
    
    def __init__(self):
        self.subscribers: List[Callable] = []
        self.is_connected = False
        
    def subscribe(self, callback: Callable):
        """Subscribe to market data updates"""
        self.subscribers.append(callback)
        
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from market data updates"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            
    def notify_subscribers(self, data: MarketData):
        """Notify all subscribers of new market data"""
        for callback in self.subscribers:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {str(e)}")

class PolygonMarketData(MarketDataProvider):
    """Polygon.io market data provider"""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.ws = None
        self.symbols = set()
        
    def connect(self):
        """Connect to Polygon WebSocket"""
        try:
            websocket.enableTrace(True)
            self.ws = websocket.WebSocketApp(
                f"wss://socket.polygon.io/stocks",
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run in separate thread
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
        except Exception as e:
            logger.error(f"Polygon connection error: {str(e)}")
            
    def on_open(self, ws):
        """WebSocket connection opened"""
        logger.info("Polygon WebSocket connected")
        
        # Authenticate
        auth_msg = {
            "action": "auth",
            "params": self.api_key
        }
        ws.send(json.dumps(auth_msg))
        self.is_connected = True
        
    def on_message(self, ws, message):
        """Handle incoming market data"""
        try:
            data = json.loads(message)
            
            if isinstance(data, list):
                for item in data:
                    self.process_message(item)
            else:
                self.process_message(data)
                
        except Exception as e:
            logger.error(f"Error processing Polygon message: {str(e)}")
            
    def process_message(self, msg: Dict):
        """Process individual market data message"""
        try:
            if msg.get('ev') == 'T':  # Trade data
                market_data = MarketData(
                    symbol=msg.get('sym', ''),
                    price=float(msg.get('p', 0)),
                    timestamp=int(msg.get('t', 0)),
                    volume=int(msg.get('s', 0))
                )
                
                self.notify_subscribers(market_data)
                
        except Exception as e:
            logger.error(f"Error processing Polygon trade data: {str(e)}")
            
    def subscribe_symbol(self, symbol: str):
        """Subscribe to a specific symbol"""
        if self.is_connected and symbol not in self.symbols:
            subscribe_msg = {
                "action": "subscribe",
                "params": f"T.{symbol}"
            }
            self.ws.send(json.dumps(subscribe_msg))
            self.symbols.add(symbol)
            logger.info(f"Subscribed to {symbol}")
            
    def on_error(self, ws, error):
        """WebSocket error"""
        logger.error(f"Polygon WebSocket error: {error}")
        self.is_connected = False
        
    def on_close(self, ws, close_status_code, close_msg):
        """WebSocket closed"""
        logger.info("Polygon WebSocket closed")
        self.is_connected = False

class AlphaVantageMarketData(MarketDataProvider):
    """Alpha Vantage market data provider (REST API polling)"""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.symbols = set()
        self.polling_interval = 1  # seconds
        self.is_running = False
        
    def connect(self):
        """Start polling for market data"""
        self.is_running = True
        self.is_connected = True
        
        # Start polling thread
        polling_thread = threading.Thread(target=self.poll_data)
        polling_thread.daemon = True
        polling_thread.start()
        
        logger.info("Alpha Vantage polling started")
        
    def poll_data(self):
        """Poll market data for subscribed symbols"""
        while self.is_running:
            try:
                for symbol in self.symbols:
                    self.fetch_quote(symbol)
                    
                time.sleep(self.polling_interval)
                
            except Exception as e:
                logger.error(f"Alpha Vantage polling error: {str(e)}")
                time.sleep(5)  # Wait before retrying
                
    def fetch_quote(self, symbol: str):
        """Fetch current quote for symbol"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if "Global Quote" in data:
                quote = data["Global Quote"]
                
                market_data = MarketData(
                    symbol=symbol,
                    price=float(quote.get("05. price", 0)),
                    timestamp=int(time.time() * 1000),
                    volume=int(quote.get("06. volume", 0))
                )
                
                self.notify_subscribers(market_data)
                
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage quote for {symbol}: {str(e)}")
            
    def subscribe_symbol(self, symbol: str):
        """Subscribe to a specific symbol"""
        self.symbols.add(symbol)
        logger.info(f"Subscribed to {symbol} (Alpha Vantage)")
        
    def disconnect(self):
        """Stop polling"""
        self.is_running = False
        self.is_connected = False

class NoDataProvider(MarketDataProvider):
    """No-data provider - shows error when no real data source configured"""
    
    def __init__(self):
        super().__init__()
        self.symbols = set()
        
    def connect(self):
        """Show error - no real data source configured"""
        logger.error("❌ NO REAL MARKET DATA CONFIGURED")
        logger.error("❌ Configure Polygon.io or Alpha Vantage API key for real data")
        logger.error("❌ System cannot function without real market data")
        self.is_connected = False
        
    def subscribe_symbol(self, symbol: str):
        """Show error for symbol subscription"""
        logger.error(f"❌ Cannot subscribe to {symbol} - no real data source")
        
    def disconnect(self):
        """Disconnect (nothing to disconnect)"""
        self.is_connected = False

class MarketDataManager:
    """Manages market data providers and routing"""
    
    def __init__(self):
        self.provider: Optional[MarketDataProvider] = None
        self.subscribers: Dict[str, List[Callable]] = {}
        
    def set_provider(self, provider: MarketDataProvider):
        """Set the market data provider"""
        if self.provider:
            self.provider.unsubscribe(self.on_market_data)
            
        self.provider = provider
        self.provider.subscribe(self.on_market_data)
        
    def subscribe_to_symbol(self, symbol: str, callback: Callable):
        """Subscribe to market data for a specific symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
            
        self.subscribers[symbol].append(callback)
        
        # Subscribe to provider if connected
        if self.provider and self.provider.is_connected:
            self.provider.subscribe_symbol(symbol)
            
    def on_market_data(self, data: MarketData):
        """Route market data to symbol-specific subscribers"""
        if data.symbol in self.subscribers:
            for callback in self.subscribers[data.symbol]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error notifying market data subscriber: {str(e)}")
                    
    def connect(self):
        """Connect to market data provider"""
        if self.provider:
            self.provider.connect()
            
            # Subscribe to all symbols once connected
            for symbol in self.subscribers.keys():
                self.provider.subscribe_symbol(symbol)

# Global market data manager instance
market_data_manager = MarketDataManager()

def setup_market_data_provider(provider_type: str = "mock", **kwargs):
    """Setup market data provider"""
    
    if provider_type == "polygon":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("Polygon API key required")
        provider = PolygonMarketData(api_key)
        
    elif provider_type == "alphavantage":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("Alpha Vantage API key required")
        provider = AlphaVantageMarketData(api_key)
        
    else:
        logger.error(f"❌ Invalid provider type: {provider_type}")
        logger.error("❌ Only 'polygon' and 'alphavantage' supported")
        logger.error("❌ NO FAKE DATA ALLOWED")
        raise ValueError(f"Invalid provider type: {provider_type}. Use 'polygon' or 'alphavantage' with real API key.")
        
    market_data_manager.set_provider(provider)
    market_data_manager.connect()
    
    return market_data_manager

def subscribe_to_nasdaq_data(callback: Callable):
    """Convenience function to subscribe to NASDAQ data"""
    market_data_manager.subscribe_to_symbol("NQ", callback)  # NASDAQ futures
    market_data_manager.subscribe_to_symbol("QQQ", callback)  # NASDAQ ETF

# Example usage
if __name__ == "__main__":
    def on_price_update(data: MarketData):
        print(f"{data.symbol}: ${data.price} at {datetime.fromtimestamp(data.timestamp/1000)}")
        
    # Setup mock provider for testing
    manager = setup_market_data_provider("mock")
    
    # Subscribe to NASDAQ data
    subscribe_to_nasdaq_data(on_price_update)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down market data...")
        if manager.provider:
            manager.provider.disconnect()
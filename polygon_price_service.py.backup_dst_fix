"""
Polygon.io Real-Time Price Service
Fetches NASDAQ (NQ) prices and feeds to dashboard
5 API calls per minute limit
"""
import requests
import time
import threading
from datetime import datetime
import pytz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolygonPriceService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self.is_running = False
        self.last_price = None
        self.last_update = None
        
    def get_current_session(self):
        """Determine current trading session"""
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        hour = now.hour
        minute = now.minute
        
        if (hour == 8 and minute >= 30) or (9 <= hour <= 11):
            return "NY AM", True
        elif 13 <= hour <= 15:
            return "NY PM", True
        elif hour == 12:
            return "NY LUNCH", False
        elif 0 <= hour <= 5:
            return "LONDON", False
        elif hour >= 6 and (hour < 8 or (hour == 8 and minute <= 29)):
            return "NY PRE", False
        elif 20 <= hour <= 23:
            return "ASIA", False
        else:
            return "INVALID", False
    
    def get_nasdaq_price(self):
        """
        Get current NASDAQ futures price from Polygon
        Uses NQ (E-mini NASDAQ-100 Futures) ticker
        """
        try:
            # Get last trade for NQ futures
            # Polygon uses X:NQMESZ2024 format for futures
            # For simplicity, we'll use the index NQX or try NQ
            
            # Try getting NASDAQ-100 index quote
            url = f"{self.base_url}/v2/last/trade/I:NDX"
            params = {"apiKey": self.api_key}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and 'results' in data:
                    result = data['results']
                    price = result.get('p', 0)  # price
                    timestamp = result.get('t', int(time.time() * 1000))  # timestamp
                    
                    # Calculate change from last price
                    change = 0
                    if self.last_price:
                        change = price - self.last_price
                    
                    self.last_price = price
                    self.last_update = datetime.now()
                    
                    session, is_priority = self.get_current_session()
                    
                    return {
                        'price': price,
                        'timestamp': timestamp,
                        'session': session,
                        'change': change,
                        'volume': result.get('s', 0),  # size
                        'bid': price - 0.25,  # Approximate
                        'ask': price + 0.25,  # Approximate
                        'source': 'polygon.io',
                        'status': 'success'
                    }
                else:
                    logger.warning(f"Polygon API returned non-OK status: {data}")
                    return None
            else:
                logger.error(f"Polygon API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching Polygon price: {str(e)}")
            return None
    
    def start_polling(self, callback, interval=12):
        """
        Start polling Polygon API
        interval: seconds between calls (default 12s = 5 calls/minute)
        callback: function to call with price data
        """
        self.is_running = True
        
        def poll_loop():
            logger.info("🚀 Polygon price polling started")
            while self.is_running:
                try:
                    # Check if market is open
                    session, _ = self.get_current_session()
                    
                    if session != "INVALID":
                        # Market is open, fetch price
                        price_data = self.get_nasdaq_price()
                        
                        if price_data:
                            logger.info(f"📊 Polygon price: ${price_data['price']:.2f} ({session})")
                            callback(price_data)
                        else:
                            logger.warning("⚠️ Failed to fetch price from Polygon")
                    else:
                        logger.info("🌙 Market closed (INVALID session)")
                    
                    # Wait for next interval
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error in polling loop: {str(e)}")
                    time.sleep(interval)
        
        # Start polling thread
        thread = threading.Thread(target=poll_loop, daemon=True)
        thread.start()
        logger.info(f"✅ Polygon polling thread started (interval: {interval}s)")
    
    def stop_polling(self):
        """Stop polling"""
        self.is_running = False
        logger.info("🛑 Polygon price polling stopped")


# Integration with existing realtime price handler
def integrate_with_realtime_handler():
    """
    Integrate Polygon service with existing realtime price handler
    """
    try:
        from realtime_price_webhook_handler import realtime_price_handler, RealTimePriceUpdate
        
        # Create Polygon service
        polygon_service = PolygonPriceService(api_key="_azuCKXmKg9r1442lnX90Sx1zYLeu_hZ")
        
        # Callback to feed data to realtime handler
        def on_price_update(price_data):
            try:
                # Create RealTimePriceUpdate object
                price_update = RealTimePriceUpdate(
                    symbol="NQ",
                    price=price_data['price'],
                    timestamp=price_data['timestamp'],
                    session=price_data['session'],
                    volume=price_data['volume'],
                    bid=price_data['bid'],
                    ask=price_data['ask'],
                    change=price_data['change'],
                    source="polygon.io"
                )
                
                # Feed to realtime handler
                realtime_price_handler.latest_price = price_update
                realtime_price_handler.notify_subscribers(price_update)
                
                logger.info(f"✅ Fed Polygon price to realtime handler: ${price_data['price']:.2f}")
                
            except Exception as e:
                logger.error(f"Error feeding price to handler: {str(e)}")
        
        # Start polling (12 seconds = 5 calls/minute)
        polygon_service.start_polling(on_price_update, interval=12)
        
        logger.info("🎯 Polygon service integrated with realtime price handler")
        return polygon_service
        
    except ImportError:
        logger.error("Could not import realtime_price_webhook_handler")
        return None


if __name__ == "__main__":
    # Test the service
    print("🧪 Testing Polygon Price Service")
    print("=" * 60)
    
    service = PolygonPriceService(api_key="_azuCKXmKg9r1442lnX90Sx1zYLeu_hZ")
    
    print("\n📊 Fetching current NASDAQ price...")
    price_data = service.get_nasdaq_price()
    
    if price_data:
        print(f"\n✅ SUCCESS!")
        print(f"   Price: ${price_data['price']:.2f}")
        print(f"   Session: {price_data['session']}")
        print(f"   Change: {price_data['change']:+.2f}")
        print(f"   Timestamp: {datetime.fromtimestamp(price_data['timestamp']/1000)}")
        print(f"   Source: {price_data['source']}")
    else:
        print("\n❌ FAILED to fetch price")
    
    print("\n" + "=" * 60)
    print("🚀 Starting polling service (Ctrl+C to stop)...")
    
    def print_price(data):
        print(f"📊 ${data['price']:.2f} | {data['session']} | {data['change']:+.2f}")
    
    service.start_polling(print_price, interval=12)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping service...")
        service.stop_polling()

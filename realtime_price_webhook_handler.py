"""
Real-Time Price Webhook Handler
Receives and processes 1-second price updates from TradingView Premium
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
import threading
import queue

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealTimePriceUpdate:
    """Real-time price update from TradingView"""
    symbol: str
    price: float
    timestamp: int
    session: str
    volume: int
    bid: float
    ask: float
    change: float
    source: str = "tradingview_1s"

class RealTimePriceHandler:
    """Handles real-time price updates from TradingView 1-second indicator"""
    
    def __init__(self):
        self.subscribers: List[Callable] = []
        self.price_queue = queue.Queue(maxsize=1000)  # Buffer for high-frequency updates
        self.latest_price: Optional[RealTimePriceUpdate] = None
        self.is_running = False
        self.price_count = 0
        self.last_log_time = time.time()
        
        # Performance tracking
        self.updates_per_second = 0
        self.total_updates = 0
        
    def start_handler(self):
        """Start the real-time price handler"""
        self.is_running = True
        
        # Start price processing thread
        processing_thread = threading.Thread(target=self.process_price_queue)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Start performance monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_performance)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("🚀 Real-time price handler started (1-second updates)")
        
    def stop_handler(self):
        """Stop the handler"""
        self.is_running = False
        logger.info("🛑 Real-time price handler stopped")
        
    def receive_price_webhook(self, webhook_data: Dict) -> Dict:
        """
        Receive price update from TradingView webhook
        Called by Flask route when TradingView sends 1-second price data
        """
        try:
            # Validate webhook data
            if webhook_data.get('type') != 'realtime_price':
                return {"status": "ignored", "reason": "not_realtime_price"}
                
            # Extract price data
            price_update = RealTimePriceUpdate(
                symbol=webhook_data.get('symbol', 'NQ'),
                price=float(webhook_data.get('price', 0)),
                timestamp=int(webhook_data.get('timestamp', time.time() * 1000)),
                session=webhook_data.get('session', 'UNKNOWN'),
                volume=int(webhook_data.get('volume', 0)),
                bid=float(webhook_data.get('bid', 0)),
                ask=float(webhook_data.get('ask', 0)),
                change=float(webhook_data.get('change', 0))
            )
            
            # Validate price data
            if price_update.price <= 0:
                return {"status": "error", "reason": "invalid_price"}
                
            # Add to processing queue (non-blocking)
            try:
                self.price_queue.put_nowait(price_update)
                self.total_updates += 1
                
                return {
                    "status": "success",
                    "message": "Real-time price update received",
                    "price": price_update.price,
                    "session": price_update.session,
                    "queue_size": self.price_queue.qsize()
                }
                
            except queue.Full:
                logger.warning("⚠️ Price queue full - dropping oldest updates")
                # Remove old updates and add new one
                try:
                    self.price_queue.get_nowait()  # Remove oldest
                    self.price_queue.put_nowait(price_update)  # Add newest
                    return {"status": "success", "message": "Price update queued (queue was full)"}
                except:
                    return {"status": "error", "reason": "queue_management_failed"}
                    
        except Exception as e:
            logger.error(f"Error processing real-time price webhook: {str(e)}")
            return {"status": "error", "reason": str(e)}
            
    def process_price_queue(self):
        """Process price updates from the queue"""
        while self.is_running:
            try:
                # Get price update from queue (with timeout)
                price_update = self.price_queue.get(timeout=1.0)
                
                # Update latest price
                self.latest_price = price_update
                
                # Notify all subscribers
                self.notify_subscribers(price_update)
                
                # Update performance counters
                self.price_count += 1
                
            except queue.Empty:
                continue  # Timeout, continue loop
            except Exception as e:
                logger.error(f"Error processing price queue: {str(e)}")
                
    def notify_subscribers(self, price_update: RealTimePriceUpdate):
        """Notify all subscribers of price update"""
        for callback in self.subscribers:
            try:
                callback(price_update)
            except Exception as e:
                logger.error(f"Error notifying price subscriber: {str(e)}")
                
    def subscribe(self, callback: Callable):
        """Subscribe to real-time price updates"""
        self.subscribers.append(callback)
        logger.info(f"📊 New real-time price subscriber added (total: {len(self.subscribers)})")
        
    def get_latest_price(self) -> Optional[RealTimePriceUpdate]:
        """Get the latest price update"""
        return self.latest_price
        
    def monitor_performance(self):
        """Monitor performance and log statistics"""
        while self.is_running:
            try:
                time.sleep(10)  # Log every 10 seconds
                
                current_time = time.time()
                time_elapsed = current_time - self.last_log_time
                
                if time_elapsed > 0:
                    updates_per_second = self.price_count / time_elapsed
                    
                    logger.info(f"📊 Real-time price stats: "
                              f"{updates_per_second:.1f} updates/sec, "
                              f"Queue: {self.price_queue.qsize()}, "
                              f"Total: {self.total_updates}, "
                              f"Subscribers: {len(self.subscribers)}")
                    
                    # Reset counters
                    self.price_count = 0
                    self.last_log_time = current_time
                    
            except Exception as e:
                logger.error(f"Error in performance monitoring: {str(e)}")

# Global real-time price handler
realtime_price_handler = RealTimePriceHandler()

def start_realtime_price_handler():
    """Start the global real-time price handler"""
    realtime_price_handler.start_handler()
    return realtime_price_handler

def process_realtime_price_webhook(webhook_data: Dict) -> Dict:
    """Process real-time price webhook (called by Flask route)"""
    return realtime_price_handler.receive_price_webhook(webhook_data)

def subscribe_to_realtime_prices(callback: Callable):
    """Subscribe to real-time price updates"""
    realtime_price_handler.subscribe(callback)

def get_current_price() -> Optional[RealTimePriceUpdate]:
    """Get the current real-time price"""
    return realtime_price_handler.get_latest_price()

# Flask route integration code
FLASK_ROUTE_CODE = '''
# Add this route to your web_server.py

@app.route('/api/realtime-price', methods=['POST'])
def receive_realtime_price():
    """Receive real-time price updates from TradingView 1-second indicator"""
    try:
        data = request.get_json()
        result = process_realtime_price_webhook(data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Real-time price webhook error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
'''

# Example usage for MFE tracking integration
class RealTimeMFETracker:
    """Example of how to use real-time prices for MFE tracking"""
    
    def __init__(self):
        self.active_trades = {}
        
        # Subscribe to real-time price updates
        subscribe_to_realtime_prices(self.on_price_update)
        
    def add_trade(self, trade_uuid: str, entry_price: float, stop_loss: float, signal_type: str):
        """Add a trade for real-time MFE tracking"""
        self.active_trades[trade_uuid] = {
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "signal_type": signal_type,
            "current_mfe": 0.0,
            "max_mfe": 0.0,
            "risk_distance": abs(entry_price - stop_loss)
        }
        
        logger.info(f"📈 Added trade {trade_uuid} for real-time MFE tracking")
        
    def on_price_update(self, price_update: RealTimePriceUpdate):
        """Handle real-time price updates for MFE calculation"""
        current_price = price_update.price
        
        for trade_uuid, trade in self.active_trades.items():
            try:
                # Calculate real-time MFE
                if trade["signal_type"] == "Bullish":
                    mfe = (current_price - trade["entry_price"]) / trade["risk_distance"]
                else:  # Bearish
                    mfe = (trade["entry_price"] - current_price) / trade["risk_distance"]
                
                # Update MFE
                trade["current_mfe"] = mfe
                if mfe > trade["max_mfe"]:
                    trade["max_mfe"] = mfe
                    logger.info(f"📈 New MFE high for {trade_uuid}: {mfe:.4f}R")
                
                # Check for break-even trigger (+1R)
                if mfe >= 1.0 and trade.get("break_even_triggered") != True:
                    trade["break_even_triggered"] = True
                    logger.info(f"🎯 Break-even triggered for {trade_uuid} at +1R!")
                
                # Check for stop loss hit
                if ((trade["signal_type"] == "Bullish" and current_price <= trade["stop_loss"]) or
                    (trade["signal_type"] == "Bearish" and current_price >= trade["stop_loss"])):
                    logger.warning(f"🛑 Stop loss hit for {trade_uuid} at ${current_price}")
                    # Remove from active tracking
                    del self.active_trades[trade_uuid]
                    break
                    
            except Exception as e:
                logger.error(f"Error calculating MFE for {trade_uuid}: {str(e)}")

if __name__ == "__main__":
    print("🚀 Real-Time Price Handler Test")
    print("=" * 50)
    
    # Start the handler
    handler = start_realtime_price_handler()
    
    # Example price subscriber
    def on_price_update(price_update: RealTimePriceUpdate):
        print(f"📊 {price_update.symbol}: ${price_update.price} "
              f"({price_update.change:+.2f}) "
              f"[{price_update.session}] "
              f"@ {datetime.fromtimestamp(price_update.timestamp/1000).strftime('%H:%M:%S')}")
    
    # Subscribe to updates
    subscribe_to_realtime_prices(on_price_update)
    
    # Create MFE tracker example
    mfe_tracker = RealTimeMFETracker()
    
    print("✅ Real-time price handler started")
    print("📊 Waiting for TradingView 1-second price updates...")
    print("🔧 Configure TradingView 1s indicator with webhook URL")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping real-time price handler...")
        handler.stop_handler()
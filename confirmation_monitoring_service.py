"""
Confirmation Monitoring Service for V2 Automation
Monitors market data for signal confirmations and triggers trade entries
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
import psycopg2
from real_time_market_data import MarketData, market_data_manager, subscribe_to_nasdaq_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConfirmationRequirement:
    """Represents a confirmation requirement for a signal"""
    trade_uuid: str
    signal_type: str  # "Bullish" or "Bearish"
    target_price: float
    condition: str  # "candle_close_above_signal_high" or "candle_close_below_signal_low"
    signal_candle_high: float
    signal_candle_low: float
    created_at: datetime
    last_check: Optional[datetime] = None
    current_candle_open: Optional[float] = None
    current_candle_high: Optional[float] = None
    current_candle_low: Optional[float] = None
    candle_start_time: Optional[datetime] = None

class CandleTracker:
    """Tracks current 1-minute candle formation"""
    
    def __init__(self):
        self.current_candle = {
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "start_time": None,
            "end_time": None
        }
        self.candle_subscribers: List = []
        
    def update_price(self, price: float, timestamp: int):
        """Update current candle with new price"""
        current_time = datetime.fromtimestamp(timestamp / 1000)
        current_minute = current_time.replace(second=0, microsecond=0)
        
        # Check if we need to start a new candle
        if (self.current_candle["start_time"] is None or 
            current_minute > self.current_candle["start_time"]):
            
            # Close previous candle if it exists
            if self.current_candle["start_time"] is not None:
                self.current_candle["close"] = price
                self.current_candle["end_time"] = current_time
                self.notify_candle_close()
            
            # Start new candle
            self.current_candle = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "start_time": current_minute,
                "end_time": None
            }
            
            logger.info(f"New candle started at {current_minute}: Open=${price}")
            
        else:
            # Update current candle
            if price > self.current_candle["high"]:
                self.current_candle["high"] = price
            if price < self.current_candle["low"]:
                self.current_candle["low"] = price
            self.current_candle["close"] = price
            
    def notify_candle_close(self):
        """Notify subscribers when a candle closes"""
        for callback in self.candle_subscribers:
            try:
                callback(self.current_candle.copy())
            except Exception as e:
                logger.error(f"Error notifying candle subscriber: {str(e)}")
                
    def subscribe_to_candle_close(self, callback):
        """Subscribe to candle close events"""
        self.candle_subscribers.append(callback)

class ConfirmationMonitor:
    """Monitors market data for signal confirmations"""
    
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.active_confirmations: Dict[str, ConfirmationRequirement] = {}
        self.candle_tracker = CandleTracker()
        self.is_running = False
        
        # Subscribe to candle close events
        self.candle_tracker.subscribe_to_candle_close(self.on_candle_close)
        
    def start_monitoring(self):
        """Start the confirmation monitoring service"""
        logger.info("Starting confirmation monitoring service...")
        
        self.is_running = True
        
        # Load active confirmations from database
        self.load_active_confirmations()
        
        # Subscribe to market data
        subscribe_to_nasdaq_data(self.on_market_data)
        
        logger.info(f"Monitoring {len(self.active_confirmations)} active confirmations")
        
    def stop_monitoring(self):
        """Stop the confirmation monitoring service"""
        logger.info("Stopping confirmation monitoring service...")
        self.is_running = False
        
    def load_active_confirmations(self):
        """Load active confirmation requirements from database"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()
            
            # Get active confirmations
            cursor.execute("""
                SELECT 
                    cm.trade_uuid,
                    cm.signal_type,
                    cm.target_price,
                    cm.condition,
                    es.signal_candle_high,
                    es.signal_candle_low,
                    cm.created_at
                FROM confirmation_monitor cm
                JOIN enhanced_signals_v2 es ON cm.trade_uuid = es.trade_uuid
                WHERE cm.is_active = TRUE
                AND es.confirmation_received = FALSE
            """)
            
            results = cursor.fetchall()
            
            for row in results:
                trade_uuid = str(row[0])
                confirmation = ConfirmationRequirement(
                    trade_uuid=trade_uuid,
                    signal_type=row[1],
                    target_price=float(row[2]),
                    condition=row[3],
                    signal_candle_high=float(row[4]),
                    signal_candle_low=float(row[5]),
                    created_at=row[6]
                )
                
                self.active_confirmations[trade_uuid] = confirmation
                
            cursor.close()
            conn.close()
            
            logger.info(f"Loaded {len(self.active_confirmations)} active confirmations")
            
        except Exception as e:
            logger.error(f"Error loading active confirmations: {str(e)}")
            
    def on_market_data(self, data: MarketData):
        """Handle incoming market data"""
        if not self.is_running:
            return
            
        # Update candle tracker
        self.candle_tracker.update_price(data.price, data.timestamp)
        
        # Update confirmation requirements with current price
        for confirmation in self.active_confirmations.values():
            confirmation.last_check = datetime.now()
            
    def on_candle_close(self, candle_data: Dict):
        """Handle candle close events - check for confirmations"""
        logger.info(f"Candle closed: O={candle_data['open']}, H={candle_data['high']}, "
                   f"L={candle_data['low']}, C={candle_data['close']}")
        
        confirmations_to_remove = []
        
        for trade_uuid, confirmation in self.active_confirmations.items():
            try:
                if self.check_confirmation(confirmation, candle_data):
                    logger.info(f"CONFIRMATION TRIGGERED for {trade_uuid}!")
                    
                    # Process the confirmation
                    self.process_confirmation(confirmation, candle_data)
                    
                    # Mark for removal
                    confirmations_to_remove.append(trade_uuid)
                    
            except Exception as e:
                logger.error(f"Error checking confirmation for {trade_uuid}: {str(e)}")
                
        # Remove confirmed trades
        for trade_uuid in confirmations_to_remove:
            del self.active_confirmations[trade_uuid]
            
    def check_confirmation(self, confirmation: ConfirmationRequirement, candle_data: Dict) -> bool:
        """Check if confirmation requirements are met"""
        
        if confirmation.signal_type == "Bullish":
            # Bullish confirmation: candle closes above signal candle high
            if confirmation.condition == "candle_close_above_signal_high":
                return candle_data["close"] > confirmation.signal_candle_high
                
        elif confirmation.signal_type == "Bearish":
            # Bearish confirmation: candle closes below signal candle low
            if confirmation.condition == "candle_close_below_signal_low":
                return candle_data["close"] < confirmation.signal_candle_low
                
        return False
        
    def process_confirmation(self, confirmation: ConfirmationRequirement, candle_data: Dict):
        """Process a confirmed signal"""
        try:
            # Calculate entry price (next candle open - estimated as current close + small gap)
            entry_price = candle_data["close"] + (0.25 if confirmation.signal_type == "Bullish" else -0.25)
            
            # Update database with confirmation
            self.update_confirmation_in_database(confirmation, candle_data, entry_price)
            
            # Trigger entry execution (would integrate with broker API)
            self.trigger_entry_execution(confirmation, entry_price)
            
            logger.info(f"Confirmation processed for {confirmation.trade_uuid}: "
                       f"Entry=${entry_price}, Type={confirmation.signal_type}")
                       
        except Exception as e:
            logger.error(f"Error processing confirmation: {str(e)}")
            
    def update_confirmation_in_database(self, confirmation: ConfirmationRequirement, 
                                       candle_data: Dict, entry_price: float):
        """Update database with confirmation data"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()
            
            # Update enhanced_signals_v2 table
            cursor.execute("""
                UPDATE enhanced_signals_v2 SET
                    confirmation_received = TRUE,
                    confirmation_timestamp = %s,
                    confirmation_candle_open = %s,
                    confirmation_candle_high = %s,
                    confirmation_candle_low = %s,
                    confirmation_candle_close = %s,
                    entry_price = %s,
                    entry_timestamp = %s,
                    status = 'confirmed'
                WHERE trade_uuid = %s
            """, (
                int(time.time() * 1000),
                candle_data["open"],
                candle_data["high"],
                candle_data["low"],
                candle_data["close"],
                entry_price,
                int(time.time() * 1000),
                confirmation.trade_uuid
            ))
            
            # Deactivate confirmation monitor
            cursor.execute("""
                UPDATE confirmation_monitor SET
                    is_active = FALSE,
                    last_check = CURRENT_TIMESTAMP
                WHERE trade_uuid = %s
            """, (confirmation.trade_uuid,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Database updated for confirmation {confirmation.trade_uuid}")
            
        except Exception as e:
            logger.error(f"Error updating confirmation in database: {str(e)}")
            
    def trigger_entry_execution(self, confirmation: ConfirmationRequirement, entry_price: float):
        """Trigger entry execution (placeholder for broker integration)"""
        
        # This would integrate with your broker API to execute the trade
        # For now, we'll just log the entry
        
        entry_data = {
            "trade_uuid": confirmation.trade_uuid,
            "signal_type": confirmation.signal_type,
            "entry_price": entry_price,
            "timestamp": int(time.time() * 1000),
            "status": "entry_triggered"
        }
        
        logger.info(f"ENTRY TRIGGERED: {json.dumps(entry_data, indent=2)}")
        
        # TODO: Integrate with broker API
        # - Place market order at next candle open
        # - Set stop loss order
        # - Set up MFE tracking
        
    def add_confirmation_requirement(self, trade_uuid: str, signal_type: str, 
                                   target_price: float, condition: str,
                                   signal_candle_high: float, signal_candle_low: float):
        """Add a new confirmation requirement"""
        
        confirmation = ConfirmationRequirement(
            trade_uuid=trade_uuid,
            signal_type=signal_type,
            target_price=target_price,
            condition=condition,
            signal_candle_high=signal_candle_high,
            signal_candle_low=signal_candle_low,
            created_at=datetime.now()
        )
        
        self.active_confirmations[trade_uuid] = confirmation
        
        logger.info(f"Added confirmation requirement for {trade_uuid}: "
                   f"{signal_type} @ ${target_price}")

# Global confirmation monitor instance
confirmation_monitor: Optional[ConfirmationMonitor] = None

def start_confirmation_monitoring(db_connection_string: str):
    """Start the global confirmation monitoring service"""
    global confirmation_monitor
    
    if confirmation_monitor is None:
        confirmation_monitor = ConfirmationMonitor(db_connection_string)
        
    confirmation_monitor.start_monitoring()
    return confirmation_monitor

def stop_confirmation_monitoring():
    """Stop the global confirmation monitoring service"""
    global confirmation_monitor
    
    if confirmation_monitor:
        confirmation_monitor.stop_monitoring()

def add_confirmation_requirement(trade_uuid: str, signal_type: str, 
                               target_price: float, condition: str,
                               signal_candle_high: float, signal_candle_low: float):
    """Add a confirmation requirement to the global monitor"""
    global confirmation_monitor
    
    if confirmation_monitor:
        confirmation_monitor.add_confirmation_requirement(
            trade_uuid, signal_type, target_price, condition,
            signal_candle_high, signal_candle_low
        )

# Example usage
if __name__ == "__main__":
    import os
    
    # Mock database connection string
    db_conn_string = os.environ.get('DATABASE_URL', 'postgresql://localhost/test')
    
    # Start monitoring
    monitor = start_confirmation_monitoring(db_conn_string)
    
    # Add a test confirmation requirement
    add_confirmation_requirement(
        trade_uuid="test-123",
        signal_type="Bullish",
        target_price=4157.5,
        condition="candle_close_above_signal_high",
        signal_candle_high=4157.5,
        signal_candle_low=4154.0
    )
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down confirmation monitoring...")
        stop_confirmation_monitoring()
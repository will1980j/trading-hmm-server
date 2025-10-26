"""
MFE Tracking Service for V2 Automation
Real-time Maximum Favorable Excursion tracking for active trades
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
class ActiveTrade:
    """Represents an active trade for MFE tracking"""
    trade_uuid: str
    signal_type: str  # "Bullish" or "Bearish"
    entry_price: float
    stop_loss_price: float
    risk_distance: float
    current_mfe: float = 0.0
    max_mfe: float = 0.0
    break_even_enabled: bool = True  # BE = 1 strategy
    break_even_triggered: bool = False
    last_price: float = 0.0
    last_update: Optional[datetime] = None
    created_at: Optional[datetime] = None

class MFETracker:
    """Tracks MFE for active trades"""
    
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.active_trades: Dict[str, ActiveTrade] = {}
        self.is_running = False
        
    def start_tracking(self):
        """Start MFE tracking service"""
        logger.info("Starting MFE tracking service...")
        
        self.is_running = True
        
        # Load active trades from database
        self.load_active_trades()
        
        # Subscribe to market data
        subscribe_to_nasdaq_data(self.on_market_data)
        
        logger.info(f"Tracking MFE for {len(self.active_trades)} active trades")
        
    def stop_tracking(self):
        """Stop MFE tracking service"""
        logger.info("Stopping MFE tracking service...")
        self.is_running = False
        
    def load_active_trades(self):
        """Load active trades from database"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()
            
            # Get confirmed trades that haven't been resolved
            cursor.execute("""
                SELECT 
                    trade_uuid,
                    signal_type,
                    entry_price,
                    stop_loss_price,
                    risk_distance,
                    current_mfe,
                    max_mfe,
                    created_at
                FROM enhanced_signals_v2
                WHERE confirmation_received = TRUE
                AND resolved = FALSE
                AND entry_price IS NOT NULL
                AND stop_loss_price IS NOT NULL
            """)
            
            results = cursor.fetchall()
            
            for row in results:
                trade_uuid = str(row[0])
                trade = ActiveTrade(
                    trade_uuid=trade_uuid,
                    signal_type=row[1],
                    entry_price=float(row[2]),
                    stop_loss_price=float(row[3]),
                    risk_distance=float(row[4]) if row[4] else 0.0,
                    current_mfe=float(row[5]) if row[5] else 0.0,
                    max_mfe=float(row[6]) if row[6] else 0.0,
                    created_at=row[7]
                )
                
                self.active_trades[trade_uuid] = trade
                
            cursor.close()
            conn.close()
            
            logger.info(f"Loaded {len(self.active_trades)} active trades for MFE tracking")
            
        except Exception as e:
            logger.error(f"Error loading active trades: {str(e)}")
            
    def on_market_data(self, data: MarketData):
        """Handle incoming market data for MFE calculation"""
        if not self.is_running:
            return
            
        current_price = data.price
        timestamp = data.timestamp
        
        trades_to_resolve = []
        
        for trade_uuid, trade in self.active_trades.items():
            try:
                # Update trade with current price
                trade.last_price = current_price
                trade.last_update = datetime.now()
                
                # Calculate current MFE
                new_mfe = self.calculate_mfe(trade, current_price)
                trade.current_mfe = new_mfe
                
                # Update max MFE if new high
                is_new_mfe_high = False
                if new_mfe > trade.max_mfe:
                    trade.max_mfe = new_mfe
                    is_new_mfe_high = True
                    logger.info(f"New MFE high for {trade_uuid}: {new_mfe:.4f}R")
                
                # Check for break-even trigger
                if (trade.break_even_enabled and not trade.break_even_triggered and 
                    new_mfe >= 1.0):
                    self.trigger_break_even(trade)
                    
                # Check for stop loss hit
                if self.check_stop_loss_hit(trade, current_price):
                    logger.warning(f"Stop loss hit for {trade_uuid} at ${current_price}")
                    trades_to_resolve.append((trade_uuid, "stop_loss", current_price))
                    
                # Update database with MFE
                self.update_mfe_in_database(trade, timestamp, is_new_mfe_high)
                
            except Exception as e:
                logger.error(f"Error processing MFE for {trade_uuid}: {str(e)}")
                
        # Resolve trades that hit stop loss
        for trade_uuid, resolution_type, resolution_price in trades_to_resolve:
            self.resolve_trade(trade_uuid, resolution_type, resolution_price, timestamp)
            
    def calculate_mfe(self, trade: ActiveTrade, current_price: float) -> float:
        """Calculate MFE based on trade type and current price"""
        
        if trade.risk_distance <= 0:
            return 0.0
            
        if trade.signal_type == "Bullish":
            # MFE = (current_price - entry_price) / risk_distance
            mfe = (current_price - trade.entry_price) / trade.risk_distance
        else:  # Bearish
            # MFE = (entry_price - current_price) / risk_distance
            mfe = (trade.entry_price - current_price) / trade.risk_distance
            
        return round(mfe, 4)
        
    def check_stop_loss_hit(self, trade: ActiveTrade, current_price: float) -> bool:
        """Check if stop loss has been hit"""
        
        if trade.break_even_triggered:
            # Stop loss moved to break-even (entry price)
            if trade.signal_type == "Bullish":
                return current_price <= trade.entry_price
            else:  # Bearish
                return current_price >= trade.entry_price
        else:
            # Original stop loss
            if trade.signal_type == "Bullish":
                return current_price <= trade.stop_loss_price
            else:  # Bearish
                return current_price >= trade.stop_loss_price
                
    def trigger_break_even(self, trade: ActiveTrade):
        """Trigger break-even logic (move stop loss to entry)"""
        try:
            trade.break_even_triggered = True
            
            logger.info(f"BREAK EVEN TRIGGERED for {trade.trade_uuid} at +1R!")
            
            # Update database
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE enhanced_signals_v2 SET
                    status = 'break_even_active'
                WHERE trade_uuid = %s
            """, (trade.trade_uuid,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # TODO: Update stop loss order with broker
            # This would move the actual stop loss order to break-even price
            
            logger.info(f"Break-even activated for {trade.trade_uuid}")
            
        except Exception as e:
            logger.error(f"Error triggering break-even for {trade.trade_uuid}: {str(e)}")
            
    def update_mfe_in_database(self, trade: ActiveTrade, timestamp: int, is_new_high: bool):
        """Update MFE data in database"""
        try:
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()
            
            # Update enhanced_signals_v2 table
            cursor.execute("""
                UPDATE enhanced_signals_v2 SET
                    current_mfe = %s,
                    max_mfe = %s
                WHERE trade_uuid = %s
            """, (trade.current_mfe, trade.max_mfe, trade.trade_uuid))
            
            # Insert MFE tracking record
            cursor.execute("""
                INSERT INTO mfe_tracking (
                    trade_uuid,
                    timestamp,
                    current_price,
                    mfe_value,
                    is_new_high
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                trade.trade_uuid,
                timestamp,
                trade.last_price,
                trade.current_mfe,
                is_new_high
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating MFE in database: {str(e)}")
            
    def resolve_trade(self, trade_uuid: str, resolution_type: str, 
                     resolution_price: float, timestamp: int):
        """Resolve a trade (stop loss hit, break-even, etc.)"""
        try:
            trade = self.active_trades.get(trade_uuid)
            if not trade:
                return
                
            logger.info(f"Resolving trade {trade_uuid}: {resolution_type} at ${resolution_price}")
            
            # Update database
            conn = psycopg2.connect(self.db_connection_string)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE enhanced_signals_v2 SET
                    resolved = TRUE,
                    resolution_type = %s,
                    resolution_price = %s,
                    resolution_timestamp = %s,
                    final_mfe = %s,
                    status = 'resolved'
                WHERE trade_uuid = %s
            """, (
                resolution_type,
                resolution_price,
                timestamp,
                trade.max_mfe,
                trade_uuid
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Remove from active tracking
            del self.active_trades[trade_uuid]
            
            logger.info(f"Trade {trade_uuid} resolved: Final MFE = {trade.max_mfe:.4f}R")
            
        except Exception as e:
            logger.error(f"Error resolving trade {trade_uuid}: {str(e)}")
            
    def add_active_trade(self, trade_uuid: str, signal_type: str, entry_price: float,
                        stop_loss_price: float, risk_distance: float):
        """Add a new active trade for MFE tracking"""
        
        trade = ActiveTrade(
            trade_uuid=trade_uuid,
            signal_type=signal_type,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            risk_distance=risk_distance,
            created_at=datetime.now()
        )
        
        self.active_trades[trade_uuid] = trade
        
        logger.info(f"Added active trade for MFE tracking: {trade_uuid} "
                   f"({signal_type} @ ${entry_price})")
                   
    def get_trade_status(self, trade_uuid: str) -> Optional[Dict]:
        """Get current status of a trade"""
        trade = self.active_trades.get(trade_uuid)
        if not trade:
            return None
            
        return {
            "trade_uuid": trade.trade_uuid,
            "signal_type": trade.signal_type,
            "entry_price": trade.entry_price,
            "current_price": trade.last_price,
            "current_mfe": trade.current_mfe,
            "max_mfe": trade.max_mfe,
            "break_even_triggered": trade.break_even_triggered,
            "last_update": trade.last_update.isoformat() if trade.last_update else None
        }

# Global MFE tracker instance
mfe_tracker: Optional[MFETracker] = None

def start_mfe_tracking(db_connection_string: str):
    """Start the global MFE tracking service"""
    global mfe_tracker
    
    if mfe_tracker is None:
        mfe_tracker = MFETracker(db_connection_string)
        
    mfe_tracker.start_tracking()
    return mfe_tracker

def stop_mfe_tracking():
    """Stop the global MFE tracking service"""
    global mfe_tracker
    
    if mfe_tracker:
        mfe_tracker.stop_tracking()

def add_active_trade(trade_uuid: str, signal_type: str, entry_price: float,
                    stop_loss_price: float, risk_distance: float):
    """Add an active trade to the global MFE tracker"""
    global mfe_tracker
    
    if mfe_tracker:
        mfe_tracker.add_active_trade(
            trade_uuid, signal_type, entry_price, stop_loss_price, risk_distance
        )

def get_trade_status(trade_uuid: str) -> Optional[Dict]:
    """Get trade status from global MFE tracker"""
    global mfe_tracker
    
    if mfe_tracker:
        return mfe_tracker.get_trade_status(trade_uuid)
    return None

# Example usage
if __name__ == "__main__":
    import os
    
    # Real database connection string - NO FAKE DATA
    db_conn_string = os.environ.get('DATABASE_URL')
    if not db_conn_string:
        raise ValueError("❌ DATABASE_URL required - no fake database operations")
    
    # Start MFE tracking
    tracker = start_mfe_tracking(db_conn_string)
    
    # Add a test active trade
    add_active_trade(
        trade_uuid="test-123",
        signal_type="Bullish",
        entry_price=4158.0,
        stop_loss_price=4129.0,
        risk_distance=29.0
    )
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Print status every 10 seconds
            if int(time.time()) % 10 == 0:
                status = get_trade_status("test-123")
                if status:
                    print(f"Trade Status: MFE={status['current_mfe']:.4f}R, "
                          f"Max={status['max_mfe']:.4f}R, "
                          f"Price=${status['current_price']}")
                          
    except KeyboardInterrupt:
        print("Shutting down MFE tracking...")
        stop_mfe_tracking()
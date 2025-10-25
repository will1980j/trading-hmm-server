#!/usr/bin/env python3
"""
Automated Signal Processor - The Holy Grail Implementation
Connects TradingView signals directly to Signal Lab V2 with automated price calculations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB
import json
from datetime import datetime, timezone
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedSignalProcessor:
    def __init__(self):
        self.db = RailwayDB()
        
    def process_tradingview_signal(self, signal_data):
        """
        Process incoming TradingView signal and create V2 trade entry with automated calculations
        
        Expected signal_data format:
        {
            "type": "Bullish" or "Bearish",
            "symbol": "NQ1!",
            "timestamp": "2025-10-25T10:30:00Z",
            "price": 20000.00,
            "session": "NY AM"
        }
        """
        try:
            logger.info(f"🚀 Processing TradingView signal: {signal_data.get('type', 'Unknown')}")
            
            # Extract signal information
            bias = signal_data.get('type', '').replace('ish', '')  # "Bullish" -> "Bullish"
            symbol = signal_data.get('symbol', 'NQ1!')
            timestamp_str = signal_data.get('timestamp', '')
            current_price = float(signal_data.get('price', 0))
            session = signal_data.get('session', self._determine_session())
            
            # Parse timestamp
            if timestamp_str:
                signal_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                signal_timestamp = datetime.now(timezone.utc)
            
            # Validate session timing
            if not self._is_valid_session(signal_timestamp):
                logger.warning(f"❌ Signal rejected - invalid session time: {signal_timestamp}")
                return {"success": False, "reason": "Invalid session time"}
            
            # Wait for confirmation (this would be enhanced with real-time price monitoring)
            confirmation_result = self._wait_for_confirmation(bias, current_price, signal_timestamp)
            
            if not confirmation_result["confirmed"]:
                logger.info(f"⏳ Signal pending confirmation: {bias}")
                return {"success": True, "status": "pending_confirmation", "signal_id": confirmation_result.get("signal_id")}
            
            # Calculate entry and stop loss prices
            entry_price = confirmation_result["entry_price"]
            stop_loss_price = self._calculate_stop_loss(bias, entry_price, confirmation_result["signal_candle_data"])
            
            # Calculate risk distance and R-targets
            risk_distance = abs(entry_price - stop_loss_price)
            r_targets = self._calculate_r_targets(entry_price, stop_loss_price, bias)
            
            # Create V2 trade entry
            trade_data = {
                "trade_uuid": str(uuid.uuid4()),
                "symbol": symbol,
                "bias": bias,
                "session": session,
                "date": signal_timestamp.date(),
                "time": signal_timestamp.time(),
                "entry_price": entry_price,
                "stop_loss_price": stop_loss_price,
                "risk_distance": risk_distance,
                "target_1r_price": r_targets["1R"],
                "target_2r_price": r_targets["2R"],
                "target_3r_price": r_targets["3R"],
                "target_5r_price": r_targets["5R"],
                "target_10r_price": r_targets["10R"],
                "target_20r_price": r_targets["20R"],
                "current_mfe": 0.00,
                "trade_status": "active",
                "active_trade": True,
                "auto_populated": True
            }
            
            # Insert into V2 database
            trade_id = self._insert_v2_trade(trade_data)
            
            if trade_id:
                logger.info(f"✅ Automated trade created: ID {trade_id}, UUID {trade_data['trade_uuid']}")
                
                # Start real-time MFE monitoring
                self._start_mfe_monitoring(trade_id, trade_data)
                
                return {
                    "success": True,
                    "trade_id": trade_id,
                    "trade_uuid": trade_data["trade_uuid"],
                    "entry_price": entry_price,
                    "stop_loss_price": stop_loss_price,
                    "r_targets": r_targets,
                    "status": "active"
                }
            else:
                logger.error("❌ Failed to insert V2 trade")
                return {"success": False, "reason": "Database insertion failed"}
                
        except Exception as e:
            logger.error(f"❌ Signal processing error: {e}")
            return {"success": False, "reason": str(e)}
    
    def _is_valid_session(self, timestamp):
        """Validate signal timing against trading sessions"""
        # Convert to Eastern Time for session validation
        from datetime import timezone, timedelta
        eastern = timezone(timedelta(hours=-5))  # EST (adjust for EDT as needed)
        et_time = timestamp.astimezone(eastern)
        hour = et_time.hour
        
        # Valid sessions (Eastern Time)
        valid_sessions = [
            (20, 23),  # ASIA: 20:00-23:59
            (0, 5),    # LONDON: 00:00-05:59
            (6, 8),    # NY PRE: 06:00-08:29 (partial)
            (8, 11),   # NY AM: 08:30-11:59 (partial)
            (12, 12),  # NY LUNCH: 12:00-12:59
            (13, 15)   # NY PM: 13:00-15:59
        ]
        
        for start, end in valid_sessions:
            if start <= hour <= end:
                return True
        
        return False
    
    def _determine_session(self):
        """Determine current trading session"""
        now = datetime.now(timezone.utc)
        if self._is_valid_session(now):
            # Simplified session determination
            from datetime import timezone, timedelta
            eastern = timezone(timedelta(hours=-5))
            et_time = now.astimezone(eastern)
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
        
        return "UNKNOWN"
    
    def _wait_for_confirmation(self, bias, signal_price, signal_timestamp):
        """
        Wait for signal confirmation based on trading methodology
        
        For now, this is a simplified version. In production, this would:
        1. Monitor real-time price data
        2. Wait for confirmation candle
        3. Calculate proper entry price
        """
        # Simplified confirmation logic (would be enhanced with real-time data)
        if bias == "Bullish":
            # Entry at next candle open after confirmation
            entry_price = signal_price + 2.5  # Simulate next candle open
        else:  # Bearish
            entry_price = signal_price - 2.5  # Simulate next candle open
        
        return {
            "confirmed": True,
            "entry_price": entry_price,
            "signal_candle_data": {
                "high": signal_price + 5,
                "low": signal_price - 5,
                "close": signal_price
            }
        }
    
    def _calculate_stop_loss(self, bias, entry_price, signal_candle_data):
        """Calculate stop loss based on trading methodology"""
        # Simplified stop loss calculation (25 points buffer)
        buffer = 25.0
        
        if bias == "Bullish":
            # Stop loss below signal candle low
            signal_low = signal_candle_data.get("low", entry_price - 10)
            stop_loss = signal_low - buffer
        else:  # Bearish
            # Stop loss above signal candle high
            signal_high = signal_candle_data.get("high", entry_price + 10)
            stop_loss = signal_high + buffer
        
        return round(stop_loss, 2)
    
    def _calculate_r_targets(self, entry_price, stop_loss_price, bias):
        """Calculate all R-multiple targets (1R through 20R)"""
        risk_distance = abs(entry_price - stop_loss_price)
        targets = {}
        
        for r in [1, 2, 3, 5, 10, 20]:
            if bias == "Bullish":
                target_price = entry_price + (r * risk_distance)
            else:  # Bearish
                target_price = entry_price - (r * risk_distance)
            
            targets[f"{r}R"] = round(target_price, 2)
        
        return targets
    
    def _insert_v2_trade(self, trade_data):
        """Insert trade into V2 database"""
        try:
            cursor = self.db.conn.cursor()
            
            insert_sql = """
            INSERT INTO signal_lab_v2_trades (
                trade_uuid, symbol, bias, session, date, time,
                entry_price, stop_loss_price, risk_distance,
                target_1r_price, target_2r_price, target_3r_price,
                target_5r_price, target_10r_price, target_20r_price,
                current_mfe, trade_status, active_trade, auto_populated
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s
            ) RETURNING id;
            """
            
            cursor.execute(insert_sql, (
                trade_data["trade_uuid"], trade_data["symbol"], trade_data["bias"],
                trade_data["session"], trade_data["date"], trade_data["time"],
                trade_data["entry_price"], trade_data["stop_loss_price"], trade_data["risk_distance"],
                trade_data["target_1r_price"], trade_data["target_2r_price"], trade_data["target_3r_price"],
                trade_data["target_5r_price"], trade_data["target_10r_price"], trade_data["target_20r_price"],
                trade_data["current_mfe"], trade_data["trade_status"], trade_data["active_trade"],
                trade_data["auto_populated"]
            ))
            
            trade_id = cursor.fetchone()[0]
            self.db.conn.commit()
            
            return trade_id
            
        except Exception as e:
            logger.error(f"❌ Database insertion error: {e}")
            self.db.conn.rollback()
            return None
    
    def _start_mfe_monitoring(self, trade_id, trade_data):
        """Start real-time MFE monitoring for the trade"""
        logger.info(f"📊 Starting MFE monitoring for trade {trade_id}")
        # This would integrate with real-time price feeds
        # For now, we'll create a placeholder entry in the monitoring system
        pass

# Test the automated processor
def test_automated_processor():
    """Test the automated signal processor"""
    print("🧪 TESTING AUTOMATED SIGNAL PROCESSOR")
    print("=" * 50)
    
    processor = AutomatedSignalProcessor()
    
    # Test bullish signal
    bullish_signal = {
        "type": "Bullish",
        "symbol": "NQ1!",
        "timestamp": "2025-10-25T14:30:00Z",
        "price": 20000.00,
        "session": "NY PM"
    }
    
    print("📈 Testing bullish signal...")
    result = processor.process_tradingview_signal(bullish_signal)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test bearish signal
    bearish_signal = {
        "type": "Bearish",
        "symbol": "NQ1!",
        "timestamp": "2025-10-25T14:35:00Z",
        "price": 20050.00,
        "session": "NY PM"
    }
    
    print("\n📉 Testing bearish signal...")
    result = processor.process_tradingview_signal(bearish_signal)
    print(f"Result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    test_automated_processor()
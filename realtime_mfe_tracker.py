#!/usr/bin/env python3
"""
Real-Time MFE Tracker - Monitor active V2 trades and update MFE in real-time
The foundation for capturing those big 20R trend moves!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.railway_db import RailwayDB
import time
import logging
from datetime import datetime, timezone
import json
import threading

logger = logging.getLogger(__name__)

class RealtimeMFETracker:
    def __init__(self):
        self.db = RailwayDB()
        self.running = False
        self.update_interval = 5  # Update every 5 seconds
        
    def start_monitoring(self):
        """Start real-time MFE monitoring for all active trades"""
        logger.info("🚀 Starting Real-Time MFE Tracker")
        self.running = True
        
        while self.running:
            try:
                active_trades = self._get_active_trades()
                
                if active_trades:
                    logger.info(f"📊 Monitoring {len(active_trades)} active trades")
                    
                    for trade in active_trades:
                        self._update_trade_mfe(trade)
                        self._check_trade_targets(trade)
                        self._check_stop_loss(trade)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"❌ MFE tracking error: {e}")
                time.sleep(self.update_interval)
    
    def stop_monitoring(self):
        """Stop MFE monitoring"""
        logger.info("⏹️ Stopping Real-Time MFE Tracker")
        self.running = False
    
    def _get_active_trades(self):
        """Get all active V2 trades that need monitoring"""
        try:
            cursor = self.db.conn.cursor()
            
            query = """
            SELECT 
                id, trade_uuid, bias, entry_price, stop_loss_price, risk_distance,
                target_1r_price, target_2r_price, target_3r_price, 
                target_5r_price, target_10r_price, target_20r_price,
                current_mfe, trade_status, created_at
            FROM signal_lab_v2_trades 
            WHERE active_trade = true 
            AND trade_status IN ('active', 'pending')
            ORDER BY created_at DESC;
            """
            
            cursor.execute(query)
            trades = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, trade)) for trade in trades]
            
        except Exception as e:
            logger.error(f"❌ Error fetching active trades: {e}")
            return []
    
    def _get_current_price(self, symbol="NQ1!"):
        """
        Get current market price for the symbol
        
        In production, this would connect to:
        - TradingView real-time data
        - Broker API (Interactive Brokers, etc.)
        - Market data provider
        
        For now, we'll simulate price movement
        """
        # Simulate realistic NASDAQ price movement
        import random
        base_price = 20000.00
        
        # Simulate price with small random movements
        price_change = random.uniform(-50, 50)  # ±50 points movement
        current_price = base_price + price_change
        
        return round(current_price, 2)
    
    def _calculate_current_mfe(self, trade, current_price):
        """Calculate current MFE based on trade direction and current price"""
        entry_price = float(trade['entry_price'])
        risk_distance = float(trade['risk_distance'])
        bias = trade['bias']
        
        if bias == "Bullish":
            # For bullish trades, MFE is positive when price goes up
            price_movement = current_price - entry_price
        else:  # Bearish
            # For bearish trades, MFE is positive when price goes down
            price_movement = entry_price - current_price
        
        # Calculate MFE in R-multiples
        if risk_distance > 0:
            mfe = price_movement / risk_distance
        else:
            mfe = 0.0
        
        # MFE can't be negative (that would be drawdown)
        return max(0.0, round(mfe, 2))
    
    def _update_trade_mfe(self, trade):
        """Update the current MFE for a trade"""
        try:
            current_price = self._get_current_price(trade.get('symbol', 'NQ1!'))
            new_mfe = self._calculate_current_mfe(trade, current_price)
            
            # Only update if MFE has increased (new high)
            current_mfe = float(trade.get('current_mfe', 0))
            
            if new_mfe > current_mfe:
                cursor = self.db.conn.cursor()
                
                update_sql = """
                UPDATE signal_lab_v2_trades 
                SET current_mfe = %s, updated_at = NOW()
                WHERE id = %s;
                """
                
                cursor.execute(update_sql, (new_mfe, trade['id']))
                self.db.conn.commit()
                
                logger.info(f"📈 Trade {trade['trade_uuid'][:8]} - New MFE High: {new_mfe}R (was {current_mfe}R)")
                
                # Check for significant milestones
                self._check_mfe_milestones(trade, new_mfe, current_mfe)
        
        except Exception as e:
            logger.error(f"❌ MFE update error for trade {trade.get('id')}: {e}")
    
    def _check_mfe_milestones(self, trade, new_mfe, previous_mfe):
        """Check if trade hit significant MFE milestones"""
        milestones = [1, 2, 3, 5, 10, 15, 20]
        
        for milestone in milestones:
            if previous_mfe < milestone <= new_mfe:
                logger.info(f"🎯 MILESTONE HIT! Trade {trade['trade_uuid'][:8]} reached {milestone}R!")
                
                # Log milestone achievement
                self._log_milestone_achievement(trade, milestone, new_mfe)
                
                # Special celebration for big moves
                if milestone >= 10:
                    logger.info(f"💎 BIG TREND MOVE! {milestone}R - This is what we're built for!")
    
    def _check_trade_targets(self, trade):
        """Check if trade has hit any R-targets"""
        current_mfe = float(trade.get('current_mfe', 0))
        
        # Check major targets
        targets = {
            1: trade.get('target_1r_price'),
            2: trade.get('target_2r_price'), 
            3: trade.get('target_3r_price'),
            5: trade.get('target_5r_price'),
            10: trade.get('target_10r_price'),
            20: trade.get('target_20r_price')
        }
        
        for r_multiple, target_price in targets.items():
            if target_price and current_mfe >= r_multiple:
                logger.info(f"🎯 Target Hit! Trade {trade['trade_uuid'][:8]} hit {r_multiple}R target at ${target_price}")
    
    def _check_stop_loss(self, trade):
        """Check if trade should be stopped out"""
        current_price = self._get_current_price()
        stop_loss_price = float(trade['stop_loss_price'])
        bias = trade['bias']
        
        should_stop = False
        
        if bias == "Bullish" and current_price <= stop_loss_price:
            should_stop = True
        elif bias == "Bearish" and current_price >= stop_loss_price:
            should_stop = True
        
        if should_stop:
            self._close_trade(trade, "stop_loss", current_price)
    
    def _close_trade(self, trade, reason, exit_price):
        """Close a trade and finalize MFE"""
        try:
            cursor = self.db.conn.cursor()
            
            # Calculate final MFE
            final_mfe = trade.get('current_mfe', 0)
            
            update_sql = """
            UPDATE signal_lab_v2_trades 
            SET 
                active_trade = false,
                trade_status = %s,
                final_mfe = %s,
                updated_at = NOW()
            WHERE id = %s;
            """
            
            cursor.execute(update_sql, (reason, final_mfe, trade['id']))
            self.db.conn.commit()
            
            logger.info(f"🏁 Trade Closed! {trade['trade_uuid'][:8]} - Reason: {reason}, Final MFE: {final_mfe}R")
            
        except Exception as e:
            logger.error(f"❌ Trade closure error: {e}")
    
    def _log_milestone_achievement(self, trade, milestone, mfe):
        """Log milestone achievements for analysis"""
        try:
            # This could be expanded to create detailed milestone tracking
            logger.info(f"📊 Milestone Log: Trade {trade['id']} - {milestone}R at {datetime.now()}")
        except Exception as e:
            logger.error(f"❌ Milestone logging error: {e}")
    
    def get_monitoring_stats(self):
        """Get current monitoring statistics"""
        try:
            cursor = self.db.conn.cursor()
            
            stats_query = """
            SELECT 
                COUNT(*) as total_active,
                AVG(current_mfe) as avg_mfe,
                MAX(current_mfe) as max_mfe,
                COUNT(CASE WHEN current_mfe >= 1 THEN 1 END) as above_1r,
                COUNT(CASE WHEN current_mfe >= 5 THEN 1 END) as above_5r,
                COUNT(CASE WHEN current_mfe >= 10 THEN 1 END) as above_10r
            FROM signal_lab_v2_trades 
            WHERE active_trade = true;
            """
            
            cursor.execute(stats_query)
            result = cursor.fetchone()
            
            if result:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, result))
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Stats query error: {e}")
            return {}

# Background monitoring service
class MFEMonitoringService:
    def __init__(self):
        self.tracker = RealtimeMFETracker()
        self.thread = None
    
    def start_service(self):
        """Start MFE monitoring as background service"""
        if self.thread and self.thread.is_alive():
            logger.warning("⚠️ MFE monitoring already running")
            return
        
        self.thread = threading.Thread(target=self.tracker.start_monitoring, daemon=True)
        self.thread.start()
        logger.info("🚀 MFE Monitoring Service started in background")
    
    def stop_service(self):
        """Stop MFE monitoring service"""
        self.tracker.stop_monitoring()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ MFE Monitoring Service stopped")
    
    def get_status(self):
        """Get service status"""
        return {
            "running": self.tracker.running,
            "thread_alive": self.thread.is_alive() if self.thread else False,
            "stats": self.tracker.get_monitoring_stats()
        }

# Test the MFE tracker
def test_mfe_tracker():
    """Test the MFE tracking system"""
    print("🧪 TESTING REAL-TIME MFE TRACKER")
    print("=" * 50)
    
    tracker = RealtimeMFETracker()
    
    # Get active trades
    active_trades = tracker._get_active_trades()
    print(f"📊 Found {len(active_trades)} active trades")
    
    if active_trades:
        for trade in active_trades[:3]:  # Test first 3 trades
            print(f"\n📈 Testing trade {trade['trade_uuid'][:8]}:")
            print(f"   Entry: ${trade['entry_price']}, Current MFE: {trade['current_mfe']}R")
            
            # Simulate price update
            current_price = tracker._get_current_price()
            new_mfe = tracker._calculate_current_mfe(trade, current_price)
            print(f"   Simulated price: ${current_price}, Calculated MFE: {new_mfe}R")
    
    # Get monitoring stats
    stats = tracker.get_monitoring_stats()
    print(f"\n📊 Monitoring Stats: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    test_mfe_tracker()
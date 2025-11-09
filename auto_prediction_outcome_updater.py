"""
Automatic Prediction Outcome Updater
Monitors signal lab trades and automatically updates prediction outcomes
"""

import logging
from datetime import datetime, timedelta
import threading
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AutoPredictionOutcomeUpdater:
    """Automatically updates prediction outcomes based on completed trades"""
    
    def __init__(self, db, prediction_tracker):
        self.db = db
        self.prediction_tracker = prediction_tracker
        self.running = False
        self.update_thread = None
        
    def start_monitoring(self):
        """Start monitoring for completed trades"""
        if self.running:
            return
            
        self.running = True
        self.update_thread = threading.Thread(target=self._monitor_completed_trades, daemon=True)
        self.update_thread.start()
        logger.info("✅ Auto prediction outcome updater started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
    
    def _monitor_completed_trades(self):
        """Monitor for completed trades and update predictions"""
        while self.running:
            try:
                self._check_and_update_outcomes()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in prediction outcome monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _check_and_update_outcomes(self):
        """Check for completed trades and update corresponding predictions"""
        try:
            cursor = self.db.conn.cursor()
            
            # Find completed trades that haven't been processed for prediction outcomes
            cursor.execute("""
                SELECT slt.*, ls.id as signal_id
                FROM signal_lab_trades slt
                JOIN live_signals ls ON (
                    ls.symbol = 'NQ1!' AND 
                    ls.bias = slt.bias AND
                    ls.timestamp::date = slt.date AND
                    ABS(EXTRACT(EPOCH FROM (ls.timestamp::time - slt.time::time))) < 300
                )
                WHERE slt.active_trade = false 
                AND slt.created_at > NOW() - INTERVAL '1 hour'
                AND slt.mfe IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM prediction_accuracy_tracking pat 
                    WHERE pat.signal_id = ls.id AND pat.actual_outcome IS NOT NULL
                )
                ORDER BY slt.created_at DESC
                LIMIT 10
            """)
            
            completed_trades = cursor.fetchall()
            
            for trade in completed_trades:
                self._update_prediction_from_trade(trade)
                
        except Exception as e:
            logger.error(f"Error checking completed trades: {e}")
    
    def _update_prediction_from_trade(self, trade):
        """Update prediction outcome based on completed trade"""
        try:
            signal_id = trade['signal_id']
            
            # Determine outcome based on MFE
            mfe = float(trade['mfe']) if trade['mfe'] else 0.0
            outcome = 'Success' if mfe >= 1.0 else 'Failure'
            
            # Determine targets hit
            targets_hit = {
                '1R': mfe >= 1.0,
                '2R': mfe >= 2.0,
                '3R': mfe >= 3.0
            }
            
            # Check for specific target columns
            if trade.get('mfe1') is not None:
                targets_hit['1R'] = float(trade['mfe1']) >= 1.0
            if trade.get('mfe2') is not None:
                targets_hit['2R'] = float(trade['mfe2']) >= 2.0
            if trade.get('mfe3') is not None:
                targets_hit['3R'] = float(trade['mfe3']) >= 3.0
            
            # Update prediction outcome
            actual_data = {
                'outcome': outcome,
                'mfe': mfe,
                'targets_hit': targets_hit
            }
            
            self.prediction_tracker.update_actual_outcome(signal_id, actual_data)
            
            logger.info(f"📊 Auto-updated prediction outcome: Signal {signal_id} - {outcome} ({mfe:.2f}R)")
            
        except Exception as e:
            logger.error(f"Error updating prediction from trade: {e}")
    
    def manual_update_prediction(self, signal_id: int, outcome_data: Dict):
        """Manually update a prediction outcome"""
        try:
            self.prediction_tracker.update_actual_outcome(signal_id, outcome_data)
            logger.info(f"📊 Manually updated prediction: Signal {signal_id}")
            return True
        except Exception as e:
            logger.error(f"Error manually updating prediction: {e}")
            return False
    
    def get_pending_predictions(self) -> list:
        """Get predictions that are pending outcome updates"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT pat.*, ls.symbol, ls.bias, ls.price, ls.timestamp as signal_timestamp
                FROM prediction_accuracy_tracking pat
                JOIN live_signals ls ON pat.signal_id = ls.id
                WHERE pat.actual_outcome IS NULL
                AND pat.timestamp > NOW() - INTERVAL '24 hours'
                ORDER BY pat.timestamp DESC
            """)
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting pending predictions: {e}")
            return []
    
    def force_update_stale_predictions(self):
        """Force update predictions that are >4 hours old as 'timeout'"""
        try:
            cursor = self.db.conn.cursor()
            
            # Find stale predictions
            cursor.execute("""
                SELECT prediction_id, signal_id 
                FROM prediction_accuracy_tracking 
                WHERE actual_outcome IS NULL 
                AND timestamp < NOW() - INTERVAL '4 hours'
            """)
            
            stale_predictions = cursor.fetchall()
            
            for pred in stale_predictions:
                # Mark as timeout
                timeout_data = {
                    'outcome': 'Timeout',
                    'mfe': 0.0,
                    'targets_hit': {'1R': False, '2R': False, '3R': False}
                }
                
                self.prediction_tracker.update_actual_outcome(pred['signal_id'], timeout_data)
                logger.warning(f"⏰ Marked stale prediction as timeout: {pred['prediction_id']}")
            
            return len(stale_predictions)
            
        except Exception as e:
            logger.error(f"Error updating stale predictions: {e}")
            return 0
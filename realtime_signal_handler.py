"""
Real-time Signal Handler with WebSocket Integration
Handles instant signal broadcasting and ML predictions
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import threading
import time

logger = logging.getLogger(__name__)

class RealtimeSignalHandler:
    """Handles real-time signal processing and WebSocket broadcasting"""
    
    def __init__(self, socketio, db):
        self.socketio = socketio
        self.db = db
        self.active_connections = 0
        self.last_signal = None
        self.signal_cache = {}
        self.ml_engine = None
        
        # Initialize ML engine if available
        try:
            if db:
                from unified_ml_intelligence import get_unified_ml
                self.ml_engine = get_unified_ml(db)
                logger.info("✅ ML engine initialized for real-time predictions")
        except Exception as e:
            logger.warning(f"ML engine not available for real-time handler: {e}")
    
    def process_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming signal and broadcast to all connected clients"""
        try:
            # Store signal for reference
            self.last_signal = signal_data
            
            # Generate ML prediction if available
            prediction = self._generate_ml_prediction(signal_data)
            
            # Create broadcast payload
            broadcast_data = {
                'type': 'signal_update',
                'signal': signal_data,
                'prediction': prediction,
                'timestamp': datetime.now().isoformat(),
                'session': self._get_current_session(),
                'connections': self.active_connections
            }
            
            # Broadcast to all connected clients
            self._broadcast_signal(broadcast_data)
            
            # Update signal cache for new connections
            self._update_signal_cache(broadcast_data)
            
            logger.info(f"🚀 Signal broadcasted to {self.active_connections} clients: {signal_data.get('symbol')} {signal_data.get('bias')}")
            
            return broadcast_data
            
        except Exception as e:
            logger.error(f"Error processing signal for broadcast: {e}")
            return {}
    
    def _generate_ml_prediction(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate ML prediction for the signal"""
        try:
            if not self.ml_engine:
                return None
            
            # Create feature vector from signal data
            features = {
                'session': signal_data.get('session', 'NY AM'),
                'bias': signal_data.get('bias', 'Bullish'),
                'symbol': signal_data.get('symbol', 'NQ1!'),
                'price': signal_data.get('price', 0),
                'strength': signal_data.get('strength', 50),
                'htf_aligned': signal_data.get('htf_aligned', False)
            }
            
            # Get prediction from ML engine
            prediction_result = self.ml_engine.predict_signal_outcome(features)
            
            if prediction_result and 'error' not in prediction_result:
                # Format prediction for WebSocket
                return {
                    'prediction': prediction_result.get('prediction', 'Unknown'),
                    'confidence': prediction_result.get('confidence', 0),
                    'position_size': self._get_position_size_recommendation(prediction_result.get('confidence', 0)),
                    'multi_target': prediction_result.get('multi_target_predictions', {}),
                    'model_health': prediction_result.get('model_health', 'Unknown')
                }
            
        except Exception as e:
            logger.error(f"Error generating ML prediction: {e}")
        
        return None
    
    def _get_position_size_recommendation(self, confidence: float) -> str:
        """Get position size recommendation based on confidence"""
        if confidence >= 80:
            return "Full Size"
        elif confidence >= 60:
            return "Half Size"
        else:
            return "Skip Trade"
    
    def _broadcast_signal(self, data: Dict[str, Any]):
        """Broadcast signal to all connected WebSocket clients"""
        try:
            if self.active_connections > 0:
                self.socketio.emit('signal_update', data)
                
                # Also emit specific events for different components
                if data.get('prediction'):
                    self.socketio.emit('ml_prediction_update', {
                        'prediction': data['prediction'],
                        'signal': data['signal'],
                        'timestamp': data['timestamp']
                    })
                
                # Emit webhook health update
                self.socketio.emit('webhook_health_update', {
                    'status': 'healthy',
                    'last_signal': data['timestamp'],
                    'signal_type': data['signal'].get('bias', 'Unknown')
                })
                
        except Exception as e:
            logger.error(f"Error broadcasting signal: {e}")
    
    def _update_signal_cache(self, data: Dict[str, Any]):
        """Update signal cache for new connections"""
        self.signal_cache = {
            'last_signal': data,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_current_session(self) -> str:
        """Get current trading session"""
        try:
            from datetime import datetime
            import pytz
            
            ny_tz = pytz.timezone('America/New_York')
            ny_time = datetime.now(ny_tz)
            hour = ny_time.hour
            
            if 0 <= hour < 6:
                return "London"
            elif 6 <= hour < 8:
                return "NY Pre Market"
            elif 8 <= hour < 12:
                return "NY AM"
            elif 12 <= hour < 13:
                return "NY Lunch"
            elif 13 <= hour < 16:
                return "NY PM"
            else:
                return "Asia"
                
        except Exception:
            return "Unknown"
    
    def get_cached_signal(self) -> Optional[Dict[str, Any]]:
        """Get last cached signal for new connections"""
        return self.signal_cache.get('last_signal')
    
    def broadcast_system_health(self, health_data: Dict[str, Any]):
        """Broadcast system health updates"""
        try:
            if self.active_connections > 0:
                self.socketio.emit('system_health_update', {
                    'type': 'health_update',
                    'data': health_data,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error broadcasting health update: {e}")
    
    def broadcast_ml_model_update(self, model_data: Dict[str, Any]):
        """Broadcast ML model updates (retraining, optimization, etc.)"""
        try:
            if self.active_connections > 0:
                self.socketio.emit('ml_model_update', {
                    'type': 'model_update',
                    'data': model_data,
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            logger.error(f"Error broadcasting ML update: {e}")
    
    def start_health_monitor(self):
        """Start background health monitoring"""
        def health_monitor():
            while True:
                try:
                    # Check signal gaps
                    if self.last_signal:
                        time_since_last = (datetime.now() - datetime.fromisoformat(self.last_signal.get('timestamp', datetime.now().isoformat()))).total_seconds()
                        
                        if time_since_last > 300:  # 5 minutes
                            self.socketio.emit('signal_gap_alert', {
                                'type': 'signal_gap',
                                'minutes_since_last': int(time_since_last / 60),
                                'timestamp': datetime.now().isoformat()
                            })
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                    time.sleep(60)
        
        # Start health monitor in background thread
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        health_thread.start()
        logger.info("✅ Real-time health monitor started")
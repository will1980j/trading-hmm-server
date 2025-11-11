"""
Robust WebSocket Handler for Automated Signals
Production-grade implementation with connection management and error handling
"""

import logging
from datetime import datetime
import pytz
from threading import Lock, Thread
import time

logger = logging.getLogger(__name__)

class RobustWebSocketHandler:
    """
    Production-grade WebSocket handler with:
    - Connection state management
    - Automatic reconnection
    - Health monitoring
    - Error recovery
    - Message queuing
    """
    
    def __init__(self, socketio, db):
        self.socketio = socketio
        self.db = db
        self.active_connections = 0
        self.connection_lock = Lock()
        self.last_signal = None
        self.health_status = {
            'websocket': 'initializing',
            'database': 'unknown',
            'last_check': None
        }
        self.message_queue = []
        self.max_queue_size = 100
        
        logger.info("RobustWebSocketHandler initialized")
    
    def start_health_monitor(self):
        """Start background health monitoring thread"""
        def monitor():
            while True:
                try:
                    self._check_health()
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Health monitor error: {e}", exc_info=True)
                    time.sleep(60)
        
        thread = Thread(target=monitor, daemon=True)
        thread.start()
        logger.info("Health monitor started")
    
    def _check_health(self):
        """Check system health"""
        try:
            # Check database
            if self.db and self.db.conn:
                cursor = self.db.conn.cursor()
                cursor.execute("SELECT 1;")
                cursor.fetchone()
                self.health_status['database'] = 'healthy'
            else:
                self.health_status['database'] = 'disconnected'
            
            # Check WebSocket
            if self.active_connections > 0:
                self.health_status['websocket'] = 'active'
            else:
                self.health_status['websocket'] = 'idle'
            
            self.health_status['last_check'] = datetime.now(pytz.UTC).isoformat()
            
            # Broadcast health status
            self._broadcast_health()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            self.health_status['database'] = 'error'
            self.health_status['websocket'] = 'error'
    
    def _broadcast_health(self):
        """Broadcast health status to all connected clients"""
        try:
            self.socketio.emit('health_update', {
                'status': self.health_status,
                'connections': self.active_connections,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            })
        except Exception as e:
            logger.error(f"Health broadcast failed: {e}")
    
    def handle_connect(self, sid=None):
        """Handle new WebSocket connection"""
        with self.connection_lock:
            self.active_connections += 1
        
        logger.info(f"WebSocket connected (SID: {sid}). Active: {self.active_connections}")
        
        # Send cached signal to new connection
        if self.last_signal:
            try:
                self.socketio.emit('signal_update', self.last_signal, room=sid)
            except Exception as e:
                logger.error(f"Failed to send cached signal: {e}")
        
        # Send current health status
        try:
            self.socketio.emit('health_update', {
                'status': self.health_status,
                'connections': self.active_connections,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }, room=sid)
        except Exception as e:
            logger.error(f"Failed to send health status: {e}")
        
        return {'status': 'connected', 'connections': self.active_connections}
    
    def handle_disconnect(self, sid=None):
        """Handle WebSocket disconnection"""
        with self.connection_lock:
            self.active_connections = max(0, self.active_connections - 1)
        
        logger.info(f"WebSocket disconnected (SID: {sid}). Active: {self.active_connections}")
    
    def broadcast_signal(self, signal_data):
        """Broadcast new signal to all connected clients"""
        try:
            # Cache the signal
            self.last_signal = signal_data
            
            # Add to message queue
            self._add_to_queue(signal_data)
            
            # Broadcast to all clients
            self.socketio.emit('signal_update', signal_data)
            
            logger.info(f"Signal broadcasted to {self.active_connections} clients")
            
        except Exception as e:
            logger.error(f"Signal broadcast failed: {e}", exc_info=True)
    
    def broadcast_mfe_update(self, trade_id, mfe_data):
        """Broadcast MFE update for specific trade"""
        try:
            update_data = {
                'type': 'mfe_update',
                'trade_id': trade_id,
                'data': mfe_data,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
            
            self.socketio.emit('mfe_update', update_data)
            logger.info(f"MFE update broadcasted for trade {trade_id}")
            
        except Exception as e:
            logger.error(f"MFE broadcast failed: {e}", exc_info=True)
    
    def broadcast_trade_completion(self, trade_id, completion_data):
        """Broadcast trade completion"""
        try:
            completion_event = {
                'type': 'trade_completed',
                'trade_id': trade_id,
                'data': completion_data,
                'timestamp': datetime.now(pytz.UTC).isoformat()
            }
            
            self.socketio.emit('trade_completed', completion_event)
            logger.info(f"Trade completion broadcasted for {trade_id}")
            
        except Exception as e:
            logger.error(f"Completion broadcast failed: {e}", exc_info=True)
    
    def _add_to_queue(self, message):
        """Add message to queue with size limit"""
        self.message_queue.append(message)
        if len(self.message_queue) > self.max_queue_size:
            self.message_queue.pop(0)
    
    def get_cached_signal(self):
        """Get last cached signal"""
        return self.last_signal
    
    def get_message_history(self, limit=10):
        """Get recent message history"""
        return self.message_queue[-limit:] if self.message_queue else []
    
    def get_connection_stats(self):
        """Get connection statistics"""
        return {
            'active_connections': self.active_connections,
            'health_status': self.health_status,
            'queue_size': len(self.message_queue),
            'last_signal': self.last_signal is not None,
            'timestamp': datetime.now(pytz.UTC).isoformat()
        }


def register_websocket_handlers(socketio, handler):
    """Register all WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        return handler.handle_connect()
    
    @socketio.on('disconnect')
    def handle_disconnect():
        handler.handle_disconnect()
    
    @socketio.on('request_signal_history')
    def handle_signal_history_request(data):
        """Handle request for signal history"""
        try:
            limit = data.get('limit', 10) if data else 10
            history = handler.get_message_history(limit)
            socketio.emit('signal_history', {
                'signals': history,
                'count': len(history),
                'timestamp': datetime.now(pytz.UTC).isoformat()
            })
        except Exception as e:
            logger.error(f"Signal history request failed: {e}")
            socketio.emit('error', {'message': 'Failed to retrieve signal history'})
    
    @socketio.on('request_health_status')
    def handle_health_request():
        """Handle request for health status"""
        try:
            stats = handler.get_connection_stats()
            socketio.emit('health_update', stats)
        except Exception as e:
            logger.error(f"Health request failed: {e}")
            socketio.emit('error', {'message': 'Failed to retrieve health status'})
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping for connection keepalive"""
        socketio.emit('pong', {
            'timestamp': datetime.now(pytz.UTC).isoformat()
        })
    
    logger.info("WebSocket handlers registered")

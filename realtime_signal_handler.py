"""Real-time Signal WebSocket Handler"""
from flask_socketio import emit
from datetime import datetime

class RealtimeSignalHandler:
    def __init__(self, socketio, db):
        self.socketio = socketio
        self.db = db
        self.active_connections = 0
        
    def broadcast_signal_update(self, signal_data):
        """Broadcast signal update to all connected clients"""
        try:
            self.socketio.emit('signal_update', signal_data, namespace='/')
            return True
        except Exception as e:
            print(f"Broadcast error: {e}")
            return False
    
    def broadcast_prediction_update(self, prediction_data):
        """Broadcast ML prediction update"""
        try:
            self.socketio.emit('prediction_update', prediction_data, namespace='/')
            return True
        except Exception as e:
            print(f"Prediction broadcast error: {e}")
            return False
    
    def get_connection_count(self):
        """Get active connection count"""
        return self.active_connections

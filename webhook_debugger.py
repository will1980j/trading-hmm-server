"""Webhook Signal Debugging and Monitoring"""
from datetime import datetime
from collections import defaultdict
import json
from db_error_handler import auto_fix_db_errors

class WebhookDebugger:
    def __init__(self, db):
        self.db = db
        self.signal_counters = defaultdict(int)
        self.last_signals = {'Bullish': None, 'Bearish': None}
        
    @auto_fix_db_errors
    def log_webhook_request(self, raw_data, parsed_data, source='TradingView'):
        """Log all incoming webhook requests"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO webhook_debug_log 
                (raw_payload, parsed_data, source, received_at)
                VALUES (%s, %s, %s, NOW())
            """, (raw_data, json.dumps(parsed_data) if parsed_data else None, source))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Webhook log error: {e}")
            return False
    
    @auto_fix_db_errors
    def log_signal_processing(self, signal_data, status, error_msg=None):
        """Log signal processing results"""
        try:
            bias = signal_data.get('bias', 'Unknown')
            self.signal_counters[f'{bias}_received'] += 1
            
            if status == 'success':
                self.signal_counters[f'{bias}_processed'] += 1
                self.last_signals[bias] = datetime.now()
            else:
                self.signal_counters[f'{bias}_failed'] += 1
            
            cursor = self.db.conn.cursor()
            cursor.execute("""
                INSERT INTO signal_processing_log 
                (bias, symbol, price, status, error_message, processed_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                bias,
                signal_data.get('symbol', 'Unknown'),
                signal_data.get('price', 0),
                status,
                error_msg
            ))
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"Signal processing log error: {e}")
            return False
    
    @auto_fix_db_errors
    def get_signal_stats(self):
        """Get signal reception statistics"""
        try:
            cursor = self.db.conn.cursor()
            
            # Last 24 hours stats
            cursor.execute("""
                SELECT 
                    bias,
                    COUNT(*) as count,
                    MAX(processed_at) as last_received
                FROM signal_processing_log
                WHERE processed_at > NOW() - INTERVAL '24 hours'
                GROUP BY bias
            """)
            
            stats = cursor.fetchall()
            
            return {
                'last_24h': [dict(row) for row in stats],
                'counters': dict(self.signal_counters),
                'last_bullish': self.last_signals['Bullish'].isoformat() if self.last_signals['Bullish'] else None,
                'last_bearish': self.last_signals['Bearish'].isoformat() if self.last_signals['Bearish'] else None
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {'error': str(e)}
    
    @auto_fix_db_errors
    def check_signal_health(self):
        """Check if both signal types are being received"""
        try:
            cursor = self.db.conn.cursor()
            
            # Check last hour
            cursor.execute("""
                SELECT 
                    bias,
                    COUNT(*) as count
                FROM signal_processing_log
                WHERE processed_at > NOW() - INTERVAL '1 hour'
                AND status = 'success'
                GROUP BY bias
            """)
            
            recent = {row['bias']: row['count'] for row in cursor.fetchall()}
            
            alerts = []
            if recent.get('Bullish', 0) > 0 and recent.get('Bearish', 0) == 0:
                alerts.append({
                    'type': 'missing_bearish',
                    'message': 'No bearish signals received in last hour',
                    'severity': 'warning'
                })
            elif recent.get('Bearish', 0) > 0 and recent.get('Bullish', 0) == 0:
                alerts.append({
                    'type': 'missing_bullish',
                    'message': 'No bullish signals received in last hour',
                    'severity': 'warning'
                })
            
            return {
                'healthy': len(alerts) == 0,
                'alerts': alerts,
                'recent_signals': recent
            }
        except Exception as e:
            return {'healthy': False, 'error': str(e)}
    
    def get_webhook_failures(self, limit=20):
        """Get recent webhook failures"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT bias, symbol, price, error_message, processed_at
                FROM signal_processing_log
                WHERE status = 'failed'
                ORDER BY processed_at DESC
                LIMIT %s
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            return []

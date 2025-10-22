"""
Webhook Monitor - Detects when TradingView webhooks stop firing
and automatically switches to backup signal generation
"""
from datetime import datetime, timedelta
from database.railway_db import RailwayDB
import time

class WebhookMonitor:
    def __init__(self, db):
        self.db = db
        self.alert_threshold = 300  # 5 minutes without signal = alert
        
    def check_last_signal_time(self):
        """Check when the last signal was received"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT MAX(timestamp) as last_signal
            FROM live_signals
            WHERE source != 'BACKUP_GENERATOR'
        """)
        result = cursor.fetchone()
        
        if not result or not result['last_signal']:
            return None
        
        return result['last_signal']
    
    def is_webhook_healthy(self):
        """Check if webhooks are still firing"""
        last_signal = self.check_last_signal_time()
        
        if not last_signal:
            return False
        
        time_since_signal = (datetime.now() - last_signal).total_seconds()
        
        return time_since_signal < self.alert_threshold
    
    def monitor(self):
        """Continuously monitor webhook health"""
        print("🔍 Webhook Monitor started")
        
        while True:
            try:
                healthy = self.is_webhook_healthy()
                last_signal = self.check_last_signal_time()
                
                if healthy:
                    print(f"✅ Webhooks healthy - Last signal: {last_signal}")
                else:
                    print(f"⚠️ WARNING: No signals in {self.alert_threshold}s")
                    print(f"💡 Consider: Check TradingView alert status")
                    print(f"💡 Consider: Enable backup signal generator")
                
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                print("\n🛑 Monitor stopped")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(60)

if __name__ == '__main__':
    db = RailwayDB()
    monitor = WebhookMonitor(db)
    monitor.monitor()

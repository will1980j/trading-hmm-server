"""Real-time Webhook Log Viewer"""
import time
from database.railway_db import RailwayDB
from datetime import datetime

def view_webhook_logs(follow=True, limit=20):
    """View webhook logs in real-time"""
    db = RailwayDB()
    last_id = 0
    
    print("=" * 80)
    print("WEBHOOK LOG VIEWER - Press Ctrl+C to exit")
    print("=" * 80)
    print()
    
    try:
        while True:
            cursor = db.conn.cursor()
            
            if follow:
                # Get new logs since last check
                cursor.execute("""
                    SELECT id, raw_payload, source, received_at
                    FROM webhook_debug_log
                    WHERE id > %s
                    ORDER BY id ASC
                """, (last_id,))
            else:
                # Get last N logs
                cursor.execute("""
                    SELECT id, raw_payload, source, received_at
                    FROM webhook_debug_log
                    ORDER BY id DESC
                    LIMIT %s
                """, (limit,))
            
            logs = cursor.fetchall()
            
            for log in logs:
                timestamp = log['received_at'].strftime('%Y-%m-%d %H:%M:%S')
                payload = log['raw_payload'][:200] if log['raw_payload'] else 'Empty'
                
                # Extract bias if present
                bias = 'Unknown'
                if 'Bullish' in payload:
                    bias = '🟢 Bullish'
                elif 'Bearish' in payload:
                    bias = '🔴 Bearish'
                
                print(f"[{timestamp}] {bias} | {log['source']}")
                print(f"  Payload: {payload}")
                print()
                
                last_id = max(last_id, log['id'])
            
            if not follow:
                break
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\nLog viewer stopped")
    except Exception as e:
        print(f"Error: {str(e)}")

def view_signal_processing_logs(limit=20):
    """View signal processing logs"""
    db = RailwayDB()
    
    print("=" * 80)
    print("SIGNAL PROCESSING LOG")
    print("=" * 80)
    print()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT bias, symbol, price, status, error_message, processed_at
            FROM signal_processing_log
            ORDER BY processed_at DESC
            LIMIT %s
        """, (limit,))
        
        logs = cursor.fetchall()
        
        for log in logs:
            timestamp = log['processed_at'].strftime('%Y-%m-%d %H:%M:%S')
            bias_icon = '🟢' if log['bias'] == 'Bullish' else '🔴'
            status_icon = '✅' if log['status'] == 'success' else '❌'
            
            print(f"[{timestamp}] {status_icon} {bias_icon} {log['bias']} | {log['symbol']} @ {log['price']}")
            
            if log['error_message']:
                print(f"  Error: {log['error_message']}")
            
            print()
            
    except Exception as e:
        print(f"Error: {str(e)}")

def show_signal_stats():
    """Show signal statistics"""
    db = RailwayDB()
    
    print("=" * 80)
    print("SIGNAL STATISTICS (Last 24 Hours)")
    print("=" * 80)
    print()
    
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT 
                bias,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                MAX(processed_at) as last_signal
            FROM signal_processing_log
            WHERE processed_at > NOW() - INTERVAL '24 hours'
            GROUP BY bias
        """)
        
        stats = cursor.fetchall()
        
        for stat in stats:
            bias_icon = '🟢' if stat['bias'] == 'Bullish' else '🔴'
            success_rate = (stat['successful'] / stat['total'] * 100) if stat['total'] > 0 else 0
            
            print(f"{bias_icon} {stat['bias']}:")
            print(f"  Total: {stat['total']}")
            print(f"  Successful: {stat['successful']}")
            print(f"  Failed: {stat['failed']}")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Last Signal: {stat['last_signal'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'follow':
            view_webhook_logs(follow=True)
        elif command == 'recent':
            view_webhook_logs(follow=False, limit=20)
        elif command == 'processing':
            view_signal_processing_logs(limit=20)
        elif command == 'stats':
            show_signal_stats()
        else:
            print("Usage:")
            print("  python webhook_log_viewer.py follow      - Follow webhook logs in real-time")
            print("  python webhook_log_viewer.py recent      - Show recent webhook logs")
            print("  python webhook_log_viewer.py processing  - Show signal processing logs")
            print("  python webhook_log_viewer.py stats       - Show signal statistics")
    else:
        print("Webhook Log Viewer")
        print("=" * 80)
        print()
        print("Commands:")
        print("  python webhook_log_viewer.py follow      - Follow webhook logs in real-time")
        print("  python webhook_log_viewer.py recent      - Show recent webhook logs")
        print("  python webhook_log_viewer.py processing  - Show signal processing logs")
        print("  python webhook_log_viewer.py stats       - Show signal statistics")
        print()
        print("Example: python webhook_log_viewer.py follow")

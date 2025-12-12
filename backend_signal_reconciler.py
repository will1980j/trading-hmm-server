"""
Backend Signal Reconciliation Service
Fills MFE/MAE gaps for signals not tracked by indicator
Runs continuously in background every 2 minutes
"""

import psycopg2
import os
import time
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import threading

load_dotenv()

class BackendReconciler:
    """Reconciles orphaned signals by calculating MFE/MAE from database"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.running = False
        
    def get_current_nq_price(self):
        """Get current NQ price (fallback to last known price from database)"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Get most recent price from any MFE_UPDATE
            cur.execute("""
                SELECT be_mfe, no_be_mfe, entry_price, stop_loss, direction
                FROM automated_signals
                WHERE event_type = 'MFE_UPDATE'
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cur.fetchone()
            if row:
                # Reverse calculate price from MFE
                be_mfe, no_be_mfe, entry, stop, direction = row
                risk = abs(float(entry) - float(stop))
                
                if direction in ['Bullish', 'LONG']:
                    # Price = entry + (MFE * risk)
                    current_price = float(entry) + (float(no_be_mfe) * risk)
                else:
                    # Price = entry - (MFE * risk)
                    current_price = float(entry) - (float(no_be_mfe) * risk)
                
                cur.close()
                conn.close()
                return current_price
            
            cur.close()
            conn.close()
            return None
            
        except Exception as e:
            print(f"Error getting current price: {e}")
            return None
    
    def find_orphaned_signals(self):
        """Find signals with no MFE update in last 2 minutes"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Find active signals with no recent MFE_UPDATE
            cur.execute("""
                SELECT 
                    e.trade_id,
                    e.entry_price,
                    e.stop_loss,
                    e.direction,
                    e.signal_date,
                    e.signal_time,
                    e.session,
                    MAX(m.timestamp) as last_mfe_update
                FROM automated_signals e
                LEFT JOIN automated_signals m ON m.trade_id = e.trade_id AND m.event_type = 'MFE_UPDATE'
                WHERE e.event_type = 'ENTRY'
                AND e.entry_price IS NOT NULL
                AND e.stop_loss IS NOT NULL
                AND e.trade_id NOT IN (
                    SELECT DISTINCT trade_id 
                    FROM automated_signals 
                    WHERE event_type LIKE 'EXIT_%'
                )
                GROUP BY e.trade_id, e.entry_price, e.stop_loss, e.direction, e.signal_date, e.signal_time, e.session
                HAVING MAX(m.timestamp) IS NULL OR MAX(m.timestamp) < NOW() - INTERVAL '2 minutes'
                ORDER BY e.timestamp DESC
            """)
            
            orphaned = cur.fetchall()
            cur.close()
            conn.close()
            
            return orphaned
            
        except Exception as e:
            print(f"Error finding orphaned signals: {e}")
            return []
    
    def calculate_mfe_mae(self, entry_price, stop_loss, direction, current_price):
        """Calculate MFE and MAE from entry/stop/current price"""
        try:
            entry = float(entry_price)
            stop = float(stop_loss)
            price = float(current_price)
            risk = abs(entry - stop)
            
            if risk == 0:
                return 0.0, 0.0, 0.0
            
            if direction in ['Bullish', 'LONG']:
                # MFE: How far price moved favorably from entry
                mfe = (price - entry) / risk
                # MAE: Assume worst case (hit stop) for historical
                mae = (stop - entry) / risk  # Will be negative
                # BE MFE: Same as No-BE for now (we don't know if BE triggered)
                be_mfe = mfe
            else:
                # MFE: How far price moved favorably from entry
                mfe = (entry - price) / risk
                # MAE: Assume worst case (hit stop) for historical
                mae = (entry - stop) / risk  # Will be negative
                # BE MFE: Same as No-BE for now
                be_mfe = mfe
            
            return be_mfe, mfe, mae
            
        except Exception as e:
            print(f"Error calculating MFE/MAE: {e}")
            return 0.0, 0.0, 0.0
    
    def reconcile_signal(self, trade_id, entry_price, stop_loss, direction, current_price):
        """Insert calculated MFE_UPDATE for orphaned signal"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Calculate MFE/MAE
            be_mfe, no_be_mfe, mae = self.calculate_mfe_mae(entry_price, stop_loss, direction, current_price)
            
            # Parse trade_id for timestamp
            parts = trade_id.split('_')
            if len(parts) >= 2:
                date_str = parts[0]  # YYYYMMDD
                time_str = parts[1][:6]  # HHMMSS
                
                # Build timestamp
                import pytz
                ny_tz = pytz.timezone('America/New_York')
                signal_dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                signal_dt = ny_tz.localize(signal_dt)
                utc_dt = signal_dt.astimezone(pytz.UTC)
                
                signal_date = signal_dt.strftime('%Y-%m-%d')
                signal_time = signal_dt.strftime('%H:%M:%S')
            else:
                utc_dt = datetime.utcnow()
                signal_date = None
                signal_time = None
            
            # Insert reconciled MFE_UPDATE
            cur.execute("""
                INSERT INTO automated_signals (
                    trade_id, event_type, timestamp,
                    be_mfe, no_be_mfe, mae_global_r,
                    signal_date, signal_time,
                    data_source, confidence_score,
                    reconciliation_timestamp, reconciliation_reason,
                    raw_payload
                ) VALUES (
                    %s, 'MFE_UPDATE', %s,
                    %s, %s, %s,
                    %s, %s,
                    'backend_calculated', 0.7,
                    NOW(), 'orphaned_signal_reconciliation',
                    %s
                )
            """, (
                trade_id, utc_dt,
                be_mfe, no_be_mfe, mae,
                signal_date, signal_time,
                json.dumps({
                    'trade_id': trade_id,
                    'be_mfe': be_mfe,
                    'no_be_mfe': no_be_mfe,
                    'mae_global_r': mae,
                    'current_price': current_price,
                    'reconciled': True
                })
            ))
            
            # Log to audit trail
            cur.execute("""
                INSERT INTO sync_audit_log (
                    trade_id, action_type, data_source,
                    fields_filled, confidence_score, success
                ) VALUES (
                    %s, 'gap_filled', 'backend_calculated',
                    %s, 0.7, TRUE
                )
            """, (
                trade_id,
                json.dumps({'be_mfe': True, 'no_be_mfe': True, 'mae': True})
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error reconciling {trade_id}: {e}")
            return False
    
    def reconciliation_cycle(self):
        """Run one reconciliation cycle"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Starting reconciliation cycle...")
        
        # Get current price
        current_price = self.get_current_nq_price()
        if not current_price:
            print("  ⚠️ Could not determine current price - skipping cycle")
            return
        
        print(f"  Current NQ price: {current_price}")
        
        # Find orphaned signals
        orphaned = self.find_orphaned_signals()
        print(f"  Found {len(orphaned)} orphaned signals")
        
        if not orphaned:
            print("  ✅ No orphaned signals - system healthy")
            return
        
        # Reconcile each signal
        success_count = 0
        for signal_data in orphaned:
            trade_id, entry, stop, direction, sig_date, sig_time, session, last_update = signal_data
            
            if self.reconcile_signal(trade_id, entry, stop, direction, current_price):
                success_count += 1
        
        print(f"  ✅ Reconciled {success_count}/{len(orphaned)} signals")
    
    def run_continuous(self, interval_seconds=120):
        """Run reconciliation continuously"""
        self.running = True
        print("🚀 Backend Reconciliation Service Started")
        print(f"   Interval: {interval_seconds} seconds")
        print()
        
        while self.running:
            try:
                self.reconciliation_cycle()
            except Exception as e:
                print(f"❌ Reconciliation cycle error: {e}")
            
            time.sleep(interval_seconds)
    
    def start_background(self, interval_seconds=120):
        """Start reconciliation in background thread"""
        thread = threading.Thread(target=self.run_continuous, args=(interval_seconds,), daemon=True)
        thread.start()
        return thread

def start_reconciliation_service(interval_seconds=120):
    """Start the backend reconciliation service"""
    reconciler = BackendReconciler()
    return reconciler.start_background(interval_seconds)

if __name__ == "__main__":
    # Run standalone
    reconciler = BackendReconciler()
    reconciler.run_continuous(interval_seconds=120)

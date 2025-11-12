"""
Diagnose MFE calculation issue for stopped-out trades
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Get database connection"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set")
        return None
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def diagnose_mfe_issue():
    """Check stopped-out trades with positive MFE values"""
    conn = get_db_connection()
    if not conn:
        print("❌ Could not connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Get stopped-out trades with positive MFE
        query = """
        SELECT 
            id,
            direction,
            signal_time,
            entry_price,
            stop_loss,
            risk_distance,
            no_be_mfe,
            be_mfe,
            be_triggered,
            be_stopped,
            no_be_stopped
        FROM automated_signals
        WHERE no_be_stopped = true
        AND no_be_mfe > 0.5
        ORDER BY signal_time DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        trades = cursor.fetchall()
        
        print(f"\n🔍 Found {len(trades)} stopped-out trades with MFE > 0.5R:\n")
        
        for trade in trades:
            trade_id, direction, signal_time, entry, stop, risk, no_be_mfe, be_mfe, be_trig, be_stop, no_be_stop = trade
            
            print(f"Trade #{trade_id} - {direction}")
            print(f"  Signal Time: {signal_time}")
            print(f"  Entry: {entry}, Stop: {stop}, Risk: {risk}")
            print(f"  No BE MFE: {no_be_mfe}R (STOPPED OUT)")
            print(f"  BE MFE: {be_mfe}R")
            print(f"  BE Triggered: {be_trig}, BE Stopped: {be_stop}")
            print(f"  ❌ PROBLEM: Trade stopped out but shows {no_be_mfe}R MFE")
            print()
        
        # Check if there are any trades with negative or zero MFE that were stopped out
        query2 = """
        SELECT COUNT(*) 
        FROM automated_signals
        WHERE no_be_stopped = true
        AND no_be_mfe <= 0.0
        """
        cursor.execute(query2)
        zero_mfe_count = cursor.fetchone()[0]
        
        print(f"📊 Trades stopped out with MFE <= 0.0R: {zero_mfe_count}")
        print(f"📊 Trades stopped out with MFE > 0.5R: {len(trades)}")
        print(f"\n💡 Expected: Most stopped-out trades should have MFE <= 0.0R")
        print(f"💡 Reality: Many have positive MFE, indicating the bug is still present")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_mfe_issue()

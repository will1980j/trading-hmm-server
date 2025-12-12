"""
Automatic Cancellation Detection
Detects cancelled signals based on alternation rule without explicit CANCELLED webhooks
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def detect_and_mark_cancelled_signals():
    """
    Detect cancelled signals based on alternation rule:
    - Signals always alternate (Bullish → Bearish → Bullish)
    - If SIGNAL_CREATED has no ENTRY and opposite direction appeared next → CANCELLED
    - NEVER mark as cancelled if ENTRY exists (signal was confirmed)
    """
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Get all SIGNAL_CREATED events in chronological order
        cur.execute("""
            SELECT 
                trade_id,
                direction,
                timestamp,
                -- Check if confirmed (has ENTRY)
                EXISTS(
                    SELECT 1 FROM automated_signals e 
                    WHERE e.trade_id = automated_signals.trade_id 
                    AND e.event_type = 'ENTRY'
                ) as has_entry,
                -- Check if already marked cancelled
                EXISTS(
                    SELECT 1 FROM automated_signals c 
                    WHERE c.trade_id = automated_signals.trade_id 
                    AND c.event_type = 'CANCELLED'
                ) as has_cancelled
            FROM automated_signals
            WHERE event_type = 'SIGNAL_CREATED'
            ORDER BY timestamp ASC
        """)
        
        signals = cur.fetchall()
        cancelled_count = 0
        
        # Process signals in pairs to detect cancellations
        for i in range(len(signals) - 1):
            current = signals[i]
            next_signal = signals[i + 1]
            
            current_id = current[0]
            current_dir = current[1]
            current_has_entry = current[3]
            current_has_cancelled = current[4]
            
            next_dir = next_signal[1]
            
            # PROTECTION: Never mark as cancelled if signal was confirmed (has ENTRY)
            if current_has_entry:
                continue
            
            # PROTECTION: Skip if already marked cancelled
            if current_has_cancelled:
                continue
            
            # CANCELLATION RULE: If next signal is opposite direction, current was cancelled
            if (current_dir == "Bullish" and next_dir == "Bearish") or \
               (current_dir == "Bearish" and next_dir == "Bullish"):
                
                # Insert CANCELLED event
                cur.execute("""
                    INSERT INTO automated_signals (
                        trade_id, event_type, timestamp,
                        direction, 
                        raw_payload,
                        data_source, confidence_score
                    ) VALUES (
                        %s, 'CANCELLED', NOW(),
                        %s,
                        %s,
                        'backend_inferred', 0.95
                    )
                """, (
                    current_id,
                    current_dir,
                    psycopg2.extras.Json({
                        "cancellation_reason": "opposite_signal_appeared",
                        "cancelled_by": next_signal[0],
                        "inferred": True
                    })
                ))
                
                cancelled_count += 1
                logger.info(f"✅ Marked as cancelled: {current_id} (opposite signal {next_signal[0]} appeared)")
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "cancelled_detected": cancelled_count,
            "total_signals_checked": len(signals)
        }
        
    except Exception as e:
        logger.error(f"❌ Cancellation detection error: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Test the cancellation detector
    result = detect_and_mark_cancelled_signals()
    print(f"Cancellation Detection Results:")
    print(f"  Signals checked: {result.get('total_signals_checked')}")
    print(f"  Cancelled detected: {result.get('cancelled_detected')}")

"""
SIGNAL_CREATED Reconciliation Engine
Uses All Signals (SIGNAL_CREATED events) as primary source of truth for gap filling
"""

import psycopg2
import psycopg2.extras
import os
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class SignalCreatedReconciler:
    """
    Tier 0 Reconciliation: Use SIGNAL_CREATED events as source of truth
    This is MORE RELIABLE than indicator polling or backend calculation
    because SIGNAL_CREATED captures the exact moment the triangle appeared
    """
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
    
    def get_signal_created_data(self, trade_id: str) -> Optional[Dict]:
        """
        Get complete data from SIGNAL_CREATED event.
        This is the MOST RELIABLE source - captured at signal moment.
        """
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    trade_id,
                    timestamp,
                    direction,
                    session,
                    signal_date,
                    signal_time,
                    htf_alignment,
                    raw_payload
                FROM automated_signals
                WHERE trade_id = %s
                AND event_type = 'SIGNAL_CREATED'
                LIMIT 1
            """, (trade_id,))
            
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if not row:
                return None
            
            # Parse raw payload for additional data
            import json
            raw_payload = row[7] if row[7] else {}
            if isinstance(raw_payload, str):
                raw_payload = json.loads(raw_payload)
            
            return {
                'trade_id': row[0],
                'timestamp': row[1],
                'direction': row[2],
                'session': row[3],
                'signal_date': row[4],
                'signal_time': row[5],
                'htf_alignment': row[6],
                'raw_payload': raw_payload,
                'confidence': 1.0  # SIGNAL_CREATED is 100% reliable
            }
            
        except Exception as e:
            logger.error(f"Error getting SIGNAL_CREATED data for {trade_id}: {e}")
            return None
    
    def fill_htf_alignment_from_signal_created(self, trade_id: str) -> bool:
        """
        Fill missing HTF alignment using SIGNAL_CREATED event.
        Confidence: 1.0 (perfect - captured at signal moment)
        """
        try:
            signal_data = self.get_signal_created_data(trade_id)
            if not signal_data or not signal_data.get('htf_alignment'):
                return False
            
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Update ENTRY event with HTF alignment from SIGNAL_CREATED
            cur.execute("""
                UPDATE automated_signals
                SET 
                    htf_alignment = %s,
                    data_source = 'reconciled',
                    confidence_score = 1.0,
                    reconciliation_timestamp = NOW(),
                    reconciliation_reason = 'htf_alignment_from_signal_created'
                WHERE trade_id = %s
                AND event_type = 'ENTRY'
                AND (htf_alignment IS NULL OR htf_alignment = '{}')
            """, (
                psycopg2.extras.Json(signal_data['htf_alignment']),
                trade_id
            ))
            
            # Log to audit trail
            cur.execute("""
                INSERT INTO sync_audit_log (
                    trade_id, action_type, data_source,
                    fields_filled, confidence_score, success
                ) VALUES (%s, 'gap_filled_htf_alignment', 'signal_created', %s, 1.0, TRUE)
            """, (
                trade_id,
                psycopg2.extras.Json({'htf_alignment': True})
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Filled HTF alignment from SIGNAL_CREATED for {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fill HTF alignment from SIGNAL_CREATED: {e}")
            return False
    
    def fill_metadata_from_signal_created(self, trade_id: str) -> bool:
        """
        Fill missing metadata (session, signal_date, signal_time) from SIGNAL_CREATED.
        Confidence: 1.0 (perfect - captured at signal moment)
        """
        try:
            signal_data = self.get_signal_created_data(trade_id)
            if not signal_data:
                return False
            
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Update ENTRY event with metadata from SIGNAL_CREATED
            cur.execute("""
                UPDATE automated_signals
                SET 
                    signal_date = COALESCE(signal_date, %s),
                    signal_time = COALESCE(signal_time, %s),
                    session = COALESCE(session, %s),
                    direction = COALESCE(direction, %s),
                    data_source = 'reconciled',
                    confidence_score = 1.0,
                    reconciliation_timestamp = NOW(),
                    reconciliation_reason = 'metadata_from_signal_created'
                WHERE trade_id = %s
                AND event_type = 'ENTRY'
            """, (
                signal_data.get('signal_date'),
                signal_data.get('signal_time'),
                signal_data.get('session'),
                signal_data.get('direction'),
                trade_id
            ))
            
            # Log to audit trail
            cur.execute("""
                INSERT INTO sync_audit_log (
                    trade_id, action_type, data_source,
                    fields_filled, confidence_score, success
                ) VALUES (%s, 'gap_filled_metadata', 'signal_created', %s, 1.0, TRUE)
            """, (
                trade_id,
                psycopg2.extras.Json({
                    'signal_date': signal_data.get('signal_date') is not None,
                    'signal_time': signal_data.get('signal_time') is not None,
                    'session': signal_data.get('session') is not None
                })
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Filled metadata from SIGNAL_CREATED for {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fill metadata from SIGNAL_CREATED: {e}")
            return False
    
    def fill_confirmation_time_from_entry(self, trade_id: str) -> bool:
        """
        Calculate confirmation_time and bars_to_confirmation using SIGNAL_CREATED and ENTRY.
        Confidence: 1.0 (exact calculation from database events)
        """
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Get SIGNAL_CREATED and ENTRY timestamps
            cur.execute("""
                SELECT 
                    sc.timestamp as signal_time,
                    e.timestamp as entry_time
                FROM automated_signals sc
                JOIN automated_signals e ON e.trade_id = sc.trade_id AND e.event_type = 'ENTRY'
                WHERE sc.trade_id = %s
                AND sc.event_type = 'SIGNAL_CREATED'
            """, (trade_id,))
            
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return False
            
            signal_time = row[0]
            entry_time = row[1]
            
            # Calculate bars to confirmation (1 bar = 1 minute)
            time_diff = entry_time - signal_time
            bars_to_confirmation = int(time_diff.total_seconds() / 60)
            
            # Update ENTRY event
            cur.execute("""
                UPDATE automated_signals
                SET 
                    confirmation_time = %s,
                    bars_to_confirmation = %s,
                    data_source = 'reconciled',
                    confidence_score = 1.0,
                    reconciliation_timestamp = NOW(),
                    reconciliation_reason = 'confirmation_time_calculated'
                WHERE trade_id = %s
                AND event_type = 'ENTRY'
            """, (entry_time, bars_to_confirmation, trade_id))
            
            # Log to audit trail
            cur.execute("""
                INSERT INTO sync_audit_log (
                    trade_id, action_type, data_source,
                    fields_filled, confidence_score, success
                ) VALUES (%s, 'gap_filled_confirmation_time', 'signal_created', %s, 1.0, TRUE)
            """, (
                trade_id,
                psycopg2.extras.Json({
                    'confirmation_time': True,
                    'bars_to_confirmation': bars_to_confirmation
                })
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Filled confirmation time for {trade_id} ({bars_to_confirmation} bars)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fill confirmation time: {e}")
            return False
    
    def reconcile_all_from_signal_created(self, trade_ids: List[str] = None) -> Dict:
        """
        Reconcile all gaps that can be filled from SIGNAL_CREATED events.
        This should run BEFORE other reconciliation methods.
        """
        logger.info("🎯 Starting SIGNAL_CREATED reconciliation (Tier 0 - highest confidence)...")
        
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Get all trade_ids that have SIGNAL_CREATED but missing data in ENTRY
            if trade_ids:
                # Reconcile specific trade_ids
                trade_id_filter = "AND sc.trade_id = ANY(%s)"
                params = (trade_ids,)
            else:
                # Reconcile all signals with gaps
                trade_id_filter = ""
                params = ()
            
            cur.execute(f"""
                SELECT DISTINCT sc.trade_id
                FROM automated_signals sc
                JOIN automated_signals e ON e.trade_id = sc.trade_id AND e.event_type = 'ENTRY'
                WHERE sc.event_type = 'SIGNAL_CREATED'
                {trade_id_filter}
                AND (
                    e.htf_alignment IS NULL OR e.htf_alignment = '{{}}' OR
                    e.session IS NULL OR
                    e.signal_date IS NULL OR
                    e.signal_time IS NULL OR
                    e.confirmation_time IS NULL
                )
            """, params)
            
            signals_to_reconcile = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            results = {
                'timestamp': datetime.utcnow().isoformat(),
                'signals_attempted': len(signals_to_reconcile),
                'htf_filled': 0,
                'metadata_filled': 0,
                'confirmation_filled': 0,
                'total_filled': 0
            }
            
            for trade_id in signals_to_reconcile:
                # Try HTF alignment
                if self.fill_htf_alignment_from_signal_created(trade_id):
                    results['htf_filled'] += 1
                    results['total_filled'] += 1
                
                # Try metadata
                if self.fill_metadata_from_signal_created(trade_id):
                    results['metadata_filled'] += 1
                    results['total_filled'] += 1
                
                # Try confirmation time
                if self.fill_confirmation_time_from_entry(trade_id):
                    results['confirmation_filled'] += 1
                    results['total_filled'] += 1
            
            logger.info(f"✅ SIGNAL_CREATED reconciliation complete: {results['total_filled']} fields filled")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ SIGNAL_CREATED reconciliation failed: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'signals_attempted': 0,
                'total_filled': 0,
                'error': str(e)
            }
    
    def get_all_signals_with_gaps(self) -> List[str]:
        """
        Get all trade_ids that have SIGNAL_CREATED but incomplete ENTRY data.
        These are candidates for SIGNAL_CREATED reconciliation.
        """
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            cur.execute("""
                SELECT DISTINCT sc.trade_id
                FROM automated_signals sc
                JOIN automated_signals e ON e.trade_id = sc.trade_id AND e.event_type = 'ENTRY'
                WHERE sc.event_type = 'SIGNAL_CREATED'
                AND (
                    e.htf_alignment IS NULL OR e.htf_alignment = '{}' OR
                    e.session IS NULL OR
                    e.signal_date IS NULL OR
                    e.signal_time IS NULL OR
                    e.confirmation_time IS NULL
                )
            """)
            
            trade_ids = [row[0] for row in cur.fetchall()]
            cur.close()
            conn.close()
            
            return trade_ids
            
        except Exception as e:
            logger.error(f"Error getting signals with gaps: {e}")
            return []

if __name__ == "__main__":
    # Test SIGNAL_CREATED reconciliation
    reconciler = SignalCreatedReconciler()
    
    print("=" * 80)
    print("SIGNAL_CREATED RECONCILIATION TEST")
    print("=" * 80)
    
    # Get signals with gaps
    signals_with_gaps = reconciler.get_all_signals_with_gaps()
    print(f"Signals with gaps that can be filled from SIGNAL_CREATED: {len(signals_with_gaps)}")
    
    if signals_with_gaps:
        print(f"\nSample trade_ids:")
        for trade_id in signals_with_gaps[:5]:
            print(f"  {trade_id}")
        
        # Run reconciliation
        print("\n" + "=" * 80)
        print("RUNNING RECONCILIATION")
        print("=" * 80)
        
        results = reconciler.reconcile_all_from_signal_created()
        
        print(f"\nResults:")
        print(f"  Signals attempted: {results['signals_attempted']}")
        print(f"  HTF alignment filled: {results['htf_filled']}")
        print(f"  Metadata filled: {results['metadata_filled']}")
        print(f"  Confirmation time filled: {results['confirmation_filled']}")
        print(f"  Total fields filled: {results['total_filled']}")

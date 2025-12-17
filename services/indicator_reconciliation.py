"""
Indicator Reconciliation - Nightly data quality checks
Compares canonical tables to ensure data consistency
"""

import logging
import psycopg2
from datetime import datetime, date
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

def run_indicator_reconciliation(date_yyyymmdd: str = None) -> dict:
    """
    Reconcile indicator exports with canonical tables for a specific date.
    
    Args:
        date_yyyymmdd: Target date (YYYYMMDD format) or None for today
        
    Returns:
        dict with reconciliation results and conflict counts
    """
    import os
    
    # Determine target date
    if date_yyyymmdd:
        target_date = datetime.strptime(date_yyyymmdd, '%Y%m%d').date()
    else:
        # Today in America/New_York
        target_date = datetime.now(ZoneInfo("America/New_York")).date()
    
    logger.info(f"[INDICATOR_RECONCILE] Starting reconciliation for date={target_date}")
    
    DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Convert date to ms range for triangle_time_ms (America/New_York boundaries)
        tz = ZoneInfo("America/New_York")
        start_dt = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=tz)
        end_dt = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, 999999, tzinfo=tz)
        start_ms = int(start_dt.timestamp() * 1000)
        end_ms = int(end_dt.timestamp() * 1000)
        
        # Get all signals for target date from all_signals_ledger
        cursor.execute("""
            SELECT trade_id, status, direction, entry_price, stop_loss
            FROM all_signals_ledger
            WHERE triangle_time_ms >= %s AND triangle_time_ms <= %s
        """, (start_ms, end_ms))
        
        ledger_signals = {row[0]: {'status': row[1], 'direction': row[2], 'entry': row[3], 'stop': row[4]} 
                         for row in cursor.fetchall()}
        
        logger.info(f"[INDICATOR_RECONCILE] Found {len(ledger_signals)} signals in all_signals_ledger for {target_date}")
        
        # Get confirmed signals for same trade_ids
        if ledger_signals:
            trade_ids = list(ledger_signals.keys())
            cursor.execute("""
                SELECT trade_id, be_mfe, no_be_mfe, mae, completed
                FROM confirmed_signals_ledger
                WHERE trade_id = ANY(%s)
            """, (trade_ids,))
            
            confirmed_signals = {row[0]: {'be_mfe': row[1], 'no_be_mfe': row[2], 'mae': row[3], 'completed': row[4]} 
                               for row in cursor.fetchall()}
        else:
            confirmed_signals = {}
        
        logger.info(f"[INDICATOR_RECONCILE] Found {len(confirmed_signals)} in confirmed_signals_ledger")
        
        # Step 0: Auto-heal missing confirmed rows from all_signals_ledger
        cursor.execute("""
            INSERT INTO confirmed_signals_ledger (
                trade_id,
                triangle_time_ms,
                confirmation_time_ms,
                date,
                session,
                direction,
                entry,
                stop,
                last_seen_batch_id,
                updated_at
            )
            SELECT
                a.trade_id,
                a.triangle_time_ms,
                a.confirmation_time_ms,
                a.updated_at::date,
                a.session,
                a.direction,
                a.entry_price,
                a.stop_loss,
                a.last_seen_batch_id,
                NOW()
            FROM all_signals_ledger a
            LEFT JOIN confirmed_signals_ledger c ON a.trade_id = c.trade_id
            WHERE a.status = 'CONFIRMED'
              AND c.trade_id IS NULL
        """)
        
        auto_created = cursor.rowcount
        conn.commit()
        
        if auto_created > 0:
            logger.info(f"[INDICATOR_RECONCILE] Auto-created {auto_created} confirmed ledger rows")
        
        # Check latest ALL_SIGNALS_EXPORT batch for missing ledger rows
        cursor.execute("""
            SELECT id, payload_json
            FROM indicator_export_batches
            WHERE event_type = 'ALL_SIGNALS_EXPORT' AND is_valid = true
            ORDER BY received_at DESC
            LIMIT 1
        """)
        
        batch_row = cursor.fetchone()
        missing_ledger_trade_ids = []
        
        if batch_row:
            batch_id_latest, batch_payload = batch_row
            batch_signals = batch_payload.get('signals', [])
            
            # Filter to signals within date window
            batch_trade_ids_in_window = []
            for sig in batch_signals:
                sig_time = sig.get('signal_time')
                if sig_time and start_ms <= sig_time <= end_ms:
                    batch_trade_ids_in_window.append(sig.get('trade_id'))
            
            # Find missing in ledger
            missing_ledger_trade_ids = [tid for tid in batch_trade_ids_in_window if tid and tid not in ledger_signals]
            
            logger.info(f"[INDICATOR_RECONCILE] Latest batch has {len(batch_trade_ids_in_window)} signals in date window, {len(missing_ledger_trade_ids)} missing from ledger")
        
        # Identify issues (missing_confirmed removed - auto-healed above)
        missing_entry_stop = []
        
        for trade_id, ledger_data in ledger_signals.items():
            # Check if CONFIRMED signal missing entry/stop
            if ledger_data['status'] == 'CONFIRMED' and (ledger_data['entry'] is None or ledger_data['stop'] is None):
                missing_entry_stop.append(trade_id)
        
        logger.info(f"[INDICATOR_RECONCILE] Issues found: missing_confirmed={len(missing_confirmed)}, missing_entry_stop={len(missing_entry_stop)}")
        
        # Save reconciliation record (matching existing schema)
        total_missing = len(missing_ledger_trade_ids)
        total_conflicts = total_missing + len(missing_entry_stop)
        
        cursor.execute("""
            INSERT INTO data_quality_reconciliations 
            (reconciliation_date, reconciliation_time, signals_in_indicator, signals_in_database,
             missing_signals, incomplete_signals, mfe_mismatches, conflicts_requiring_review, 
             auto_resolved, webhook_success_rate, status, notes)
            VALUES (%s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            target_date,
            len(ledger_signals),
            len(confirmed_signals),
            total_missing,
            len(missing_entry_stop),
            0,  # mfe_mismatches (not checked yet)
            total_conflicts,
            0,  # auto_resolved
            None,  # webhook_success_rate (nullable)
            'complete',
            f'Indicator reconciliation for {target_date}'
        ))
        
        reconciliation_id = cursor.fetchone()[0]
        
        logger.info(f"[INDICATOR_RECONCILE] Created reconciliation record id={reconciliation_id}")
        
        # Save conflicts (matching existing schema)
        conflicts_saved = 0
        
        for trade_id in missing_ledger_trade_ids:
            cursor.execute("""
                INSERT INTO data_quality_conflicts
                (reconciliation_id, trade_id, conflict_type, webhook_value, indicator_value, 
                 field_name, severity, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (reconciliation_id, trade_id, 'missing_signal',
                  'missing_in_ledger', 'present_in_export', 'all_signals_ledger', 'high', 'pending'))
            conflicts_saved += 1
        
        for trade_id in missing_entry_stop:
            cursor.execute("""
                INSERT INTO data_quality_conflicts
                (reconciliation_id, trade_id, conflict_type, webhook_value, indicator_value,
                 field_name, severity, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (reconciliation_id, trade_id, 'missing_field',
                  'null', 'null', 'entry_price,stop_loss', 'medium', 'pending'))
            conflicts_saved += 1
        
        conn.commit()
        
        logger.info(f"[INDICATOR_RECONCILE] ✅ Saved {conflicts_saved} conflicts")
        
        result = {
            'success': True,
            'reconciliation_id': reconciliation_id,
            'date': str(target_date),
            'total_signals': len(ledger_signals),
            'confirmed_signals': len([s for s in ledger_signals.values() if s['status'] == 'CONFIRMED']),
            'in_confirmed_ledger': len(confirmed_signals),
            'issues': {
                'missing_ledger': len(missing_ledger_trade_ids),
                'missing_entry_stop': len(missing_entry_stop),
                'auto_created_confirmed': auto_created
            },
            'conflicts_saved': conflicts_saved
        }
        
        logger.info(f"[INDICATOR_RECONCILE] ✅ Reconciliation complete: {result}")
        
        return result
        
    except Exception as e:
        conn.rollback()
        logger.error(f"[INDICATOR_RECONCILE] ❌ Error: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_signals': 0,
            'issues': {}
        }
        
    finally:
        cursor.close()
        conn.close()

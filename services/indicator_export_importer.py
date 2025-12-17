"""
Indicator Export Importer - INDICATOR_EXPORT_V2
Idempotent import from raw batches into confirmed_signals_ledger
"""

import logging
import psycopg2
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def import_indicator_export_v2(batch_id: int, conn=None) -> dict:
    """
    Import INDICATOR_EXPORT_V2 batch into confirmed_signals_ledger.
    
    Args:
        batch_id: ID from indicator_export_batches table
        
    Returns:
        dict with counts: inserted, updated, skipped_invalid
    """
    import os
    
    logger.info(f"[INDICATOR_IMPORT_V2] Starting import for batch_id={batch_id}")
    
    # Use injected connection or create new one
    conn_provided = conn is not None
    if not conn_provided:
        DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
    
    cursor = conn.cursor()
    
    try:
        # Load batch payload
        cursor.execute("""
            SELECT payload_json, event_type, batch_number, batch_size
            FROM indicator_export_batches
            WHERE id = %s
        """, (batch_id,))
        
        row = cursor.fetchone()
        if not row:
            logger.error(f"[INDICATOR_IMPORT_V2] Batch {batch_id} not found")
            return {'error': 'Batch not found', 'inserted': 0, 'updated': 0, 'skipped_invalid': 0}
        
        payload_json, event_type, batch_number, batch_size = row
        
        # Enforce correct event_type
        if event_type != 'INDICATOR_EXPORT_V2':
            logger.error(f"[INDICATOR_IMPORT_V2] Wrong event_type={event_type}, expected INDICATOR_EXPORT_V2")
            return {'success': False, 'error': 'wrong_event_type', 'inserted': 0, 'updated': 0, 'skipped_invalid': 0}
        
        signals = payload_json.get('signals', [])
        
        logger.info(f"[INDICATOR_IMPORT_V2] Loaded batch {batch_number}, event_type={event_type}, signals={len(signals)}")
        
        inserted = 0
        updated = 0
        skipped_invalid = 0
        
        for signal in signals:
            # Validate and coerce required fields
            trade_id = signal.get('trade_id')
            direction = signal.get('direction')
            
            # Coerce triangle_time_ms
            try:
                triangle_time = int(signal.get('triangle_time'))
            except (ValueError, TypeError):
                logger.warning(f"[INDICATOR_IMPORT_V2] Skipping signal - invalid triangle_time: {signal}")
                skipped_invalid += 1
                continue
            
            if not trade_id or not direction:
                logger.warning(f"[INDICATOR_IMPORT_V2] Skipping signal - missing required fields: {signal}")
                skipped_invalid += 1
                continue
            
            # Coerce confirmation_time_ms
            try:
                confirmation_time = int(signal['confirmation_time']) if signal.get('confirmation_time') else None
            except (ValueError, TypeError):
                confirmation_time = None
            date_str = signal.get('date')
            session = signal.get('session')
            
            # Coerce numeric fields
            try:
                entry = float(signal['entry']) if signal.get('entry') else None
            except (ValueError, TypeError):
                entry = None
            
            try:
                stop = float(signal['stop']) if signal.get('stop') else None
            except (ValueError, TypeError):
                stop = None
            
            try:
                be_mfe = float(signal['be_mfe']) if signal.get('be_mfe') else None
            except (ValueError, TypeError):
                be_mfe = None
            
            try:
                no_be_mfe = float(signal['no_be_mfe']) if signal.get('no_be_mfe') else None
            except (ValueError, TypeError):
                no_be_mfe = None
            
            try:
                mae = float(signal['mae']) if signal.get('mae') else None
            except (ValueError, TypeError):
                mae = None
            
            # Ensure MAE <= 0.0
            if mae is not None and mae > 0.0:
                logger.warning(f"[INDICATOR_IMPORT_V2] MAE > 0 detected for {trade_id}: {mae}, clamping to 0.0")
                mae = 0.0
            
            # Coerce completed field
            completed_raw = signal.get('completed')
            if isinstance(completed_raw, str):
                completed = completed_raw.lower() == 'true'
            elif isinstance(completed_raw, bool):
                completed = completed_raw
            else:
                completed = None
            
            # Parse date
            date_obj = None
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    date_obj = None
            
            # Upsert into confirmed_signals_ledger
            cursor.execute("""
                INSERT INTO confirmed_signals_ledger 
                (trade_id, triangle_time_ms, confirmation_time_ms, date, session, direction, 
                 entry, stop, be_mfe, no_be_mfe, mae, completed, last_seen_batch_id, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (trade_id) DO UPDATE SET
                    direction = EXCLUDED.direction,
                    confirmation_time_ms = COALESCE(EXCLUDED.confirmation_time_ms, confirmed_signals_ledger.confirmation_time_ms),
                    date = COALESCE(EXCLUDED.date, confirmed_signals_ledger.date),
                    session = COALESCE(EXCLUDED.session, confirmed_signals_ledger.session),
                    entry = COALESCE(EXCLUDED.entry, confirmed_signals_ledger.entry),
                    stop = COALESCE(EXCLUDED.stop, confirmed_signals_ledger.stop),
                    be_mfe = COALESCE(EXCLUDED.be_mfe, confirmed_signals_ledger.be_mfe),
                    no_be_mfe = COALESCE(EXCLUDED.no_be_mfe, confirmed_signals_ledger.no_be_mfe),
                    mae = COALESCE(EXCLUDED.mae, confirmed_signals_ledger.mae),
                    completed = COALESCE(EXCLUDED.completed, confirmed_signals_ledger.completed),
                    last_seen_batch_id = EXCLUDED.last_seen_batch_id,
                    updated_at = NOW()
                RETURNING (xmax = 0) AS inserted
            """, (trade_id, triangle_time, confirmation_time, date_obj, session, direction,
                  entry, stop, be_mfe, no_be_mfe, mae, completed, batch_id))
            
            result = cursor.fetchone()
            if result and result[0]:
                inserted += 1
            else:
                updated += 1
        
        conn.commit()
        
        logger.info(f"[INDICATOR_IMPORT_V2] ✅ Batch {batch_id} complete: inserted={inserted}, updated={updated}, skipped={skipped_invalid}")
        
        return {
            'success': True,
            'batch_id': batch_id,
            'inserted': inserted,
            'updated': updated,
            'skipped_invalid': skipped_invalid,
            'total_processed': inserted + updated
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"[INDICATOR_IMPORT_V2] ❌ Error importing batch {batch_id}: {e}")
        return {
            'success': False,
            'error': str(e),
            'inserted': 0,
            'updated': 0,
            'skipped_invalid': 0
        }
        
    finally:
        cursor.close()
        if not conn_provided:
            conn.close()


def import_all_signals_export(batch_id: int) -> dict:
    """
    Import ALL_SIGNALS_EXPORT batch into all_signals_ledger.
    
    Args:
        batch_id: ID from indicator_export_batches table
        
    Returns:
        dict with counts: inserted, updated, skipped_invalid
    """
    import os
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    logger.info(f"[ALL_SIGNALS_IMPORT] Starting import for batch_id={batch_id}")
    
    DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    try:
        # Load batch payload
        cursor.execute("""
            SELECT payload_json, event_type, batch_number, batch_size
            FROM indicator_export_batches
            WHERE id = %s
        """, (batch_id,))
        
        row = cursor.fetchone()
        if not row:
            logger.error(f"[ALL_SIGNALS_IMPORT] Batch {batch_id} not found")
            return {'error': 'Batch not found', 'inserted': 0, 'updated': 0, 'skipped_invalid': 0}
        
        payload_json, event_type, batch_number, batch_size = row
        
        # Enforce correct event_type
        if event_type != 'ALL_SIGNALS_EXPORT':
            logger.error(f"[ALL_SIGNALS_IMPORT] Wrong event_type={event_type}, expected ALL_SIGNALS_EXPORT")
            return {'success': False, 'error': 'wrong_event_type', 'inserted': 0, 'updated': 0, 'skipped_invalid': 0}
        
        signals = payload_json.get('signals', [])
        
        logger.info(f"[ALL_SIGNALS_IMPORT] Loaded batch {batch_number}, event_type={event_type}, signals={len(signals)}")
        
        inserted = 0
        updated = 0
        skipped_invalid = 0
        
        for signal in signals:
            # Validate and coerce required fields
            trade_id = signal.get('trade_id')
            direction = signal.get('direction')
            status = signal.get('status')
            
            # Coerce triangle_time_ms
            try:
                triangle_time_ms = int(signal.get('signal_time'))
            except (ValueError, TypeError):
                logger.warning(f"[ALL_SIGNALS_IMPORT] Skipping signal - invalid signal_time: {signal}")
                skipped_invalid += 1
                continue
            
            if not trade_id or not direction or not status:
                logger.warning(f"[ALL_SIGNALS_IMPORT] Skipping signal - missing required fields: {signal}")
                skipped_invalid += 1
                continue
            
            # Coerce confirmation_time_ms
            try:
                confirmation_time_ms = int(signal['confirmation_time']) if signal.get('confirmation_time') else None
            except (ValueError, TypeError):
                confirmation_time_ms = None
            
            # Coerce bars_to_confirm
            try:
                bars_to_confirm = int(signal['bars_to_confirm']) if signal.get('bars_to_confirm') else None
            except (ValueError, TypeError):
                bars_to_confirm = None
            
            # Coerce numeric fields safely
            try:
                entry_price = float(signal['entry']) if signal.get('entry') and signal.get('entry') != 'null' else None
            except (ValueError, TypeError):
                entry_price = None
            
            try:
                stop_loss = float(signal['stop']) if signal.get('stop') and signal.get('stop') != 'null' else None
            except (ValueError, TypeError):
                stop_loss = None
            
            try:
                risk_points = float(signal['risk']) if signal.get('risk') and signal.get('risk') != 'null' else None
            except (ValueError, TypeError):
                risk_points = None
            
            # HTF fields
            htf_daily = signal.get('htf_daily')
            htf_4h = signal.get('htf_4h')
            htf_1h = signal.get('htf_1h')
            htf_15m = signal.get('htf_15m')
            htf_5m = signal.get('htf_5m')
            htf_1m = signal.get('htf_1m')
            
            # Compute session from triangle_time_ms if not provided
            session = signal.get('session')
            if not session:
                # Convert ms timestamp to datetime in America/New_York
                try:
                    dt = datetime.fromtimestamp(triangle_time_ms / 1000, tz=ZoneInfo("America/New_York"))
                    h = dt.hour
                    m = dt.minute
                    
                    if 20 <= h <= 23:
                        session = "ASIA"
                    elif 0 <= h <= 5:
                        session = "LONDON"
                    elif h == 6 or (h == 8 and m <= 29):
                        session = "NY PRE"
                    elif (h == 8 and m >= 30) or (9 <= h <= 11):
                        session = "NY AM"
                    elif h == 12:
                        session = "NY LUNCH"
                    elif 13 <= h <= 15:
                        session = "NY PM"
                    else:
                        session = "AFTER_HOURS"
                except:
                    session = None
            
            # Upsert into all_signals_ledger
            # Do not overwrite non-null entry/stop with null (prefer existing non-null)
            cursor.execute("""
                INSERT INTO all_signals_ledger 
                (trade_id, triangle_time_ms, confirmation_time_ms, direction, status, 
                 bars_to_confirm, session, entry_price, stop_loss, risk_points,
                 htf_daily, htf_4h, htf_1h, htf_15m, htf_5m, htf_1m,
                 last_seen_batch_id, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (trade_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    confirmation_time_ms = COALESCE(EXCLUDED.confirmation_time_ms, all_signals_ledger.confirmation_time_ms),
                    bars_to_confirm = COALESCE(EXCLUDED.bars_to_confirm, all_signals_ledger.bars_to_confirm),
                    session = COALESCE(EXCLUDED.session, all_signals_ledger.session),
                    entry_price = COALESCE(EXCLUDED.entry_price, all_signals_ledger.entry_price),
                    stop_loss = COALESCE(EXCLUDED.stop_loss, all_signals_ledger.stop_loss),
                    risk_points = COALESCE(EXCLUDED.risk_points, all_signals_ledger.risk_points),
                    htf_daily = COALESCE(EXCLUDED.htf_daily, all_signals_ledger.htf_daily),
                    htf_4h = COALESCE(EXCLUDED.htf_4h, all_signals_ledger.htf_4h),
                    htf_1h = COALESCE(EXCLUDED.htf_1h, all_signals_ledger.htf_1h),
                    htf_15m = COALESCE(EXCLUDED.htf_15m, all_signals_ledger.htf_15m),
                    htf_5m = COALESCE(EXCLUDED.htf_5m, all_signals_ledger.htf_5m),
                    htf_1m = COALESCE(EXCLUDED.htf_1m, all_signals_ledger.htf_1m),
                    last_seen_batch_id = EXCLUDED.last_seen_batch_id,
                    updated_at = NOW()
                RETURNING (xmax = 0) AS inserted
            """, (trade_id, triangle_time_ms, confirmation_time_ms, direction, status,
                  bars_to_confirm, session, entry_price, stop_loss, risk_points,
                  htf_daily, htf_4h, htf_1h, htf_15m, htf_5m, htf_1m, batch_id))
            
            result = cursor.fetchone()
            if result and result[0]:
                inserted += 1
            else:
                updated += 1
        
        conn.commit()
        
        logger.info(f"[ALL_SIGNALS_IMPORT] ✅ Batch {batch_id} complete: inserted={inserted}, updated={updated}, skipped={skipped_invalid}")
        
        return {
            'success': True,
            'batch_id': batch_id,
            'inserted': inserted,
            'updated': updated,
            'skipped_invalid': skipped_invalid,
            'total_processed': inserted + updated
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"[ALL_SIGNALS_IMPORT] ❌ Error importing batch {batch_id}: {e}")
        return {
            'success': False,
            'error': str(e),
            'inserted': 0,
            'updated': 0,
            'skipped_invalid': 0
        }
        
    finally:
        cursor.close()
        conn.close()

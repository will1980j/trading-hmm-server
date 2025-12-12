"""
Hybrid Signal Synchronization System - Reconciliation Engine
Enterprise-grade three-tier gap filling with confidence scoring
"""

import psycopg2
import os
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
import logging
import pytz

load_dotenv()
logger = logging.getLogger(__name__)

class ReconciliationEngine:
    """
    Three-tier gap filling system:
    Tier 1: Request from indicator (confidence 1.0) - NOT IMPLEMENTED YET
    Tier 2: Calculate from database (confidence 0.8)
    Tier 3: Extract from trade_id (confidence 0.9 for metadata)
    """
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.ny_tz = pytz.timezone('America/New_York')
        self.utc_tz = pytz.UTC
        
    def get_current_price(self) -> Optional[float]:
        """
        Get current NQ price from most recent MFE_UPDATE.
        Returns None if no recent price data available.
        """
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Get most recent price from batch payload
            cur.execute("""
                SELECT raw_payload
                FROM automated_signals
                WHERE event_type = 'MFE_UPDATE'
                AND raw_payload IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cur.fetchone()
            if row and row[0]:
                import json
                payload = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                current_price = payload.get('current_price')
                if current_price:
                    cur.close()
                    conn.close()
                    return float(current_price)
            
            cur.close()
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None
    
    def calculate_mfe_mae(self, entry_price: float, stop_loss: float, 
                          direction: str, current_price: float) -> Tuple[float, float, float]:
        """
        Calculate MFE and MAE from entry/stop/current price.
        Returns: (be_mfe, no_be_mfe, mae)
        
        MFE = Maximum Favorable Excursion (how far price moved in favorable direction)
        MAE = Maximum Adverse Excursion (worst drawdown, always negative or zero)
        """
        try:
            entry = float(entry_price)
            stop = float(stop_loss)
            price = float(current_price)
            risk = abs(entry - stop)
            
            if risk == 0:
                logger.warning(f"Risk is zero: entry={entry}, stop={stop}")
                return 0.0, 0.0, 0.0
            
            if direction in ['Bullish', 'LONG']:
                # For bullish: favorable = price going UP from entry
                mfe = (price - entry) / risk
                
                # MAE: If price is below entry, that's adverse movement
                # Conservative: assume worst case is hitting the stop
                if price < entry:
                    mae = (price - entry) / risk  # Will be negative
                else:
                    mae = 0.0  # No adverse movement yet
                
                # BE MFE: If MFE >= 1.0, assume BE triggered
                # After BE trigger, BE MFE caps at the value when BE was hit
                # We don't know exact BE trigger point, so use current MFE if < 1.0, else 1.0
                if mfe >= 1.0:
                    be_mfe = 1.0  # Assume BE triggered and stopped at entry
                else:
                    be_mfe = mfe  # BE not triggered yet, same as No-BE
                    
            else:  # Bearish/SHORT
                # For bearish: favorable = price going DOWN from entry
                mfe = (entry - price) / risk
                
                # MAE: If price is above entry, that's adverse movement
                if price > entry:
                    mae = (entry - price) / risk  # Will be negative
                else:
                    mae = 0.0  # No adverse movement yet
                
                # BE MFE logic same as bullish
                if mfe >= 1.0:
                    be_mfe = 1.0
                else:
                    be_mfe = mfe
            
            # Ensure MFE is never negative (that would mean price moved against us)
            mfe = max(0.0, mfe)
            be_mfe = max(0.0, be_mfe)
            
            # Ensure MAE is never positive (it's adverse movement)
            mae = min(0.0, mae)
            
            return be_mfe, mfe, mae
            
        except Exception as e:
            logger.error(f"Error calculating MFE/MAE: {e}")
            return 0.0, 0.0, 0.0
    
    def extract_metadata_from_trade_id(self, trade_id: str) -> Dict:
        """
        Extract signal_date, signal_time, direction from trade_id.
        Format: YYYYMMDD_HHMMSS000_DIRECTION
        Confidence: 0.9 (trade_id is reliable)
        """
        try:
            parts = trade_id.split('_')
            if len(parts) >= 3:
                date_str = parts[0]  # YYYYMMDD
                time_str = parts[1][:6]  # HHMMSS
                direction = parts[2]  # BULLISH/BEARISH
                
                # Parse date
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                signal_date = f"{year}-{month:02d}-{day:02d}"
                
                # Parse time
                hour = int(time_str[:2])
                minute = int(time_str[2:4])
                second = int(time_str[4:6])
                signal_time = f"{hour:02d}:{minute:02d}:{second:02d}"
                
                # Determine session from time (NY timezone)
                session = self.determine_session(hour, minute)
                
                return {
                    'signal_date': signal_date,
                    'signal_time': signal_time,
                    'direction': 'LONG' if direction == 'BULLISH' else 'SHORT',
                    'session': session,
                    'confidence': 0.9
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {trade_id}: {e}")
            return {}
    
    def determine_session(self, hour: int, minute: int) -> str:
        """Determine trading session from NY time"""
        if 20 <= hour <= 23:
            return "ASIA"
        elif 0 <= hour <= 5:
            return "LONDON"
        elif hour == 6 or (hour == 8 and minute <= 29):
            return "NY PRE"
        elif (hour == 8 and minute >= 30) or (9 <= hour <= 11):
            return "NY AM"
        elif hour == 12:
            return "NY LUNCH"
        elif 13 <= hour <= 15:
            return "NY PM"
        else:
            return "AFTER_HOURS"
    
    def calculate_extended_targets(self, entry_price: float, stop_loss: float, 
                                   direction: str) -> Dict:
        """Calculate targets from 1R to 20R"""
        try:
            entry = float(entry_price)
            stop = float(stop_loss)
            risk = abs(entry - stop)
            
            targets = {}
            for r in range(1, 21):  # 1R to 20R
                if direction in ['Bullish', 'LONG']:
                    target_price = entry + (r * risk)
                else:
                    target_price = entry - (r * risk)
                
                targets[f'target_{r}R'] = round(target_price, 2)
            
            return targets
            
        except Exception as e:
            logger.error(f"Error calculating targets: {e}")
            return {}
    
    def fill_mfe_mae_gap(self, trade_id: str, entry_price: float, stop_loss: float,
                         direction: str, current_price: float) -> bool:
        """
        Fill MFE/MAE gap using Tier 2 (database calculation).
        Confidence: 0.8
        """
        try:
            # Calculate MFE/MAE
            be_mfe, no_be_mfe, mae = self.calculate_mfe_mae(
                entry_price, stop_loss, direction, current_price
            )
            
            # Extract metadata from trade_id
            metadata = self.extract_metadata_from_trade_id(trade_id)
            
            # Build timestamp
            signal_date = metadata.get('signal_date')
            signal_time = metadata.get('signal_time')
            
            if signal_date and signal_time:
                dt_str = f"{signal_date} {signal_time}"
                signal_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                signal_dt = self.ny_tz.localize(signal_dt)
                utc_dt = signal_dt.astimezone(self.utc_tz)
            else:
                utc_dt = datetime.utcnow()
            
            # Insert reconciled MFE_UPDATE
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
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
                    'backend_calculated', 0.8,
                    NOW(), 'mfe_mae_gap_fill',
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
                    'reconciled': True,
                    'method': 'tier2_calculation'
                })
            ))
            
            # Log to audit trail
            cur.execute("""
                INSERT INTO sync_audit_log (
                    trade_id, action_type, data_source,
                    fields_filled, confidence_score, success
                ) VALUES (%s, 'gap_filled_mfe_mae', 'backend_calculated', %s, 0.8, TRUE)
            """, (
                trade_id,
                json.dumps({'be_mfe': True, 'no_be_mfe': True, 'mae': True})
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Filled MFE/MAE gap for {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fill MFE/MAE gap for {trade_id}: {e}")
            return False
    
    def fill_metadata_gap(self, trade_id: str) -> bool:
        """
        Fill metadata gaps (session, signal_date, signal_time) using Tier 3 (trade_id extraction).
        Confidence: 0.9
        """
        try:
            metadata = self.extract_metadata_from_trade_id(trade_id)
            if not metadata:
                return False
            
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Update ENTRY event with extracted metadata
            cur.execute("""
                UPDATE automated_signals
                SET 
                    signal_date = COALESCE(signal_date, %s),
                    signal_time = COALESCE(signal_time, %s),
                    session = COALESCE(session, %s),
                    direction = COALESCE(direction, %s),
                    data_source = 'reconciled',
                    confidence_score = 0.9,
                    reconciliation_timestamp = NOW(),
                    reconciliation_reason = 'metadata_extracted_from_trade_id'
                WHERE trade_id = %s
                AND event_type = 'ENTRY'
            """, (
                metadata.get('signal_date'),
                metadata.get('signal_time'),
                metadata.get('session'),
                metadata.get('direction'),
                trade_id
            ))
            
            # Log to audit trail
            cur.execute("""
                INSERT INTO sync_audit_log (
                    trade_id, action_type, data_source,
                    fields_filled, confidence_score, success
                ) VALUES (%s, 'gap_filled_metadata', 'trade_id_extraction', %s, 0.9, TRUE)
            """, (
                trade_id,
                json.dumps({
                    'signal_date': metadata.get('signal_date') is not None,
                    'signal_time': metadata.get('signal_time') is not None,
                    'session': metadata.get('session') is not None
                })
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Filled metadata gap for {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fill metadata gap for {trade_id}: {e}")
            return False
    
    def fill_targets_gap(self, trade_id: str, entry_price: float, stop_loss: float, direction: str) -> bool:
        """Fill missing extended targets (1R-20R)"""
        try:
            targets = self.calculate_extended_targets(entry_price, stop_loss, direction)
            if not targets:
                return False
            
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE automated_signals
                SET 
                    targets_extended = %s,
                    reconciliation_timestamp = NOW(),
                    reconciliation_reason = 'targets_calculated'
                WHERE trade_id = %s
                AND event_type = 'ENTRY'
            """, (json.dumps(targets), trade_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Filled targets gap for {trade_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fill targets gap for {trade_id}: {e}")
            return False
    
    def reconcile_signal(self, gap_data: Dict) -> bool:
        """
        Reconcile a single signal based on gap type.
        Routes to appropriate gap-filling method.
        """
        trade_id = gap_data['trade_id']
        gap_type = gap_data['gap_type']
        
        try:
            if gap_type == 'No MFE Update':
                # Need current price to calculate MFE
                current_price = self.get_current_price()
                if not current_price:
                    logger.warning(f"Cannot reconcile {trade_id}: No current price available")
                    return False
                
                return self.fill_mfe_mae_gap(
                    trade_id,
                    gap_data['entry_price'],
                    gap_data['stop_loss'],
                    gap_data['direction'],
                    current_price
                )
            
            elif gap_type in ['No Session Data', 'No Signal Date']:
                return self.fill_metadata_gap(trade_id)
            
            elif gap_type == 'No Extended Targets':
                return self.fill_targets_gap(
                    trade_id,
                    gap_data['entry_price'],
                    gap_data['stop_loss'],
                    gap_data.get('direction', 'LONG')
                )
            
            else:
                logger.warning(f"Unknown gap type: {gap_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error reconciling {trade_id}: {e}")
            return False
    
    def reconcile_all_gaps(self, gap_report: Dict) -> Dict:
        """
        Reconcile all detected gaps.
        Returns summary of reconciliation results.
        """
        logger.info("🔧 Starting gap reconciliation...")
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'gaps_attempted': 0,
            'gaps_filled': 0,
            'gaps_failed': 0,
            'by_type': {}
        }
        
        for gap_type, gap_list in gap_report['gap_details'].items():
            if not gap_list:
                continue
            
            type_success = 0
            type_failed = 0
            
            for gap_data in gap_list:
                results['gaps_attempted'] += 1
                
                if self.reconcile_signal(gap_data):
                    results['gaps_filled'] += 1
                    type_success += 1
                else:
                    results['gaps_failed'] += 1
                    type_failed += 1
            
            results['by_type'][gap_type] = {
                'attempted': len(gap_list),
                'filled': type_success,
                'failed': type_failed
            }
        
        logger.info(f"✅ Reconciliation complete: {results['gaps_filled']}/{results['gaps_attempted']} gaps filled")
        
        return results

if __name__ == "__main__":
    # Test reconciliation
    from gap_detector import GapDetector
    
    detector = GapDetector()
    gap_report = detector.run_complete_scan()
    
    engine = ReconciliationEngine()
    results = engine.reconcile_all_gaps(gap_report)
    
    print("=" * 80)
    print("RECONCILIATION RESULTS")
    print("=" * 80)
    print(f"Gaps Attempted: {results['gaps_attempted']}")
    print(f"Gaps Filled: {results['gaps_filled']}")
    print(f"Gaps Failed: {results['gaps_failed']}")
    print()
    print("By Type:")
    for gap_type, stats in results['by_type'].items():
        print(f"  {gap_type}: {stats['filled']}/{stats['attempted']} filled")

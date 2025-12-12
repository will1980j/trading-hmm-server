"""
Hybrid Signal Synchronization System - Gap Detection Engine
Enterprise-grade gap detection with comprehensive field validation
"""

import psycopg2
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class GapDetector:
    """
    Detects data gaps in signal lifecycle with specific, actionable flags.
    Runs every 2 minutes to ensure real-time gap awareness.
    """
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.gap_threshold_minutes = 2  # Flag if no MFE update in 2 minutes
        
    def detect_no_mfe_update(self) -> List[Dict]:
        """Detect signals with no MFE_UPDATE in last 2 minutes"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                e.trade_id,
                e.entry_price,
                e.stop_loss,
                e.direction,
                MAX(m.timestamp) as last_mfe_update,
                EXTRACT(EPOCH FROM (NOW() - MAX(m.timestamp)))/60 as minutes_since_update
            FROM automated_signals e
            LEFT JOIN automated_signals m ON m.trade_id = e.trade_id AND m.event_type = 'MFE_UPDATE'
            WHERE e.event_type = 'ENTRY'
            AND e.trade_id NOT IN (
                SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%'
            )
            GROUP BY e.trade_id, e.entry_price, e.stop_loss, e.direction
            HAVING MAX(m.timestamp) IS NULL OR MAX(m.timestamp) < NOW() - INTERVAL '2 minutes'
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No MFE Update',
                'entry_price': float(row[1]) if row[1] else None,
                'stop_loss': float(row[2]) if row[2] else None,
                'direction': row[3],
                'last_update': row[4],
                'minutes_since': float(row[5]) if row[5] else 999
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_no_entry_price(self) -> List[Dict]:
        """Detect signals with NULL entry_price"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT trade_id, signal_date, signal_time, direction
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND entry_price IS NULL
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No Entry Price',
                'signal_date': row[1],
                'signal_time': row[2],
                'direction': row[3]
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_no_stop_loss(self) -> List[Dict]:
        """Detect signals with NULL stop_loss"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT trade_id, signal_date, signal_time, direction, entry_price
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND stop_loss IS NULL
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No Stop Loss',
                'signal_date': row[1],
                'signal_time': row[2],
                'direction': row[3],
                'entry_price': float(row[4]) if row[4] else None
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_no_mae(self) -> List[Dict]:
        """Detect active signals with no MAE data"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT e.trade_id, e.entry_price, e.stop_loss, e.direction
            FROM automated_signals e
            WHERE e.event_type = 'ENTRY'
            AND e.trade_id NOT IN (
                SELECT DISTINCT trade_id FROM automated_signals WHERE event_type LIKE 'EXIT_%'
            )
            AND NOT EXISTS (
                SELECT 1 FROM automated_signals m
                WHERE m.trade_id = e.trade_id
                AND m.mae_global_r IS NOT NULL
                AND m.mae_global_r != 0
            )
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No MAE',
                'entry_price': float(row[1]) if row[1] else None,
                'stop_loss': float(row[2]) if row[2] else None,
                'direction': row[3]
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_no_session(self) -> List[Dict]:
        """Detect signals with NULL session"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT trade_id, signal_date, signal_time, direction
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND session IS NULL
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No Session Data',
                'signal_date': row[1],
                'signal_time': row[2],
                'direction': row[3]
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_no_signal_date(self) -> List[Dict]:
        """Detect signals with NULL signal_date"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT trade_id, timestamp, direction
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND signal_date IS NULL
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No Signal Date',
                'timestamp': row[1],
                'direction': row[2]
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_missing_htf_alignment(self) -> List[Dict]:
        """Detect signals missing HTF alignment data"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT trade_id, signal_date, signal_time
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND (htf_alignment IS NULL OR htf_alignment = '{}')
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No HTF Alignment',
                'signal_date': row[1],
                'signal_time': row[2]
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_missing_targets(self) -> List[Dict]:
        """Detect signals missing extended targets (1R-20R)"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT trade_id, entry_price, stop_loss
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND (targets_extended IS NULL OR targets_extended = '{}')
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No Extended Targets',
                'entry_price': float(row[1]) if row[1] else None,
                'stop_loss': float(row[2]) if row[2] else None
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def detect_missing_confirmation_time(self) -> List[Dict]:
        """Detect signals missing confirmation time tracking"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT trade_id, signal_date, signal_time
            FROM automated_signals
            WHERE event_type = 'ENTRY'
            AND confirmation_time IS NULL
        """)
        
        gaps = []
        for row in cur.fetchall():
            gaps.append({
                'trade_id': row[0],
                'gap_type': 'No Confirmation Time',
                'signal_date': row[1],
                'signal_time': row[2]
            })
        
        cur.close()
        conn.close()
        return gaps
    
    def calculate_health_score(self, gaps: Dict[str, List]) -> int:
        """
        Calculate health score (0-100) based on gap types.
        Each gap type deducts points based on severity.
        """
        score = 100
        
        # Critical gaps (high impact)
        score -= len(gaps.get('no_mfe_update', [])) * 20  # Most critical
        score -= len(gaps.get('no_entry_price', [])) * 15
        score -= len(gaps.get('no_stop_loss', [])) * 15
        
        # Important gaps (medium impact)
        score -= len(gaps.get('no_mae', [])) * 10
        score -= len(gaps.get('no_session', [])) * 8
        score -= len(gaps.get('no_signal_date', [])) * 8
        
        # Nice-to-have gaps (low impact)
        score -= len(gaps.get('no_htf_alignment', [])) * 5
        score -= len(gaps.get('no_targets', [])) * 5
        score -= len(gaps.get('no_confirmation_time', [])) * 3
        
        return max(0, min(100, score))
    
    def run_complete_scan(self) -> Dict:
        """
        Run complete gap detection across all field types.
        Returns comprehensive gap report.
        """
        logger.info("🔍 Starting comprehensive gap detection scan...")
        
        gaps = {
            'no_mfe_update': self.detect_no_mfe_update(),
            'no_entry_price': self.detect_no_entry_price(),
            'no_stop_loss': self.detect_no_stop_loss(),
            'no_mae': self.detect_no_mae(),
            'no_session': self.detect_no_session(),
            'no_signal_date': self.detect_no_signal_date(),
            'no_htf_alignment': self.detect_missing_htf_alignment(),
            'no_targets': self.detect_missing_targets(),
            'no_confirmation_time': self.detect_missing_confirmation_time()
        }
        
        # Calculate total gaps
        total_gaps = sum(len(gap_list) for gap_list in gaps.values())
        
        # Calculate health score
        health_score = self.calculate_health_score(gaps)
        
        # Build report
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_gaps': total_gaps,
            'health_score': health_score,
            'gaps_by_type': {k: len(v) for k, v in gaps.items()},
            'gap_details': gaps
        }
        
        logger.info(f"✅ Gap scan complete: {total_gaps} gaps detected, health score: {health_score}/100")
        
        return report
    
    def update_health_metrics(self, trade_id: str, gap_flags: Dict) -> None:
        """Update signal_health_metrics table for a specific signal"""
        conn = psycopg2.connect(self.database_url)
        cur = conn.cursor()
        
        # Calculate health score for this signal
        gap_count = sum(1 for v in gap_flags.values() if v)
        health_score = max(0, 100 - (gap_count * 12))  # ~12 points per gap
        
        # Insert or update
        cur.execute("""
            INSERT INTO signal_health_metrics (
                trade_id, health_score, gap_flags, last_check
            ) VALUES (%s, %s, %s, NOW())
            ON CONFLICT (trade_id) DO UPDATE SET
                health_score = EXCLUDED.health_score,
                gap_flags = EXCLUDED.gap_flags,
                last_check = NOW(),
                updated_at = NOW()
        """, (trade_id, health_score, psycopg2.extras.Json(gap_flags)))
        
        conn.commit()
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Test gap detection
    detector = GapDetector()
    report = detector.run_complete_scan()
    
    print("=" * 80)
    print("GAP DETECTION REPORT")
    print("=" * 80)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Health Score: {report['health_score']}/100")
    print(f"Total Gaps: {report['total_gaps']}")
    print()
    print("Gaps by Type:")
    for gap_type, count in report['gaps_by_type'].items():
        if count > 0:
            print(f"  {gap_type}: {count}")

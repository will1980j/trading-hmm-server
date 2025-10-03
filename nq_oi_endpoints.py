"""NQ Options OI endpoints for web_server.py integration"""

import json
import hashlib
from datetime import datetime, date
from typing import List, Dict, Optional
import asyncio
import sqlite3
from dataclasses import dataclass

@dataclass
class OIStrike:
    expiry_date: date
    dte: int
    strike: float
    call_oi: int
    put_oi: int
    total_oi: int

@dataclass
class OIFeatures:
    nearest_expiry_date: date
    nearest_dte: int
    top_put_strikes: List[Dict]
    top_call_strikes: List[Dict]
    pin_candidate_strike: Optional[float]

class NQOIProcessor:
    def __init__(self, db_path='trading_data.db'):
        self.db_path = db_path
        self.min_oi_threshold = 1000
        self.top_n_strikes = 3
        self.init_db()

    def init_db(self):
        """Initialize SQLite tables for NQ OI data"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS nq_oi_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    payload TEXT NOT NULL,
                    hash TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS nq_oi_strikes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expiry_date DATE NOT NULL,
                    dte INTEGER NOT NULL,
                    strike REAL NOT NULL,
                    call_oi INTEGER DEFAULT 0,
                    put_oi INTEGER DEFAULT 0,
                    total_oi INTEGER DEFAULT 0,
                    snapshot_id INTEGER REFERENCES nq_oi_snapshots(id)
                );
                
                CREATE TABLE IF NOT EXISTS nq_oi_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    nearest_expiry_date DATE NOT NULL,
                    nearest_dte INTEGER NOT NULL,
                    top_put_strikes TEXT NOT NULL,
                    top_call_strikes TEXT NOT NULL,
                    pin_candidate_strike REAL,
                    rules_version TEXT DEFAULT 'v1.0'
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def compute_features(self, strikes: List[OIStrike]) -> OIFeatures:
        """Compute OI features from raw strikes"""
        if not strikes:
            return OIFeatures(date.today(), 0, [], [], None)
        
        # Find nearest expiry (smallest DTE >= 0)
        valid_strikes = [s for s in strikes if s.dte >= 0]
        if not valid_strikes:
            return OIFeatures(date.today(), 0, [], [], None)
            
        nearest_dte = min(s.dte for s in valid_strikes)
        nearest_strikes = [s for s in valid_strikes if s.dte == nearest_dte]
        
        # Filter by minimum OI threshold
        filtered_strikes = [s for s in nearest_strikes if s.total_oi >= self.min_oi_threshold]
        
        # Top put strikes (highest put OI)
        top_puts = sorted(filtered_strikes, key=lambda x: x.put_oi, reverse=True)[:self.top_n_strikes]
        top_put_strikes = [{"strike": s.strike, "oi": s.put_oi} for s in top_puts]
        
        # Top call strikes (highest call OI)
        top_calls = sorted(filtered_strikes, key=lambda x: x.call_oi, reverse=True)[:self.top_n_strikes]
        top_call_strikes = [{"strike": s.strike, "oi": s.call_oi} for s in top_calls]
        
        # Pin candidate (max total OI for DTE 0)
        pin_candidate = None
        if nearest_dte == 0 and filtered_strikes:
            max_total_oi_strike = max(filtered_strikes, key=lambda x: x.total_oi)
            pin_candidate = max_total_oi_strike.strike
        
        return OIFeatures(
            nearest_expiry_date=date.today(),
            nearest_dte=nearest_dte,
            top_put_strikes=top_put_strikes,
            top_call_strikes=top_call_strikes,
            pin_candidate_strike=pin_candidate
        )

    def store_mock_data(self):
        """Store mock NQ OI data for testing"""
        mock_strikes = [
            OIStrike(date.today(), 0, 20800.0, 5200, 8900, 14100),
            OIStrike(date.today(), 0, 20825.0, 4800, 7200, 12000),
            OIStrike(date.today(), 0, 20850.0, 6100, 5800, 11900),
            OIStrike(date.today(), 0, 20875.0, 7300, 4200, 11500),
            OIStrike(date.today(), 0, 20900.0, 8900, 3100, 12000),
            OIStrike(date.today(), 1, 20800.0, 3200, 6900, 10100),
            OIStrike(date.today(), 1, 20825.0, 2800, 5200, 8000),
        ]
        
        features = self.compute_features(mock_strikes)
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Store snapshot
            payload = json.dumps([{
                'expiry_date': s.expiry_date.isoformat(),
                'dte': s.dte,
                'strike': s.strike,
                'call_oi': s.call_oi,
                'put_oi': s.put_oi,
                'total_oi': s.total_oi
            } for s in mock_strikes])
            
            payload_hash = hashlib.md5(payload.encode()).hexdigest()
            
            cursor = conn.execute(
                "INSERT INTO nq_oi_snapshots (payload, hash) VALUES (?, ?)",
                (payload, payload_hash)
            )
            snapshot_id = cursor.lastrowid
            
            # Store strikes
            for strike in mock_strikes:
                conn.execute("""
                    INSERT INTO nq_oi_strikes (expiry_date, dte, strike, call_oi, put_oi, total_oi, snapshot_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (strike.expiry_date.isoformat(), strike.dte, strike.strike, 
                     strike.call_oi, strike.put_oi, strike.total_oi, snapshot_id))
            
            # Store features
            conn.execute("""
                INSERT INTO nq_oi_features (nearest_expiry_date, nearest_dte, top_put_strikes, 
                                          top_call_strikes, pin_candidate_strike, rules_version)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (features.nearest_expiry_date.isoformat(), features.nearest_dte,
                 json.dumps(features.top_put_strikes), json.dumps(features.top_call_strikes),
                 features.pin_candidate_strike, 'v1.0'))
            
            conn.commit()
            return True
        finally:
            conn.close()

    def get_daily_levels(self):
        """Get daily NQ OI levels for overlay"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("""
                SELECT * FROM nq_oi_features 
                ORDER BY computed_at DESC LIMIT 1
            """)
            row = cursor.fetchone()
            
            if not row:
                # Store mock data if none exists
                self.store_mock_data()
                cursor = conn.execute("""
                    SELECT * FROM nq_oi_features 
                    ORDER BY computed_at DESC LIMIT 1
                """)
                row = cursor.fetchone()
            
            if row:
                return {
                    "date": datetime.now().date().isoformat(),
                    "nearest_dte": row[3],
                    "top_puts": json.loads(row[4]),
                    "top_calls": json.loads(row[5]),
                    "pin_candidate": row[6],
                    "rules_version": row[7] or 'v1.0',
                    "generated_at": datetime.now().isoformat()
                }
            
            return None
        finally:
            conn.close()

# Global processor instance
nq_oi_processor = NQOIProcessor()
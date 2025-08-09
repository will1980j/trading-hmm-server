import sqlite3
import json
from datetime import datetime
from typing import Dict, List

class SQLiteDB:
    def __init__(self, db_path="trading_data.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.setup_tables()
    
    def setup_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                open REAL, high REAL, low REAL, close REAL, volume INTEGER,
                timeframe TEXT DEFAULT '1m',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                entry_price REAL,
                stop_loss REAL,
                take_profit REAL,
                confidence REAL,
                reason TEXT,
                status TEXT DEFAULT 'active',
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS ict_levels (
                id INTEGER PRIMARY KEY,
                symbol TEXT NOT NULL,
                level_type TEXT NOT NULL,
                price_high REAL,
                price_low REAL,
                strength REAL,
                active INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol, timestamp)')
        self.conn.commit()
    
    def store_market_data(self, symbol: str, data: Dict):
        self.conn.execute('''
            INSERT OR REPLACE INTO market_data 
            (symbol, timestamp, open, high, low, close, volume, timeframe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            datetime.now().isoformat(),
            data.get('open', 0),
            data.get('high', 0),
            data.get('low', 0),
            data.get('close', 0),
            data.get('volume', 0),
            data.get('timeframe', '1m')
        ))
        self.conn.commit()
        return {"status": "success"}
    
    def get_recent_data(self, symbol: str, limit: int = 100):
        cursor = self.conn.execute('''
            SELECT * FROM market_data 
            WHERE symbol = ? 
            ORDER BY timestamp DESC LIMIT ?
        ''', (symbol, limit))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        
        return type('Result', (), {'data': data})()
    
    def store_signal(self, signal: Dict):
        self.conn.execute('''
            INSERT INTO trading_signals 
            (symbol, signal_type, entry_price, stop_loss, take_profit, confidence, reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal.get('symbol'),
            signal.get('type'),
            signal.get('entry', 0),
            signal.get('stop_loss', 0),
            signal.get('take_profit', 0),
            signal.get('confidence', 0),
            signal.get('reason', ''),
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return {"status": "success"}
    
    def store_ict_level(self, level: Dict):
        self.conn.execute('''
            INSERT INTO ict_levels 
            (symbol, level_type, price_high, price_low, strength, active, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            level.get('symbol'),
            level.get('type'),
            level.get('top', 0),
            level.get('bottom', 0),
            level.get('strength', 0),
            1 if level.get('active', True) else 0,
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return {"status": "success"}
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict

class RailwayDB:
    def __init__(self):
        # Railway automatically provides DATABASE_URL
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise Exception("DATABASE_URL not found - add PostgreSQL service in Railway")
        
        self.conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
        self.setup_tables()
    
    def setup_tables(self):
        with self.conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    open DECIMAL(12,4),
                    high DECIMAL(12,4),
                    low DECIMAL(12,4),
                    close DECIMAL(12,4),
                    volume BIGINT,
                    timeframe VARCHAR(5) DEFAULT '1m',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    signal_type VARCHAR(10) NOT NULL,
                    entry_price DECIMAL(12,4),
                    confidence DECIMAL(3,2),
                    reason TEXT,
                    timestamp TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS ict_levels (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    level_type VARCHAR(20) NOT NULL,
                    price_high DECIMAL(12,4),
                    price_low DECIMAL(12,4),
                    strength DECIMAL(3,2),
                    active BOOLEAN DEFAULT TRUE,
                    timestamp TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            cur.execute('''
                CREATE TABLE IF NOT EXISTS prop_firms (
                    id SERIAL PRIMARY KEY,
                    firm_name VARCHAR(100) NOT NULL,
                    website VARCHAR(200),
                    status VARCHAR(20) NOT NULL,
                    market_type VARCHAR(20),
                    account_size DECIMAL(15,2),
                    max_funding DECIMAL(15,2),
                    profit_split DECIMAL(5,2),
                    currency VARCHAR(5),
                    monthly_profit DECIMAL(15,2) DEFAULT 0,
                    month_year VARCHAR(7) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            # Indexes
            cur.execute('CREATE INDEX IF NOT EXISTS idx_market_data_symbol_time ON market_data(symbol, timestamp DESC)')
            
        self.conn.commit()
    
    def store_market_data(self, symbol: str, data: Dict):
        with self.conn.cursor() as cur:
            cur.execute('''
                INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume, timeframe)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                symbol,
                datetime.now(),
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
        with self.conn.cursor() as cur:
            cur.execute('''
                SELECT * FROM market_data 
                WHERE symbol = %s 
                ORDER BY timestamp DESC LIMIT %s
            ''', (symbol, limit))
            
            data = cur.fetchall()
            return type('Result', (), {'data': data})()
    
    def store_signal(self, signal: Dict):
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO trading_signals (symbol, signal_type, entry_price, confidence, reason, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    signal.get('symbol'),
                    signal.get('type'),
                    signal.get('entry', 0),
                    signal.get('confidence', 0),
                    signal.get('reason', ''),
                    datetime.now()
                ))
            self.conn.commit()
            return {"status": "success"}
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def store_ict_level(self, level: Dict):
        with self.conn.cursor() as cur:
            cur.execute('''
                INSERT INTO ict_levels (symbol, level_type, price_high, price_low, strength, active, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                level.get('symbol'),
                level.get('type'),
                level.get('top', 0),
                level.get('bottom', 0),
                level.get('strength', 0),
                level.get('active', True),
                datetime.now()
            ))
        self.conn.commit()
        return {"status": "success"}
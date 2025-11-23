#!/usr/bin/env python3
"""
Automated Contract Rollover Manager
Handles futures contract changes automatically without manual intervention
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from json import dumps, loads
from db_error_handler import auto_fix_db_errors

logger = logging.getLogger(__name__)

# =====================================================================
# MULTI-MARKET INSTRUMENT REGISTRY (Stage 11)
# ---------------------------------------------------------------------
# Centralised mapping for US index futures + their micro counterparts.
# This is purely metadata – no behavioural changes to existing NQ logic.
# =====================================================================
INSTRUMENT_REGISTRY = {
    # Nasdaq 100
    "NQ": {
        "description": "E-mini Nasdaq-100 Futures",
        "root": "NQ",
        "is_micro": False,
        "micro_symbol": "MNQ",
        "tick_size": 0.25,
        "tick_value": 5.0,   # $5 per tick for NQ
        "point_value": 20.0  # 4 ticks per point * $5
    },
    "MNQ": {
        "description": "Micro E-mini Nasdaq-100 Futures",
        "root": "MNQ",
        "is_micro": True,
        "parent_symbol": "NQ",
        "tick_size": 0.25,
        "tick_value": 0.5,   # $0.50 per tick
        "point_value": 2.0
    },
    
    # S&P 500
    "ES": {
        "description": "E-mini S&P 500 Futures",
        "root": "ES",
        "is_micro": False,
        "micro_symbol": "MES",
        "tick_size": 0.25,
        "tick_value": 12.5,
        "point_value": 50.0
    },
    "MES": {
        "description": "Micro E-mini S&P 500 Futures",
        "root": "MES",
        "is_micro": True,
        "parent_symbol": "ES",
        "tick_size": 0.25,
        "tick_value": 1.25,
        "point_value": 5.0
    },
    
    # Dow
    "YM": {
        "description": "E-mini Dow Futures",
        "root": "YM",
        "is_micro": False,
        "micro_symbol": "MYM",
        "tick_size": 1.0,
        "tick_value": 5.0,
        "point_value": 5.0
    },
    "MYM": {
        "description": "Micro E-mini Dow Futures",
        "root": "MYM",
        "is_micro": True,
        "parent_symbol": "YM",
        "tick_size": 1.0,
        "tick_value": 0.5,
        "point_value": 0.5
    },
    
    # Russell 2000
    "RTY": {
        "description": "E-mini Russell 2000 Futures",
        "root": "RTY",
        "is_micro": False,
        "micro_symbol": "M2K",
        "tick_size": 0.1,
        "tick_value": 5.0,
        "point_value": 50.0
    },
    "M2K": {
        "description": "Micro E-mini Russell 2000 Futures",
        "root": "M2K",
        "is_micro": True,
        "parent_symbol": "RTY",
        "tick_size": 0.1,
        "tick_value": 0.5,
        "point_value": 5.0
    },
}


def get_instrument_base_symbol(raw_symbol: str) -> str:
    """
    Given a raw TradingView / exchange symbol (e.g. 'NQ1!', 'MNQH5', 'ESM5'),
    return the logical base symbol key used in INSTRUMENT_REGISTRY
    (e.g. 'NQ', 'MNQ', 'ES', 'MES', 'YM', 'MYM', 'RTY', 'M2K').
    
    This is a pure helper – it does NOT perform any DB or network I/O.
    """
    if not raw_symbol:
        return "NQ"  # default to existing behaviour
    
    sym = str(raw_symbol).upper()
    
    # Normalise common futures roots; keep simple substring rules.
    for root in ("MNQ", "NQ", "MES", "ES", "MYM", "YM", "M2K", "RTY"):
        if root in sym:
            return root
    
    # Fallback: keep legacy behaviour – NQ as default
    return "NQ"


def get_instrument_meta(base_symbol: str) -> dict:
    """
    Return the instrument metadata dict from INSTRUMENT_REGISTRY.
    If unknown, fallback to NQ defaults (to preserve legacy behaviour).
    """
    base = (base_symbol or "NQ").upper()
    meta = INSTRUMENT_REGISTRY.get(base)
    if meta is None:
        return INSTRUMENT_REGISTRY["NQ"].copy()
    # Return a shallow copy to avoid accidental in-place mutation
    return dict(meta)


class ContractManager:
    def __init__(self, db):
        self.db = db
        self.contract_patterns = {
            'NQ': r'NQ[A-Z]?\d{0,2}!?',  # Matches NQ1!, NQZ24, NQU24, etc.
            'MNQ': r'MNQ[A-Z]?\d{0,2}!?',  # Matches MNQ1!, MNQZ24, etc.
            'ES': r'ES[A-Z]?\d{0,2}!?',  # Matches ES1!, ESZ24, ESU24, etc.
            'MES': r'MES[A-Z]?\d{0,2}!?',  # Matches MES1!, MESZ24, etc.
            'YM': r'YM[A-Z]?\d{0,2}!?',  # Matches YM1!, YMZ24, YMU24, etc.
            'MYM': r'MYM[A-Z]?\d{0,2}!?',  # Matches MYM1!, MYMZ24, etc.
            'RTY': r'RTY[A-Z]?\d{0,2}!?', # Matches RTY1!, RTYZ24, etc.
            'M2K': r'M2K[A-Z]?\d{0,2}!?', # Matches M2K1!, M2KZ24, etc.
        }
        
        # Contract month codes
        self.month_codes = {
            'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6,
            'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12
        }
        
        self.active_contracts = self._load_active_contracts()
    
    @auto_fix_db_errors
    def _load_active_contracts(self) -> Dict[str, str]:
        """Load current active contracts from database or initialize defaults"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT contract_data FROM contract_settings 
                WHERE id = 1
            """)
            result = cursor.fetchone()
            
            if result:
                data = result['contract_data']
                # psycopg2 already parses JSONB to dict
                return data if isinstance(data, dict) else loads(data)
            else:
                # Initialize with defaults (Stage 11: added micro contracts)
                defaults = {
                    'NQ': 'NQ1!',
                    'MNQ': 'MNQ1!',
                    'ES': 'ES1!',
                    'MES': 'MES1!',
                    'YM': 'YM1!',
                    'MYM': 'MYM1!',
                    'RTY': 'RTY1!',
                    'M2K': 'M2K1!'
                }
                self._save_active_contracts(defaults)
                return defaults
                
        except Exception as e:
            logger.error(f"Error loading contracts: {e}")
            # Fallback to defaults (Stage 11: added micro contracts)
            return {
                'NQ': 'NQ1!', 'MNQ': 'MNQ1!',
                'ES': 'ES1!', 'MES': 'MES1!',
                'YM': 'YM1!', 'MYM': 'MYM1!',
                'RTY': 'RTY1!', 'M2K': 'M2K1!'
            }
    
    @auto_fix_db_errors
    def _save_active_contracts(self, contracts: Dict[str, str]):
        """Save active contracts to database"""
        try:
            cursor = self.db.conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contract_settings (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    contract_data JSONB NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Upsert the contract data
            cursor.execute("""
                INSERT INTO contract_settings (id, contract_data, updated_at)
                VALUES (1, %s, NOW())
                ON CONFLICT (id) DO UPDATE SET
                contract_data = EXCLUDED.contract_data,
                updated_at = EXCLUDED.updated_at
            """, (dumps(contracts),))
            
            self.db.conn.commit()
            logger.info(f"Saved active contracts: {contracts}")
            
        except Exception as e:
            logger.error(f"Error saving contracts: {e}")
            if hasattr(self.db, 'conn') and self.db.conn:
                self.db.conn.rollback()
    
    def detect_contract_rollover(self, incoming_symbol: str) -> Optional[Dict]:
        """
        Detect if incoming symbol represents a contract rollover
        Returns rollover info if detected, None otherwise
        """
        # Extract base symbol (NQ, ES, etc.)
        base_symbol = self._extract_base_symbol(incoming_symbol)
        if not base_symbol:
            return None
        
        current_contract = self.active_contracts.get(base_symbol)
        if not current_contract:
            return None
        
        # If symbols are the same, no rollover
        if incoming_symbol == current_contract:
            return None
        
        # Check if this is a valid contract format
        if not self._is_valid_contract_format(incoming_symbol, base_symbol):
            return None
        
        # Determine if this is a rollover (newer contract)
        if self._is_newer_contract(incoming_symbol, current_contract):
            return {
                'base_symbol': base_symbol,
                'old_contract': current_contract,
                'new_contract': incoming_symbol,
                'rollover_detected': True,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _extract_base_symbol(self, symbol: str) -> Optional[str]:
        """Extract base symbol (NQ, ES, etc.) from contract symbol"""
        for base, pattern in self.contract_patterns.items():
            if re.match(pattern, symbol):
                return base
        return None
    
    def _is_valid_contract_format(self, symbol: str, base_symbol: str) -> bool:
        """Check if symbol follows valid futures contract format"""
        pattern = self.contract_patterns.get(base_symbol)
        return bool(pattern and re.match(pattern, symbol))
    
    def _is_newer_contract(self, new_symbol: str, current_symbol: str) -> bool:
        """
        Determine if new_symbol represents a newer contract than current_symbol
        """
        try:
            # Extract contract info
            new_info = self._parse_contract_symbol(new_symbol)
            current_info = self._parse_contract_symbol(current_symbol)
            
            if not new_info or not current_info:
                return False
            
            # If one is generic (like NQ1!) and other is specific, prefer specific
            if current_info['is_generic'] and not new_info['is_generic']:
                return True
            
            if new_info['is_generic'] and not current_info['is_generic']:
                return False
            
            # Both are specific contracts - compare dates
            if not new_info['is_generic'] and not current_info['is_generic']:
                new_expiry = self._get_contract_expiry(new_info)
                current_expiry = self._get_contract_expiry(current_info)
                
                if new_expiry and current_expiry:
                    return new_expiry > current_expiry
            
            return False
            
        except Exception as e:
            logger.error(f"Error comparing contracts: {e}")
            return False
    
    def _parse_contract_symbol(self, symbol: str) -> Optional[Dict]:
        """Parse contract symbol into components"""
        try:
            # Generic contracts (NQ1!, ES1!, etc.)
            if symbol.endswith('1!'):
                return {
                    'base': symbol[:-2],
                    'is_generic': True,
                    'month_code': None,
                    'year': None
                }
            
            # Specific contracts (NQZ24, ESU24, etc.)
            match = re.match(r'([A-Z]+)([A-Z])(\d{2})!?', symbol)
            if match:
                base, month_code, year = match.groups()
                return {
                    'base': base,
                    'is_generic': False,
                    'month_code': month_code,
                    'year': int(year)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing contract symbol {symbol}: {e}")
            return None
    
    def _get_contract_expiry(self, contract_info: Dict) -> Optional[datetime]:
        """Get contract expiry date"""
        try:
            if contract_info['is_generic']:
                return None
            
            month_code = contract_info['month_code']
            year = contract_info['year']
            
            if month_code not in self.month_codes:
                return None
            
            month = self.month_codes[month_code]
            
            # Convert 2-digit year to 4-digit (assume 20xx for now)
            full_year = 2000 + year if year < 50 else 1900 + year
            
            # Futures typically expire on the third Friday of the month
            # Simplified: use 15th of the month
            return datetime(full_year, month, 15)
            
        except Exception as e:
            logger.error(f"Error calculating expiry: {e}")
            return None
    
    def handle_rollover(self, rollover_info: Dict) -> bool:
        """
        Handle contract rollover automatically
        """
        try:
            base_symbol = rollover_info['base_symbol']
            old_contract = rollover_info['old_contract']
            new_contract = rollover_info['new_contract']
            
            logger.info(f"🔄 HANDLING CONTRACT ROLLOVER: {old_contract} → {new_contract}")
            
            # Update active contracts
            self.active_contracts[base_symbol] = new_contract
            self._save_active_contracts(self.active_contracts)
            
            # Log the rollover event
            self._log_rollover_event(rollover_info)
            
            # Update any existing signals/trades with old contract
            self._update_historical_data(old_contract, new_contract)
            
            logger.info(f"✅ Contract rollover completed: {base_symbol} now uses {new_contract}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling rollover: {e}")
            return False
    
    @auto_fix_db_errors
    def _log_rollover_event(self, rollover_info: Dict):
        """Log rollover event to database"""
        try:
            cursor = self.db.conn.cursor()
            
            # Create rollover log table if needed
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contract_rollover_log (
                    id SERIAL PRIMARY KEY,
                    base_symbol VARCHAR(10) NOT NULL,
                    old_contract VARCHAR(20) NOT NULL,
                    new_contract VARCHAR(20) NOT NULL,
                    rollover_data JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            cursor.execute("""
                INSERT INTO contract_rollover_log 
                (base_symbol, old_contract, new_contract, rollover_data)
                VALUES (%s, %s, %s, %s)
            """, (
                rollover_info['base_symbol'],
                rollover_info['old_contract'], 
                rollover_info['new_contract'],
                dumps(rollover_info)
            ))
            
            self.db.conn.commit()
            
        except Exception as e:
            logger.error(f"Error logging rollover: {e}")
    
    @auto_fix_db_errors
    def _update_historical_data(self, old_contract: str, new_contract: str):
        """Update historical data with new contract symbol"""
        try:
            cursor = self.db.conn.cursor()
            
            # Update live_signals table
            cursor.execute("""
                UPDATE live_signals 
                SET symbol = %s 
                WHERE symbol = %s 
                AND timestamp > NOW() - INTERVAL '7 days'
            """, (new_contract, old_contract))
            
            updated_signals = cursor.rowcount
            
            # Update recent signal_lab_trades
            cursor.execute("""
                UPDATE signal_lab_trades 
                SET signal_type = REPLACE(signal_type, %s, %s)
                WHERE signal_type LIKE %s
                AND created_at > NOW() - INTERVAL '7 days'
            """, (old_contract, new_contract, f'%{old_contract}%'))
            
            updated_trades = cursor.rowcount
            
            self.db.conn.commit()
            
            logger.info(f"Updated {updated_signals} signals and {updated_trades} trades with new contract")
            
        except Exception as e:
            logger.error(f"Error updating historical data: {e}")
            if hasattr(self.db, 'conn') and self.db.conn:
                self.db.conn.rollback()
    
    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize incoming symbol to current active contract
        """
        base_symbol = self._extract_base_symbol(symbol)
        if base_symbol and base_symbol in self.active_contracts:
            return self.active_contracts[base_symbol]
        return symbol
    
    def process_incoming_signal(self, signal_data: Dict) -> Dict:
        """
        Process incoming signal and handle any contract rollovers
        Returns updated signal data with normalized symbol
        
        Stage 11: Now adds base_symbol, normalized_symbol, and instrument_meta fields
        """
        try:
            original_symbol = signal_data.get('symbol', '')
            raw_symbol = str(original_symbol)
            
            # Stage 11: Extract base symbol and metadata
            base_symbol = get_instrument_base_symbol(raw_symbol)
            meta = get_instrument_meta(base_symbol)
            
            # Stage 11: Compute normalized_symbol for backward compatibility
            normalized = None
            raw_upper = raw_symbol.upper()
            if "NQ" in raw_upper and "MNQ" not in raw_upper:
                normalized = "NQ1!"
            elif "MNQ" in raw_upper:
                normalized = "MNQ1!"
            elif "ES" in raw_upper and "MES" not in raw_upper:
                normalized = "ES1!"
            elif "MES" in raw_upper:
                normalized = "MES1!"
            elif "YM" in raw_upper and "MYM" not in raw_upper:
                normalized = "YM1!"
            elif "MYM" in raw_upper:
                normalized = "MYM1!"
            elif "RTY" in raw_upper:
                normalized = "RTY1!"
            elif "M2K" in raw_upper:
                normalized = "M2K1!"
            elif "DXY" in raw_upper:
                normalized = "DXY"
            else:
                normalized = "NQ1!"  # legacy fallback
            
            # Stage 11: Add new fields
            signal_data["base_symbol"] = base_symbol
            signal_data["normalized_symbol"] = normalized
            signal_data["instrument_meta"] = meta
            
            # Check for rollover
            rollover_info = self.detect_contract_rollover(original_symbol)
            
            if rollover_info:
                # Stage 11: Add base_symbol to rollover_info
                rollover_info["base_symbol"] = base_symbol
                rollover_info["raw_symbol"] = raw_symbol
                
                logger.info(
                    f"🔄 CONTRACT ROLLOVER: base={base_symbol} old={rollover_info.get('old_contract')} "
                    f"new={rollover_info.get('new_contract')} (raw={raw_symbol})"
                )
                
                # Handle the rollover
                if self.handle_rollover(rollover_info):
                    # Update signal with new contract
                    signal_data['symbol'] = rollover_info['new_contract']
                    signal_data['contract_rollover'] = True
                    signal_data['original_symbol'] = original_symbol
            else:
                # Normalize to current active contract
                normalized_contract = self.normalize_symbol(original_symbol)
                if normalized_contract != original_symbol:
                    signal_data['symbol'] = normalized_contract
                    signal_data['symbol_normalized'] = True
                    signal_data['original_symbol'] = original_symbol
            
            return signal_data
            
        except Exception as e:
            logger.error(f"Error processing signal: {e}")
            return signal_data
    
    def get_active_contract(self, base_symbol: str) -> Optional[str]:
        """Get current active contract for base symbol"""
        return self.active_contracts.get(base_symbol)
    
    def get_all_active_contracts(self) -> Dict[str, str]:
        """Get all active contracts"""
        return self.active_contracts.copy()
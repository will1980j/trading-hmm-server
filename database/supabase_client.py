import os
import json
from datetime import datetime
from supabase import create_client, Client
from typing import Dict, List, Optional

class SupabaseDB:
    def __init__(self):
        url = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
        key = os.getenv('SUPABASE_ANON_KEY', 'your-anon-key')
        self.supabase: Client = create_client(url, key)
    
    def store_market_data(self, symbol: str, data: Dict):
        """Store market data"""
        return self.supabase.table('market_data').insert({
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'open': data.get('open', 0),
            'high': data.get('high', 0),
            'low': data.get('low', 0),
            'close': data.get('close', 0),
            'volume': data.get('volume', 0),
            'timeframe': data.get('timeframe', '1m')
        }).execute()
    
    def get_recent_data(self, symbol: str, limit: int = 100):
        """Get recent market data"""
        return self.supabase.table('market_data')\
            .select('*')\
            .eq('symbol', symbol)\
            .order('timestamp', desc=True)\
            .limit(limit)\
            .execute()
    
    def store_signal(self, signal: Dict):
        """Store trading signal"""
        return self.supabase.table('trading_signals').insert({
            'symbol': signal.get('symbol'),
            'signal_type': signal.get('type'),
            'entry_price': signal.get('entry', 0),
            'stop_loss': signal.get('stop_loss', 0),
            'take_profit': signal.get('take_profit', 0),
            'confidence': signal.get('confidence', 0),
            'reason': signal.get('reason', ''),
            'timestamp': datetime.now().isoformat()
        }).execute()
    
    def get_active_signals(self):
        """Get active trading signals"""
        return self.supabase.table('trading_signals')\
            .select('*')\
            .eq('status', 'active')\
            .order('timestamp', desc=True)\
            .execute()
    
    def store_ict_level(self, level: Dict):
        """Store ICT level"""
        return self.supabase.table('ict_levels').insert({
            'symbol': level.get('symbol'),
            'level_type': level.get('type'),
            'price_high': level.get('top', 0),
            'price_low': level.get('bottom', 0),
            'strength': level.get('strength', 0),
            'active': level.get('active', True),
            'timestamp': datetime.now().isoformat()
        }).execute()
    
    def get_active_levels(self, symbol: str):
        """Get active ICT levels"""
        return self.supabase.table('ict_levels')\
            .select('*')\
            .eq('symbol', symbol)\
            .eq('active', True)\
            .execute()
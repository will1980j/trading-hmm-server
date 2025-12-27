"""
Phase B Module 3: HTF Bias Calculation
Exact replication of Pine request.security() semantics for HTF bias computation

Key behaviors replicated:
1. Each HTF has independent BiasEngine instance
2. HTF bars aggregate from 1m bars with correct OHLC
3. HTF bias updates ONLY on HTF bar close
4. HTF bias forward-fills to all 1m bars until next HTF close
5. No lookahead, no repaint
"""

from datetime import datetime, timedelta
from typing import Dict, Callable
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

class HTFBiasEngine:
    """
    HTF Bias Engine with request.security() parity
    
    Maintains independent bias engines for each HTF and aggregates 1m bars correctly.
    """
    
    def __init__(self, bias_engine_factory: Callable = None):
        """
        Initialize HTF bias engine
        
        Args:
            bias_engine_factory: Factory function to create BiasEngine instances
                                Default: BiasEngineFvgIfvg
        """
        if bias_engine_factory is None:
            bias_engine_factory = BiasEngineFvgIfvg
        
        # Independent bias engine per timeframe
        self.engines = {
            '1D': bias_engine_factory(),
            '4H': bias_engine_factory(),
            '1H': bias_engine_factory(),
            '15M': bias_engine_factory(),
            '5M': bias_engine_factory()
        }
        
        # Current aggregating HTF bar (None = not started)
        self.current_htf_bars = {
            '1D': None,
            '4H': None,
            '1H': None,
            '15M': None,
            '5M': None
        }
        
        # Last confirmed HTF bias (forward-filled)
        self.last_biases = {
            '1D': "Neutral",
            '4H': "Neutral",
            '1H': "Neutral",
            '15M': "Neutral",
            '5M': "Neutral"
        }
        
        # Track last HTF bar close time for each timeframe
        self.last_htf_close = {
            '1D': None,
            '4H': None,
            '1H': None,
            '15M': None,
            '5M': None
        }
    
    def _is_htf_bar_close(self, ts: datetime, timeframe: str) -> bool:
        """
        Check if this 1m bar timestamp closes an HTF bar
        
        HTF bar close times (UTC):
        - 5M: minute ends in 4, 9, 14, 19, ... (every 5 minutes)
        - 15M: minute ends in 14, 29, 44, 59 (every 15 minutes)
        - 1H: minute = 59 (every hour)
        - 4H: minute = 59 AND hour % 4 == 3 (00:00, 04:00, 08:00, 12:00, 16:00, 20:00)
        - 1D: hour = 23 AND minute = 59 (end of UTC day)
        
        Args:
            ts: 1-minute bar timestamp (UTC)
            timeframe: '5M', '15M', '1H', '4H', or '1D'
        
        Returns:
            True if this 1m bar closes the HTF bar
        """
        minute = ts.minute
        hour = ts.hour
        
        if timeframe == '5M':
            return minute % 5 == 4
        elif timeframe == '15M':
            return minute % 15 == 14
        elif timeframe == '1H':
            return minute == 59
        elif timeframe == '4H':
            return minute == 59 and hour % 4 == 3
        elif timeframe == '1D':
            return hour == 23 and minute == 59
        
        return False
    
    def _aggregate_1m_into_htf(self, bar_1m: dict, timeframe: str):
        """
        Aggregate 1-minute bar into HTF bar
        
        OHLC aggregation rules:
        - Open: first bar's open in HTF period
        - High: max of all highs in HTF period
        - Low: min of all lows in HTF period
        - Close: last bar's close in HTF period
        
        Args:
            bar_1m: 1-minute bar dict with ts, open, high, low, close
            timeframe: HTF timeframe key
        """
        current = self.current_htf_bars[timeframe]
        
        if current is None:
            # Start new HTF bar
            self.current_htf_bars[timeframe] = {
                'ts': bar_1m['ts'],
                'open': bar_1m['open'],
                'high': bar_1m['high'],
                'low': bar_1m['low'],
                'close': bar_1m['close']
            }
        else:
            # Update aggregating HTF bar
            current['high'] = max(current['high'], bar_1m['high'])
            current['low'] = min(current['low'], bar_1m['low'])
            current['close'] = bar_1m['close']
            # Open stays as first bar's open
    
    def update_ltf_bar(self, bar_1m: dict) -> Dict[str, str]:
        """
        Process 1-minute bar and return current HTF biases
        
        Behavior:
        1. Aggregate 1m bar into each HTF bar
        2. If HTF bar closes, update that HTF's bias engine
        3. Forward-fill last confirmed HTF bias
        
        Args:
            bar_1m: dict with keys: ts (datetime), open, high, low, close
        
        Returns:
            dict with keys: daily_bias, h4_bias, h1_bias, m15_bias, m5_bias
        """
        ts = bar_1m['ts']
        
        # Process each timeframe in order (smallest to largest)
        for tf in ['5M', '15M', '1H', '4H', '1D']:
            # Aggregate this 1m bar into HTF bar
            self._aggregate_1m_into_htf(bar_1m, tf)
            
            # Check if HTF bar closes on this 1m bar
            if self._is_htf_bar_close(ts, tf):
                htf_bar = self.current_htf_bars[tf]
                
                if htf_bar is not None:
                    # Update HTF bias engine with completed HTF bar
                    bias = self.engines[tf].update(htf_bar)
                    self.last_biases[tf] = bias
                    self.last_htf_close[tf] = ts
                    
                    # Reset HTF bar for next period
                    self.current_htf_bars[tf] = None
        
        # Return current (forward-filled) HTF biases
        return {
            'daily_bias': self.last_biases['1D'],
            'h4_bias': self.last_biases['4H'],
            'h1_bias': self.last_biases['1H'],
            'm15_bias': self.last_biases['15M'],
            'm5_bias': self.last_biases['5M']
        }

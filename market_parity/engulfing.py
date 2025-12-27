"""
Phase B - Module 1: Engulfing Detection
Exact Pine Script parity - no tolerances, no modifications
"""

from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Bar:
    """Immutable OHLC bar"""
    open: float
    high: float
    low: float
    close: float
    
    def __post_init__(self):
        if any(x is None or math.isnan(x) for x in [self.open, self.high, self.low, self.close]):
            raise ValueError("All OHLC values must be non-None and non-NaN")

@dataclass(frozen=True)
class EngulfingResult:
    """Engulfing detection result"""
    bullish: bool
    bearish: bool
    bullish_sweep: bool
    bearish_sweep: bool

def detect_engulfing(prev: Bar, curr: Bar) -> EngulfingResult:
    """
    Detect engulfing patterns (exact Pine Script logic)
    
    Bearish engulfing:
        curr_close < curr_open
        prev_close > prev_open
        curr_open >= prev_close
        curr_close < prev_open
    
    Bullish engulfing:
        curr_close > curr_open
        prev_close < prev_open
        curr_open <= prev_close
        curr_close > prev_open
    
    Sweep engulfing adds:
        Bearish: bearish_engulfing AND curr_high > prev_high AND curr_close < prev_close
        Bullish: bullish_engulfing AND curr_low < prev_low AND curr_close > prev_close
    
    Args:
        prev: Previous bar
        curr: Current bar
    
    Returns:
        EngulfingResult with all four flags
    """
    # Bearish engulfing
    bearish = (
        curr.close < curr.open and
        prev.close > prev.open and
        curr.open >= prev.close and
        curr.close < prev.open
    )
    
    # Bullish engulfing
    bullish = (
        curr.close > curr.open and
        prev.close < prev.open and
        curr.open <= prev.close and
        curr.close > prev.open
    )
    
    # Bearish sweep engulfing
    bearish_sweep = (
        bearish and
        curr.high > prev.high and
        curr.close < prev.close
    )
    
    # Bullish sweep engulfing
    bullish_sweep = (
        bullish and
        curr.low < prev.low and
        curr.close > prev.close
    )
    
    return EngulfingResult(
        bullish=bullish,
        bearish=bearish,
        bullish_sweep=bullish_sweep,
        bearish_sweep=bearish_sweep
    )

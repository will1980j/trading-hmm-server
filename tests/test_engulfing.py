"""
Unit tests for engulfing detection (Phase B Module 1)
"""

import pytest
import sys
sys.path.append('.')
from market_parity.engulfing import Bar, EngulfingResult, detect_engulfing

def test_bullish_engulfing_basic():
    """Basic bullish engulfing: green curr engulfs red prev"""
    prev = Bar(open=100, high=102, low=98, close=99)  # Red candle
    curr = Bar(open=98.5, high=103, low=97, close=101)  # Green engulfs
    result = detect_engulfing(prev, curr)
    assert result.bullish == True
    assert result.bearish == False

def test_bearish_engulfing_basic():
    """Basic bearish engulfing: red curr engulfs green prev"""
    prev = Bar(open=100, high=102, low=98, close=101)  # Green candle
    curr = Bar(open=102, high=103, low=97, close=99)  # Red engulfs
    result = detect_engulfing(prev, curr)
    assert result.bearish == True
    assert result.bullish == False

def test_bullish_engulfing_boundary_open_equals_prev_close():
    """Bullish engulfing allows curr_open == prev_close (<=)"""
    prev = Bar(open=100, high=101, low=99, close=99.5)  # Red
    curr = Bar(open=99.5, high=102, low=98, close=101)  # Green, open == prev_close
    result = detect_engulfing(prev, curr)
    assert result.bullish == True

def test_bearish_engulfing_boundary_open_equals_prev_close():
    """Bearish engulfing allows curr_open == prev_close (>=)"""
    prev = Bar(open=100, high=101, low=99, close=100.5)  # Green
    curr = Bar(open=100.5, high=102, low=98, close=99)  # Red, open == prev_close
    result = detect_engulfing(prev, curr)
    assert result.bearish == True

def test_bullish_sweep_engulfing():
    """Bullish sweep: engulfing + curr_low < prev_low + curr_close > prev_close"""
    prev = Bar(open=100, high=102, low=98, close=99)  # Red
    curr = Bar(open=98, high=103, low=97, close=101)  # Green, low sweeps below prev
    result = detect_engulfing(prev, curr)
    assert result.bullish == True
    assert result.bullish_sweep == True

def test_bearish_sweep_engulfing():
    """Bearish sweep: engulfing + curr_high > prev_high + curr_close < prev_close"""
    prev = Bar(open=100, high=102, low=98, close=101)  # Green
    curr = Bar(open=102.5, high=104, low=97, close=99)  # Red, high sweeps above prev
    result = detect_engulfing(prev, curr)
    assert result.bearish == True
    assert result.bearish_sweep == True

def test_engulfing_true_but_sweep_false_bullish():
    """Bullish engulfing but NOT sweep (missing low sweep)"""
    prev = Bar(open=100, high=102, low=98, close=99)  # Red
    curr = Bar(open=98.5, high=103, low=98.5, close=101)  # Green, but low >= prev_low
    result = detect_engulfing(prev, curr)
    assert result.bullish == True
    assert result.bullish_sweep == False  # No sweep because curr_low >= prev_low

def test_engulfing_true_but_sweep_false_bearish():
    """Bearish engulfing but NOT sweep (missing high sweep)"""
    prev = Bar(open=100, high=102, low=98, close=101)  # Green
    curr = Bar(open=102, high=102, low=97, close=99)  # Red, but high <= prev_high
    result = detect_engulfing(prev, curr)
    assert result.bearish == True
    assert result.bearish_sweep == False  # No sweep because curr_high <= prev_high

def test_wick_condition_true_but_no_engulfing():
    """Wick condition met but NOT engulfing (must not flag sweep)"""
    prev = Bar(open=100, high=102, low=98, close=99)  # Red
    curr = Bar(open=99.5, high=101, low=97, close=99.8)  # Low sweeps but doesn't engulf
    result = detect_engulfing(prev, curr)
    assert result.bullish == False  # Not engulfing
    assert result.bullish_sweep == False  # No sweep without engulfing

def test_no_engulfing():
    """No engulfing pattern"""
    prev = Bar(open=100, high=102, low=98, close=101)
    curr = Bar(open=101, high=103, low=100, close=102)
    result = detect_engulfing(prev, curr)
    assert result.bullish == False
    assert result.bearish == False
    assert result.bullish_sweep == False
    assert result.bearish_sweep == False

def test_invalid_bar_raises():
    """Invalid bar with None/NaN raises ValueError"""
    with pytest.raises(ValueError):
        Bar(open=None, high=100, low=98, close=99)
    
    with pytest.raises(ValueError):
        Bar(open=100, high=float('nan'), low=98, close=99)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

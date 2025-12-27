"""
Phase B Module 5: Signal Generation
Pure function - generates triangle signals from bias and filters

Canonical Pine logic:
fvg_bull_signal = bias != bias[1] and bias == "Bullish" and (not htf_aligned_only or htf_bullish)
fvg_bear_signal = bias != bias[1] and bias == "Bearish" and (not htf_aligned_only or htf_bearish)

show_bull_triangle = require_sweep_engulfing ? (fvg_bull_signal and bullish_sweep_engulfing) : 
                     require_engulfing ? (fvg_bull_signal and bullish_engulfing) : 
                     fvg_bull_signal

show_bear_triangle = require_sweep_engulfing ? (fvg_bear_signal and bearish_sweep_engulfing) : 
                     require_engulfing ? (fvg_bear_signal and bearish_engulfing) : 
                     fvg_bear_signal
"""

from typing import Dict

def generate_signals(
    bias: str,
    bias_prev: str,
    htf_bullish: bool,
    htf_bearish: bool,
    bullish_engulfing: bool,
    bearish_engulfing: bool,
    bullish_sweep_engulfing: bool,
    bearish_sweep_engulfing: bool,
    htf_aligned_only: bool,
    require_engulfing: bool,
    require_sweep_engulfing: bool
) -> Dict[str, bool]:
    """
    Generate triangle signals (exact Pine parity)
    
    Args:
        bias: Current bar bias ("Bullish", "Bearish", "Neutral")
        bias_prev: Previous bar bias
        htf_bullish: HTF alignment bullish flag
        htf_bearish: HTF alignment bearish flag
        bullish_engulfing: Bullish engulfing detected
        bearish_engulfing: Bearish engulfing detected
        bullish_sweep_engulfing: Bullish sweep engulfing detected
        bearish_sweep_engulfing: Bearish sweep engulfing detected
        htf_aligned_only: Require HTF alignment
        require_engulfing: Require basic engulfing
        require_sweep_engulfing: Require sweep engulfing
    
    Returns:
        dict with keys: fvg_bull_signal, fvg_bear_signal, show_bull_triangle, show_bear_triangle
    """
    # Step 1: FVG signal candidates (bias flip + HTF gating)
    fvg_bull_signal = (
        bias != bias_prev and
        bias == "Bullish" and
        (not htf_aligned_only or htf_bullish)
    )
    
    fvg_bear_signal = (
        bias != bias_prev and
        bias == "Bearish" and
        (not htf_aligned_only or htf_bearish)
    )
    
    # Step 2: Apply engulfing filters (priority: sweep > basic > none)
    if require_sweep_engulfing:
        show_bull_triangle = fvg_bull_signal and bullish_sweep_engulfing
        show_bear_triangle = fvg_bear_signal and bearish_sweep_engulfing
    elif require_engulfing:
        show_bull_triangle = fvg_bull_signal and bullish_engulfing
        show_bear_triangle = fvg_bear_signal and bearish_engulfing
    else:
        show_bull_triangle = fvg_bull_signal
        show_bear_triangle = fvg_bear_signal
    
    return {
        'fvg_bull_signal': fvg_bull_signal,
        'fvg_bear_signal': fvg_bear_signal,
        'show_bull_triangle': show_bull_triangle,
        'show_bear_triangle': show_bear_triangle
    }

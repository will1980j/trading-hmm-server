"""
Unit tests for Signal Generation (Phase B Module 5)
Pure function tests - no state, no timing
"""

import sys
sys.path.append('.')
from market_parity.signal_generation import generate_signals

def test_bias_flip_bullish_no_filters():
    """Bias flip to Bullish with no filters → signal"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == True
    assert result['show_bull_triangle'] == True
    print("OK Bias flip bullish no filters")

def test_bias_flip_bearish_no_filters():
    """Bias flip to Bearish with no filters → signal"""
    result = generate_signals(
        bias="Bearish", bias_prev="Neutral",
        htf_bullish=False, htf_bearish=True,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=False
    )
    assert result['fvg_bear_signal'] == True
    assert result['show_bear_triangle'] == True
    print("OK Bias flip bearish no filters")

def test_no_signal_if_bias_unchanged():
    """No bias change → no signal"""
    result = generate_signals(
        bias="Bullish", bias_prev="Bullish",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == False
    assert result['show_bull_triangle'] == False
    print("OK No signal if bias unchanged")

def test_htf_alignment_pass():
    """HTF alignment required and met → signal"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=True, require_engulfing=False, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == True
    assert result['show_bull_triangle'] == True
    print("OK HTF alignment pass")

def test_htf_alignment_veto():
    """HTF alignment required but not met → no signal"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=False, htf_bearish=False,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=True, require_engulfing=False, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == False
    assert result['show_bull_triangle'] == False
    print("OK HTF alignment veto")

def test_engulfing_required_pass():
    """Engulfing required and present → signal"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=True, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=True, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == True
    assert result['show_bull_triangle'] == True
    print("OK Engulfing required pass")

def test_engulfing_required_veto():
    """Engulfing required but not present → no triangle"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=True, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == True  # FVG signal still true
    assert result['show_bull_triangle'] == False  # But triangle vetoed
    print("OK Engulfing required veto")

def test_sweep_engulfing_required_pass():
    """Sweep engulfing required and present → signal"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=True, bearish_engulfing=False,
        bullish_sweep_engulfing=True, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=True
    )
    assert result['fvg_bull_signal'] == True
    assert result['show_bull_triangle'] == True
    print("OK Sweep engulfing required pass")

def test_sweep_engulfing_required_veto():
    """Sweep engulfing required but not present → no triangle"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=True, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=True
    )
    assert result['fvg_bull_signal'] == True
    assert result['show_bull_triangle'] == False  # Sweep required but not present
    print("OK Sweep engulfing required veto")

def test_conflicting_filters():
    """Multiple filters must all pass"""
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=False, htf_bearish=False,
        bullish_engulfing=True, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=True, require_engulfing=True, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == False  # HTF not aligned
    assert result['show_bull_triangle'] == False
    print("OK Conflicting filters")

def test_bullish_and_bearish_independent():
    """Bullish and bearish signals are independent"""
    result = generate_signals(
        bias="Bullish", bias_prev="Bearish",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == True
    assert result['fvg_bear_signal'] == False
    assert result['show_bull_triangle'] == True
    assert result['show_bear_triangle'] == False
    print("OK Bullish and bearish independent")

def test_neutral_bias_no_signal():
    """Neutral bias → no signal"""
    result = generate_signals(
        bias="Neutral", bias_prev="Bullish",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=False, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=False
    )
    assert result['fvg_bull_signal'] == False
    assert result['fvg_bear_signal'] == False
    print("OK Neutral bias no signal")

def test_sweep_priority_over_basic():
    """Sweep engulfing takes priority over basic engulfing"""
    # When sweep required, basic engulfing alone is not enough
    result = generate_signals(
        bias="Bullish", bias_prev="Neutral",
        htf_bullish=True, htf_bearish=False,
        bullish_engulfing=True, bearish_engulfing=False,
        bullish_sweep_engulfing=False, bearish_sweep_engulfing=False,
        htf_aligned_only=False, require_engulfing=False, require_sweep_engulfing=True
    )
    assert result['show_bull_triangle'] == False  # Sweep required but not present
    print("OK Sweep priority over basic")

if __name__ == '__main__':
    test_bias_flip_bullish_no_filters()
    test_bias_flip_bearish_no_filters()
    test_no_signal_if_bias_unchanged()
    test_htf_alignment_pass()
    test_htf_alignment_veto()
    test_engulfing_required_pass()
    test_engulfing_required_veto()
    test_sweep_engulfing_required_pass()
    test_sweep_engulfing_required_veto()
    test_conflicting_filters()
    test_bullish_and_bearish_independent()
    test_neutral_bias_no_signal()
    test_sweep_priority_over_basic()
    print("\n[PASS] All Module 5 tests passed")

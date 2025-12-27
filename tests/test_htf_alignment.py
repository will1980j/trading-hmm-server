"""
Unit tests for HTF Alignment (Phase B Module 4)
Pure boolean logic tests - no state, no timing
"""

import sys
sys.path.append('.')
from market_parity.htf_alignment import compute_htf_alignment

def test_single_tf_enabled_bullish():
    """Single TF enabled and bullish → htf_bullish True"""
    biases = {'daily': 'Bullish', 'h4': 'Neutral', 'h1': 'Neutral', 'm15': 'Neutral', 'm5': 'Neutral'}
    use_flags = {'daily': True, 'h4': False, 'h1': False, 'm15': False, 'm5': False}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == True
    assert htf_bear == False
    print("OK Single TF enabled bullish")

def test_single_tf_enabled_bearish():
    """Single TF enabled and bearish → htf_bearish True"""
    biases = {'daily': 'Bearish', 'h4': 'Neutral', 'h1': 'Neutral', 'm15': 'Neutral', 'm5': 'Neutral'}
    use_flags = {'daily': True, 'h4': False, 'h1': False, 'm15': False, 'm5': False}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == False
    assert htf_bear == True
    print("OK Single TF enabled bearish")

def test_single_tf_enabled_neutral():
    """Single TF enabled but neutral → both False"""
    biases = {'daily': 'Neutral', 'h4': 'Neutral', 'h1': 'Neutral', 'm15': 'Neutral', 'm5': 'Neutral'}
    use_flags = {'daily': True, 'h4': False, 'h1': False, 'm15': False, 'm5': False}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == False
    assert htf_bear == False
    print("OK Single TF enabled neutral")

def test_all_enabled_all_bullish():
    """All TFs enabled and all bullish → htf_bullish True"""
    biases = {'daily': 'Bullish', 'h4': 'Bullish', 'h1': 'Bullish', 'm15': 'Bullish', 'm5': 'Bullish'}
    use_flags = {'daily': True, 'h4': True, 'h1': True, 'm15': True, 'm5': True}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == True
    assert htf_bear == False
    print("OK All enabled all bullish")

def test_all_enabled_all_bearish():
    """All TFs enabled and all bearish → htf_bearish True"""
    biases = {'daily': 'Bearish', 'h4': 'Bearish', 'h1': 'Bearish', 'm15': 'Bearish', 'm5': 'Bearish'}
    use_flags = {'daily': True, 'h4': True, 'h1': True, 'm15': True, 'm5': True}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == False
    assert htf_bear == True
    print("OK All enabled all bearish")

def test_mixed_biases_one_mismatch():
    """Multiple TFs enabled, one mismatch → both False"""
    biases = {'daily': 'Bullish', 'h4': 'Bullish', 'h1': 'Bearish', 'm15': 'Bullish', 'm5': 'Bullish'}
    use_flags = {'daily': True, 'h4': True, 'h1': True, 'm15': True, 'm5': True}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == False  # h1 is Bearish
    assert htf_bear == False  # Not all Bearish
    print("OK Mixed biases one mismatch")

def test_neutral_in_enabled_tf():
    """Neutral in any enabled TF → both False"""
    biases = {'daily': 'Bullish', 'h4': 'Bullish', 'h1': 'Neutral', 'm15': 'Bullish', 'm5': 'Bullish'}
    use_flags = {'daily': True, 'h4': True, 'h1': True, 'm15': True, 'm5': True}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == False  # h1 is Neutral
    assert htf_bear == False
    print("OK Neutral in enabled TF")

def test_disabled_tfs_ignored():
    """Disabled TFs do not affect alignment"""
    biases = {'daily': 'Bearish', 'h4': 'Bullish', 'h1': 'Bullish', 'm15': 'Neutral', 'm5': 'Bullish'}
    use_flags = {'daily': False, 'h4': True, 'h1': True, 'm15': False, 'm5': True}
    
    # Only h4, h1, m5 are enabled - all Bullish
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == True   # h4, h1, m5 all Bullish
    assert htf_bear == False
    print("OK Disabled TFs ignored")

def test_no_tfs_enabled():
    """No TFs enabled → both True (Pine behavior)"""
    biases = {'daily': 'Neutral', 'h4': 'Neutral', 'h1': 'Neutral', 'm15': 'Neutral', 'm5': 'Neutral'}
    use_flags = {'daily': False, 'h4': False, 'h1': False, 'm15': False, 'm5': False}
    
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == True
    assert htf_bear == True
    print("OK No TFs enabled")

def test_partial_enabled_all_agree():
    """Subset of TFs enabled, all agree → alignment True"""
    biases = {'daily': 'Neutral', 'h4': 'Bearish', 'h1': 'Bearish', 'm15': 'Neutral', 'm5': 'Neutral'}
    use_flags = {'daily': False, 'h4': True, 'h1': True, 'm15': False, 'm5': False}
    
    # Only h4 and h1 enabled - both Bearish
    htf_bull, htf_bear = compute_htf_alignment(biases, use_flags)
    assert htf_bull == False
    assert htf_bear == True  # h4 and h1 both Bearish
    print("OK Partial enabled all agree")

if __name__ == '__main__':
    test_single_tf_enabled_bullish()
    test_single_tf_enabled_bearish()
    test_single_tf_enabled_neutral()
    test_all_enabled_all_bullish()
    test_all_enabled_all_bearish()
    test_mixed_biases_one_mismatch()
    test_neutral_in_enabled_tf()
    test_disabled_tfs_ignored()
    test_no_tfs_enabled()
    test_partial_enabled_all_agree()
    print("\n[PASS] All Module 4 tests passed")

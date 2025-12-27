"""
Phase B Module 4: HTF Alignment Check
Pure boolean reducer over HTF bias values - no state, no timing, no market logic

Canonical Pine behavior:
- Disabled timeframes are ignored (do not veto)
- Enabled timeframes must ALL agree for alignment
- Neutral breaks alignment (Neutral != Bullish and Neutral != Bearish)
- If no TFs enabled: both htf_bullish and htf_bearish are True
"""

from typing import Dict, Tuple

def compute_htf_alignment(
    biases: Dict[str, str],
    use_flags: Dict[str, bool]
) -> Tuple[bool, bool]:
    """
    Compute HTF alignment flags
    
    Args:
        biases: dict with keys 'daily', 'h4', 'h1', 'm15', 'm5'
                values must be "Bullish", "Bearish", or "Neutral"
        use_flags: dict with keys 'daily', 'h4', 'h1', 'm15', 'm5'
                   values are bool (True = enabled, False = disabled)
    
    Returns:
        tuple: (htf_bullish, htf_bearish)
        
    Logic:
        htf_bullish = ALL enabled TFs have bias == "Bullish"
        htf_bearish = ALL enabled TFs have bias == "Bearish"
        
    Special case:
        If no TFs are enabled, both return True (Pine behavior)
    """
    # Map timeframe keys
    tf_keys = ['daily', 'h4', 'h1', 'm15', 'm5']
    
    # Collect enabled timeframes
    enabled_tfs = [tf for tf in tf_keys if use_flags.get(tf, False)]
    
    # Special case: no TFs enabled
    if not enabled_tfs:
        return (True, True)
    
    # Check bullish alignment
    htf_bullish = all(biases.get(tf) == "Bullish" for tf in enabled_tfs)
    
    # Check bearish alignment
    htf_bearish = all(biases.get(tf) == "Bearish" for tf in enabled_tfs)
    
    return (htf_bullish, htf_bearish)

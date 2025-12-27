"""Unit tests for get_bias FVG/IFVG (Phase B Module 2)"""

import sys
sys.path.append('.')
from market_parity.get_bias_fvg_ifvg import BiasEngineFvgIfvg

def test_ath_breakout_sets_bullish():
    engine = BiasEngineFvgIfvg()
    engine.update({'ts': 1, 'open': 100, 'high': 105, 'low': 99, 'close': 104})
    engine.update({'ts': 2, 'open': 104, 'high': 106, 'low': 103, 'close': 106})
    assert engine.bias == "Bullish"
    print("✅ ATH breakout sets bullish")

def test_atl_breakdown_sets_bearish():
    engine = BiasEngineFvgIfvg()
    engine.update({'ts': 1, 'open': 100, 'high': 101, 'low': 95, 'close': 96})
    engine.update({'ts': 2, 'open': 96, 'high': 97, 'low': 94, 'close': 94})
    assert engine.bias == "Bearish"
    print("✅ ATL breakdown sets bearish")

def test_bullish_fvg_detection():
    engine = BiasEngineFvgIfvg()
    engine.update({'ts': 1, 'open': 100, 'high': 102, 'low': 98, 'close': 101})
    engine.update({'ts': 2, 'open': 101, 'high': 103, 'low': 100, 'close': 102})
    engine.update({'ts': 3, 'open': 105, 'high': 107, 'low': 104, 'close': 106})
    assert len(engine.bull_fvg_highs) == 1
    assert engine.bull_fvg_highs[0] == 104
    assert engine.bull_fvg_lows[0] == 102
    print("✅ Bullish FVG detection")

def test_bearish_fvg_detection():
    engine = BiasEngineFvgIfvg()
    engine.update({'ts': 1, 'open': 100, 'high': 102, 'low': 98, 'close': 99})
    engine.update({'ts': 2, 'open': 99, 'high': 101, 'low': 97, 'close': 98})
    engine.update({'ts': 3, 'open': 95, 'high': 96, 'low': 93, 'close': 94})
    assert len(engine.bear_fvg_highs) == 1
    assert engine.bear_fvg_highs[0] == 98
    assert engine.bear_fvg_lows[0] == 96
    print("✅ Bearish FVG detection")

def test_bull_fvg_to_bear_ifvg():
    """Bull FVG becomes Bear IFVG when close < bull_fvg_lows"""
    engine = BiasEngineFvgIfvg()
    engine.update({'ts': 1, 'open': 100, 'high': 102, 'low': 98, 'close': 101})
    engine.update({'ts': 2, 'open': 101, 'high': 103, 'low': 100, 'close': 102})
    engine.update({'ts': 3, 'open': 105, 'high': 107, 'low': 104, 'close': 106})
    assert len(engine.bull_fvg_highs) == 1
    # Close below bull_fvg_lows[0] (102) → becomes bear IFVG
    engine.update({'ts': 4, 'open': 104, 'high': 105, 'low': 101, 'close': 101})
    assert engine.bias == "Bearish"
    assert len(engine.bull_fvg_highs) == 0
    assert len(engine.bear_ifvg_highs) == 1
    print("✅ Bull FVG → Bear IFVG")

def test_bear_ifvg_cleanup():
    """Bear IFVG removed when close > bear_ifvg_highs"""
    engine = BiasEngineFvgIfvg()
    # Create bull FVG then convert to bear IFVG
    engine.update({'ts': 1, 'open': 100, 'high': 102, 'low': 98, 'close': 101})
    engine.update({'ts': 2, 'open': 101, 'high': 103, 'low': 100, 'close': 102})
    engine.update({'ts': 3, 'open': 105, 'high': 107, 'low': 104, 'close': 106})
    engine.update({'ts': 4, 'open': 104, 'high': 105, 'low': 101, 'close': 101})
    assert len(engine.bear_ifvg_highs) == 1
    # Close above bear_ifvg_highs[0] (104) → cleanup
    engine.update({'ts': 5, 'open': 101, 'high': 105, 'low': 100, 'close': 105})
    assert len(engine.bear_ifvg_highs) == 0
    assert engine.bias == "Bullish"
    print("✅ Bear IFVG cleanup")

if __name__ == '__main__':
    test_ath_breakout_sets_bullish()
    test_atl_breakdown_sets_bearish()
    test_bullish_fvg_detection()
    test_bearish_fvg_detection()
    test_bull_fvg_to_bear_ifvg()
    test_bear_ifvg_cleanup()
    print("\n✅ All Module 2 tests passed")

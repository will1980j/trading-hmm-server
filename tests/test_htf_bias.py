"""
Unit tests for HTF Bias (Phase B Module 3)
Tests request.security() parity behavior
"""

import sys
sys.path.append('.')
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from market_parity.htf_bias import HTFBiasEngine

def test_htf_bias_does_not_change_mid_bar():
    """HTF bias remains constant between HTF bar closes"""
    engine = HTFBiasEngine()
    
    # Create 5 consecutive 1m bars (5M bar closes on 5th bar)
    base_ts = datetime(2024, 1, 2, 0, 0, tzinfo=ZoneInfo('UTC'))
    
    for i in range(5):
        ts = base_ts + timedelta(minutes=i)
        bar = {'ts': ts, 'open': 100 + i, 'high': 101 + i, 'low': 99 + i, 'close': 100.5 + i}
        result = engine.update_ltf_bar(bar)
        
        if i < 4:
            # Before 5M close: bias should be Neutral (initial)
            assert result['m5_bias'] == "Neutral", f"Bar {i}: m5_bias changed mid-bar"
        else:
            # On 5M close (minute=4): bias may update
            pass  # Bias can change here
    
    print("OK HTF bias does not change mid-bar")

def test_htf_bias_updates_on_bar_close():
    """HTF bias updates only when HTF bar closes"""
    engine = HTFBiasEngine()
    
    base_ts = datetime(2024, 1, 2, 0, 0, tzinfo=ZoneInfo('UTC'))
    
    # First 5M bar (closes at minute 4)
    for i in range(5):
        ts = base_ts + timedelta(minutes=i)
        bar = {'ts': ts, 'open': 100, 'high': 105, 'low': 99, 'close': 104}
        result = engine.update_ltf_bar(bar)
    
    first_bias = result['m5_bias']
    
    # Second 5M bar (closes at minute 9)
    for i in range(5, 10):
        ts = base_ts + timedelta(minutes=i)
        bar = {'ts': ts, 'open': 104, 'high': 106, 'low': 103, 'close': 106}
        result = engine.update_ltf_bar(bar)
        
        if i < 9:
            # Mid-bar: should still have first_bias
            assert result['m5_bias'] == first_bias
        else:
            # Bar close: bias may have updated
            pass
    
    print("OK HTF bias updates on bar close")

def test_different_timeframes_update_independently():
    """5M, 15M, 1H update at different times"""
    engine = HTFBiasEngine()
    
    base_ts = datetime(2024, 1, 2, 0, 0, tzinfo=ZoneInfo('UTC'))
    
    m5_updates = []
    m15_updates = []
    h1_updates = []
    
    # Run for 60 minutes
    for i in range(60):
        ts = base_ts + timedelta(minutes=i)
        bar = {'ts': ts, 'open': 100 + i*0.1, 'high': 101 + i*0.1, 'low': 99 + i*0.1, 'close': 100.5 + i*0.1}
        result = engine.update_ltf_bar(bar)
        
        # Track when each TF could have updated
        if engine._is_htf_bar_close(ts, '5M'):
            m5_updates.append(i)
        if engine._is_htf_bar_close(ts, '15M'):
            m15_updates.append(i)
        if engine._is_htf_bar_close(ts, '1H'):
            h1_updates.append(i)
    
    # Verify update frequencies
    assert len(m5_updates) == 12  # 60 / 5 = 12
    assert len(m15_updates) == 4  # 60 / 15 = 4
    assert len(h1_updates) == 1   # 60 / 60 = 1
    
    # Verify update times
    assert m5_updates == [4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59]
    assert m15_updates == [14, 29, 44, 59]
    assert h1_updates == [59]
    
    print("OK Different timeframes update independently")

def test_forward_fill_behavior():
    """HTF bias forward-fills across 1m bars"""
    engine = HTFBiasEngine()
    
    base_ts = datetime(2024, 1, 2, 0, 0, tzinfo=ZoneInfo('UTC'))
    
    # First 5M bar
    for i in range(5):
        ts = base_ts + timedelta(minutes=i)
        bar = {'ts': ts, 'open': 100, 'high': 105, 'low': 99, 'close': 104}
        result = engine.update_ltf_bar(bar)
    
    bias_after_first_5m = result['m5_bias']
    
    # Next 4 bars (not yet closing 2nd 5M bar)
    for i in range(5, 9):
        ts = base_ts + timedelta(minutes=i)
        bar = {'ts': ts, 'open': 104, 'high': 106, 'low': 103, 'close': 106}
        result = engine.update_ltf_bar(bar)
        
        # Should still have same bias (forward-fill)
        assert result['m5_bias'] == bias_after_first_5m, f"Forward-fill failed at minute {i}"
    
    print("OK Forward-fill behavior")

def test_deterministic_replay():
    """Replaying same data twice produces identical results"""
    base_ts = datetime(2024, 1, 2, 0, 0, tzinfo=ZoneInfo('UTC'))
    
    bars = []
    for i in range(60):
        ts = base_ts + timedelta(minutes=i)
        bars.append({'ts': ts, 'open': 100 + i*0.1, 'high': 101 + i*0.1, 'low': 99 + i*0.1, 'close': 100.5 + i*0.1})
    
    # First run
    engine1 = HTFBiasEngine()
    results1 = []
    for bar in bars:
        result = engine1.update_ltf_bar(bar)
        results1.append(result.copy())
    
    # Second run
    engine2 = HTFBiasEngine()
    results2 = []
    for bar in bars:
        result = engine2.update_ltf_bar(bar)
        results2.append(result.copy())
    
    # Compare
    for i, (r1, r2) in enumerate(zip(results1, results2)):
        assert r1 == r2, f"Mismatch at bar {i}: {r1} != {r2}"
    
    print("OK Deterministic replay")

def test_htf_bar_close_detection():
    """Verify HTF bar close detection logic"""
    engine = HTFBiasEngine()
    
    # Test 5M closes
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 4), '5M') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 9), '5M') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 5), '5M') == False
    
    # Test 15M closes
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 14), '15M') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 29), '15M') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 15), '15M') == False
    
    # Test 1H closes
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 59), '1H') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 1, 59), '1H') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 0, 0), '1H') == False
    
    # Test 4H closes
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 3, 59), '4H') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 7, 59), '4H') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 4, 59), '4H') == False
    
    # Test 1D closes
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 23, 59), '1D') == True
    assert engine._is_htf_bar_close(datetime(2024, 1, 2, 23, 58), '1D') == False
    
    print("OK HTF bar close detection")

def test_htf_ohlc_aggregation():
    """Verify correct OHLC aggregation for HTF bars"""
    engine = HTFBiasEngine()
    
    base_ts = datetime(2024, 1, 2, 0, 0, tzinfo=ZoneInfo('UTC'))
    
    # Create 5 bars for one 5M period
    bars = [
        {'ts': base_ts, 'open': 100, 'high': 102, 'low': 99, 'close': 101},
        {'ts': base_ts + timedelta(minutes=1), 'open': 101, 'high': 103, 'low': 100, 'close': 102},
        {'ts': base_ts + timedelta(minutes=2), 'open': 102, 'high': 104, 'low': 101, 'close': 103},
        {'ts': base_ts + timedelta(minutes=3), 'open': 103, 'high': 105, 'low': 102, 'close': 104},
        {'ts': base_ts + timedelta(minutes=4), 'open': 104, 'high': 106, 'low': 103, 'close': 105}
    ]
    
    for bar in bars[:-1]:
        engine.update_ltf_bar(bar)
    
    # Check aggregated bar before close
    htf_bar = engine.current_htf_bars['5M']
    assert htf_bar['open'] == 100  # First bar's open
    assert htf_bar['high'] == 105  # Max of all highs
    assert htf_bar['low'] == 99    # Min of all lows
    assert htf_bar['close'] == 104 # Last bar's close (so far)
    
    # Process final bar
    engine.update_ltf_bar(bars[-1])
    
    # After close, HTF bar should be reset
    assert engine.current_htf_bars['5M'] is None
    
    print("OK HTF OHLC aggregation")

if __name__ == '__main__':
    test_htf_bar_close_detection()
    test_htf_ohlc_aggregation()
    test_htf_bias_does_not_change_mid_bar()
    test_htf_bias_updates_on_bar_close()
    test_different_timeframes_update_independently()
    test_forward_fill_behavior()
    test_deterministic_replay()
    print("\n[PASS] All Module 3 tests passed")

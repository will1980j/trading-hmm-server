#!/usr/bin/env python3
"""Test that mfe_R field is properly parsed"""

# Simulate the fixed parsing logic
def test_mfe_parsing():
    # Test case 1: Indicator format (mfe_R)
    data1 = {
        "event_type": "MFE_UPDATE",
        "trade_id": "TEST_001",
        "mfe_R": 0.75,
        "current_price": 21500.00
    }
    
    be_mfe = float(data1.get('be_mfe') or data1.get('mfe_R') or data1.get('mfe') or 0)
    no_be_mfe = float(data1.get('no_be_mfe') or data1.get('mfe_R') or data1.get('mfe') or 0)
    
    print("Test 1: Indicator format (mfe_R)")
    print(f"  Input: mfe_R={data1.get('mfe_R')}")
    print(f"  Output: be_mfe={be_mfe}, no_be_mfe={no_be_mfe}")
    assert be_mfe == 0.75, f"Expected 0.75, got {be_mfe}"
    assert no_be_mfe == 0.75, f"Expected 0.75, got {no_be_mfe}"
    print("  ✅ PASS")
    
    # Test case 2: Strategy format (be_mfe, no_be_mfe)
    data2 = {
        "event_type": "MFE_UPDATE",
        "trade_id": "TEST_002",
        "be_mfe": 1.0,
        "no_be_mfe": 1.5,
        "current_price": 21500.00
    }
    
    be_mfe = float(data2.get('be_mfe') or data2.get('mfe_R') or data2.get('mfe') or 0)
    no_be_mfe = float(data2.get('no_be_mfe') or data2.get('mfe_R') or data2.get('mfe') or 0)
    
    print("\nTest 2: Strategy format (be_mfe, no_be_mfe)")
    print(f"  Input: be_mfe={data2.get('be_mfe')}, no_be_mfe={data2.get('no_be_mfe')}")
    print(f"  Output: be_mfe={be_mfe}, no_be_mfe={no_be_mfe}")
    assert be_mfe == 1.0, f"Expected 1.0, got {be_mfe}"
    assert no_be_mfe == 1.5, f"Expected 1.5, got {no_be_mfe}"
    print("  ✅ PASS")
    
    # Test case 3: Legacy format (mfe)
    data3 = {
        "event_type": "MFE_UPDATE",
        "trade_id": "TEST_003",
        "mfe": 0.5,
        "current_price": 21500.00
    }
    
    be_mfe = float(data3.get('be_mfe') or data3.get('mfe_R') or data3.get('mfe') or 0)
    no_be_mfe = float(data3.get('no_be_mfe') or data3.get('mfe_R') or data3.get('mfe') or 0)
    
    print("\nTest 3: Legacy format (mfe)")
    print(f"  Input: mfe={data3.get('mfe')}")
    print(f"  Output: be_mfe={be_mfe}, no_be_mfe={no_be_mfe}")
    assert be_mfe == 0.5, f"Expected 0.5, got {be_mfe}"
    assert no_be_mfe == 0.5, f"Expected 0.5, got {no_be_mfe}"
    print("  ✅ PASS")
    
    # Test case 4: Empty/missing fields
    data4 = {
        "event_type": "MFE_UPDATE",
        "trade_id": "TEST_004",
        "current_price": 21500.00
    }
    
    be_mfe = float(data4.get('be_mfe') or data4.get('mfe_R') or data4.get('mfe') or 0)
    no_be_mfe = float(data4.get('no_be_mfe') or data4.get('mfe_R') or data4.get('mfe') or 0)
    
    print("\nTest 4: Missing MFE fields")
    print(f"  Input: (no MFE fields)")
    print(f"  Output: be_mfe={be_mfe}, no_be_mfe={no_be_mfe}")
    assert be_mfe == 0, f"Expected 0, got {be_mfe}"
    assert no_be_mfe == 0, f"Expected 0, got {no_be_mfe}"
    print("  ✅ PASS")
    
    print("\n" + "="*50)
    print("All tests passed! ✅")
    print("="*50)

if __name__ == '__main__':
    test_mfe_parsing()

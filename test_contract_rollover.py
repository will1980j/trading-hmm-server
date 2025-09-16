#!/usr/bin/env python3
"""
Test script for contract rollover functionality
"""

def test_contract_rollover():
    """Test the contract rollover detection and handling"""
    
    # Simulate different contract scenarios
    test_cases = [
        {
            'name': 'NQ Generic to Specific',
            'current': 'NQ1!',
            'incoming': 'NQZ24',
            'should_rollover': True
        },
        {
            'name': 'NQ Same Contract',
            'current': 'NQ1!',
            'incoming': 'NQ1!',
            'should_rollover': False
        },
        {
            'name': 'NQ Newer Contract',
            'current': 'NQU24',
            'incoming': 'NQZ24',
            'should_rollover': True
        },
        {
            'name': 'ES Contract Change',
            'current': 'ES1!',
            'incoming': 'ESZ24',
            'should_rollover': True
        }
    ]
    
    print("🧪 CONTRACT ROLLOVER TESTS")
    print("=" * 40)
    
    # Mock contract manager for testing
    class MockContractManager:
        def __init__(self):
            self.active_contracts = {
                'NQ': 'NQ1!',
                'ES': 'ES1!',
                'YM': 'YM1!',
                'RTY': 'RTY1!'
            }
        
        def detect_contract_rollover(self, symbol):
            # Simple test logic
            base = symbol[:2] if len(symbol) >= 2 else None
            if not base or base not in self.active_contracts:
                return None
            
            current = self.active_contracts[base]
            if symbol != current:
                return {
                    'base_symbol': base,
                    'old_contract': current,
                    'new_contract': symbol,
                    'rollover_detected': True
                }
            return None
    
    manager = MockContractManager()
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        print(f"   Current: {test['current']}")
        print(f"   Incoming: {test['incoming']}")
        
        # Set current contract
        base = test['current'][:2]
        manager.active_contracts[base] = test['current']
        
        # Test detection
        result = manager.detect_contract_rollover(test['incoming'])
        
        if test['should_rollover']:
            if result:
                print(f"   ✅ PASS: Rollover detected correctly")
                print(f"      {result['old_contract']} → {result['new_contract']}")
            else:
                print(f"   ❌ FAIL: Should have detected rollover")
        else:
            if not result:
                print(f"   ✅ PASS: No rollover detected (correct)")
            else:
                print(f"   ❌ FAIL: Should not have detected rollover")
    
    print(f"\n🎯 INTEGRATION TEST")
    print("=" * 40)
    
    # Test signal processing
    test_signals = [
        {'symbol': 'NQ1!', 'bias': 'Bullish', 'price': 15000},
        {'symbol': 'NQZ24', 'bias': 'Bearish', 'price': 15100},
        {'symbol': 'ESU24', 'bias': 'Bullish', 'price': 4500}
    ]
    
    for signal in test_signals:
        print(f"\n📡 Processing signal: {signal['symbol']}")
        
        rollover = manager.detect_contract_rollover(signal['symbol'])
        if rollover:
            print(f"   🔄 Rollover: {rollover['old_contract']} → {rollover['new_contract']}")
            # Simulate updating active contract
            manager.active_contracts[rollover['base_symbol']] = rollover['new_contract']
            print(f"   ✅ Updated active contract for {rollover['base_symbol']}")
        else:
            print(f"   ✅ No rollover needed")
    
    print(f"\n📊 Final Active Contracts:")
    for base, contract in manager.active_contracts.items():
        print(f"   {base}: {contract}")

if __name__ == "__main__":
    test_contract_rollover()
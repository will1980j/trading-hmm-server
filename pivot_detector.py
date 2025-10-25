#!/usr/bin/env python3
"""
PIVOT DETECTOR - EXACT 3-candle pivot detection algorithm
Implements your precise pivot detection rules with NO approximations
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class PivotDetector:
    """
    EXACT 3-candle pivot detection
    
    PIVOT LOW: Candle low < both adjacent candle lows
    PIVOT HIGH: Candle high > both adjacent candle highs
    
    NO shortcuts, NO approximations - EXACT implementation only
    """
    
    def __init__(self):
        pass
    
    def find_pivot_low_in_range(self, candles: List[Dict], start_index: int = 0, end_index: int = None) -> Optional[Dict]:
        """
        Find 3-candle pivot low in specified range
        
        Args:
            candles: List of candle dictionaries with 'high', 'low', 'open', 'close'
            start_index: Start searching from this index
            end_index: End searching at this index (None = end of list)
        
        Returns:
            Pivot candle dictionary or None if no pivot found
        """
        
        if end_index is None:
            end_index = len(candles) - 1
        
        logger.info(f"🔍 Searching for pivot low from index {start_index} to {end_index}")
        
        # Need at least 3 candles for pivot detection
        if len(candles) < 3:
            logger.warning("⚠️ Need at least 3 candles for pivot detection")
            return None
        
        # Search through the range (excluding first and last candles as they can't be pivots)
        for i in range(max(1, start_index), min(len(candles) - 1, end_index)):
            
            current_candle = candles[i]
            left_candle = candles[i - 1]
            right_candle = candles[i + 1]
            
            # EXACT PIVOT LOW CONDITION
            if (current_candle['low'] < left_candle['low'] and 
                current_candle['low'] < right_candle['low']):
                
                logger.info(f"✅ PIVOT LOW FOUND at index {i}: {current_candle['low']}")
                logger.info(f"   Left: {left_candle['low']}, Center: {current_candle['low']}, Right: {right_candle['low']}")
                
                return {
                    'candle': current_candle,
                    'index': i,
                    'pivot_type': 'low',
                    'pivot_value': current_candle['low']
                }
        
        logger.info("❌ No pivot low found in range")
        return None
    
    def find_pivot_high_in_range(self, candles: List[Dict], start_index: int = 0, end_index: int = None) -> Optional[Dict]:
        """
        Find 3-candle pivot high in specified range
        
        Args:
            candles: List of candle dictionaries with 'high', 'low', 'open', 'close'
            start_index: Start searching from this index
            end_index: End searching at this index (None = end of list)
        
        Returns:
            Pivot candle dictionary or None if no pivot found
        """
        
        if end_index is None:
            end_index = len(candles) - 1
        
        logger.info(f"🔍 Searching for pivot high from index {start_index} to {end_index}")
        
        # Need at least 3 candles for pivot detection
        if len(candles) < 3:
            logger.warning("⚠️ Need at least 3 candles for pivot detection")
            return None
        
        # Search through the range (excluding first and last candles as they can't be pivots)
        for i in range(max(1, start_index), min(len(candles) - 1, end_index)):
            
            current_candle = candles[i]
            left_candle = candles[i - 1]
            right_candle = candles[i + 1]
            
            # EXACT PIVOT HIGH CONDITION
            if (current_candle['high'] > left_candle['high'] and 
                current_candle['high'] > right_candle['high']):
                
                logger.info(f"✅ PIVOT HIGH FOUND at index {i}: {current_candle['high']}")
                logger.info(f"   Left: {left_candle['high']}, Center: {current_candle['high']}, Right: {right_candle['high']}")
                
                return {
                    'candle': current_candle,
                    'index': i,
                    'pivot_type': 'high',
                    'pivot_value': current_candle['high']
                }
        
        logger.info("❌ No pivot high found in range")
        return None
    
    def is_candle_pivot_low(self, candles: List[Dict], candle_index: int) -> bool:
        """
        Check if specific candle is a 3-candle pivot low
        
        Args:
            candles: List of candle dictionaries
            candle_index: Index of candle to check
        
        Returns:
            True if candle is a pivot low, False otherwise
        """
        
        # Need adjacent candles
        if candle_index <= 0 or candle_index >= len(candles) - 1:
            return False
        
        current_candle = candles[candle_index]
        left_candle = candles[candle_index - 1]
        right_candle = candles[candle_index + 1]
        
        # EXACT PIVOT LOW CONDITION
        is_pivot = (current_candle['low'] < left_candle['low'] and 
                   current_candle['low'] < right_candle['low'])
        
        if is_pivot:
            logger.info(f"✅ Candle at index {candle_index} IS a pivot low: {current_candle['low']}")
        else:
            logger.debug(f"❌ Candle at index {candle_index} is NOT a pivot low")
        
        return is_pivot
    
    def is_candle_pivot_high(self, candles: List[Dict], candle_index: int) -> bool:
        """
        Check if specific candle is a 3-candle pivot high
        
        Args:
            candles: List of candle dictionaries
            candle_index: Index of candle to check
        
        Returns:
            True if candle is a pivot high, False otherwise
        """
        
        # Need adjacent candles
        if candle_index <= 0 or candle_index >= len(candles) - 1:
            return False
        
        current_candle = candles[candle_index]
        left_candle = candles[candle_index - 1]
        right_candle = candles[candle_index + 1]
        
        # EXACT PIVOT HIGH CONDITION
        is_pivot = (current_candle['high'] > left_candle['high'] and 
                   current_candle['high'] > right_candle['high'])
        
        if is_pivot:
            logger.info(f"✅ Candle at index {candle_index} IS a pivot high: {current_candle['high']}")
        else:
            logger.debug(f"❌ Candle at index {candle_index} is NOT a pivot high")
        
        return is_pivot
    
    def find_lowest_point_in_range(self, candles: List[Dict], start_index: int = 0, end_index: int = None) -> Dict:
        """
        Find the candle with the lowest low in specified range
        
        Args:
            candles: List of candle dictionaries
            start_index: Start searching from this index
            end_index: End searching at this index (None = end of list)
        
        Returns:
            Dictionary with candle info and whether it's a pivot
        """
        
        if end_index is None:
            end_index = len(candles) - 1
        
        if start_index >= len(candles) or end_index < start_index:
            logger.error("❌ Invalid range for lowest point search")
            return None
        
        lowest_candle = None
        lowest_index = None
        lowest_value = float('inf')
        
        # Find the candle with lowest low
        for i in range(start_index, min(len(candles), end_index + 1)):
            candle = candles[i]
            if candle['low'] < lowest_value:
                lowest_value = candle['low']
                lowest_candle = candle
                lowest_index = i
        
        if lowest_candle is None:
            logger.error("❌ No candles found in range")
            return None
        
        # Check if lowest point is a pivot
        is_pivot = self.is_candle_pivot_low(candles, lowest_index)
        
        logger.info(f"📍 Lowest point in range: {lowest_value} at index {lowest_index} (Pivot: {is_pivot})")
        
        return {
            'candle': lowest_candle,
            'index': lowest_index,
            'value': lowest_value,
            'is_pivot': is_pivot,
            'type': 'low'
        }
    
    def find_highest_point_in_range(self, candles: List[Dict], start_index: int = 0, end_index: int = None) -> Dict:
        """
        Find the candle with the highest high in specified range
        
        Args:
            candles: List of candle dictionaries
            start_index: Start searching from this index
            end_index: End searching at this index (None = end of list)
        
        Returns:
            Dictionary with candle info and whether it's a pivot
        """
        
        if end_index is None:
            end_index = len(candles) - 1
        
        if start_index >= len(candles) or end_index < start_index:
            logger.error("❌ Invalid range for highest point search")
            return None
        
        highest_candle = None
        highest_index = None
        highest_value = float('-inf')
        
        # Find the candle with highest high
        for i in range(start_index, min(len(candles), end_index + 1)):
            candle = candles[i]
            if candle['high'] > highest_value:
                highest_value = candle['high']
                highest_candle = candle
                highest_index = i
        
        if highest_candle is None:
            logger.error("❌ No candles found in range")
            return None
        
        # Check if highest point is a pivot
        is_pivot = self.is_candle_pivot_high(candles, highest_index)
        
        logger.info(f"📍 Highest point in range: {highest_value} at index {highest_index} (Pivot: {is_pivot})")
        
        return {
            'candle': highest_candle,
            'index': highest_index,
            'value': highest_value,
            'is_pivot': is_pivot,
            'type': 'high'
        }
    
    def search_left_for_pivot(self, candles: List[Dict], start_index: int, search_distance: int = 5, pivot_type: str = 'low') -> Optional[Dict]:
        """
        Search left from start_index for pivot (used in stop loss methodology)
        
        Args:
            candles: List of candle dictionaries
            start_index: Index to start searching left from
            search_distance: How many candles to search left (default 5)
            pivot_type: 'low' or 'high'
        
        Returns:
            Pivot candle dictionary or None if no pivot found
        """
        
        # Calculate search range (left from start_index)
        end_search_index = max(0, start_index - search_distance)
        
        logger.info(f"🔍 Searching left for {pivot_type} pivot from index {start_index} to {end_search_index}")
        
        if pivot_type == 'low':
            return self.find_pivot_low_in_range(candles, end_search_index, start_index - 1)
        else:  # 'high'
            return self.find_pivot_high_in_range(candles, end_search_index, start_index - 1)

# Test the pivot detector
def test_pivot_detector():
    """Test the pivot detection algorithm"""
    
    print("🧪 TESTING PIVOT DETECTOR")
    print("=" * 50)
    
    detector = PivotDetector()
    
    # Test data - realistic NASDAQ candles
    test_candles = [
        {'open': 20000, 'high': 20010, 'low': 19990, 'close': 20005},  # Index 0
        {'open': 20005, 'high': 20015, 'low': 19985, 'close': 19990},  # Index 1 - Potential pivot low
        {'open': 19990, 'high': 20020, 'low': 19995, 'close': 20010},  # Index 2
        {'open': 20010, 'high': 20025, 'low': 20000, 'close': 20020},  # Index 3 - Potential pivot high
        {'open': 20020, 'high': 20015, 'low': 19995, 'close': 20000},  # Index 4
    ]
    
    print("📊 Test candles:")
    for i, candle in enumerate(test_candles):
        print(f"   {i}: H={candle['high']} L={candle['low']} O={candle['open']} C={candle['close']}")
    
    # Test pivot low detection
    print("\n🔍 Testing pivot low detection:")
    pivot_low = detector.find_pivot_low_in_range(test_candles)
    if pivot_low:
        print(f"✅ Found pivot low: {pivot_low}")
    else:
        print("❌ No pivot low found")
    
    # Test pivot high detection
    print("\n🔍 Testing pivot high detection:")
    pivot_high = detector.find_pivot_high_in_range(test_candles)
    if pivot_high:
        print(f"✅ Found pivot high: {pivot_high}")
    else:
        print("❌ No pivot high found")
    
    # Test specific candle pivot check
    print("\n🔍 Testing specific candle pivot checks:")
    for i in range(len(test_candles)):
        is_low_pivot = detector.is_candle_pivot_low(test_candles, i)
        is_high_pivot = detector.is_candle_pivot_high(test_candles, i)
        print(f"   Candle {i}: Low Pivot={is_low_pivot}, High Pivot={is_high_pivot}")
    
    # Test range analysis
    print("\n🔍 Testing range analysis:")
    lowest = detector.find_lowest_point_in_range(test_candles, 0, 3)
    highest = detector.find_highest_point_in_range(test_candles, 0, 3)
    
    if lowest:
        print(f"✅ Lowest in range: {lowest}")
    if highest:
        print(f"✅ Highest in range: {highest}")

if __name__ == "__main__":
    test_pivot_detector()
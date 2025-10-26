"""
Enhanced Webhook Processor for V2 Automation
Processes comprehensive signal data for exact methodology implementation
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import pytz

class EnhancedSignalProcessor:
    """
    Processes enhanced signal data from TradingView for exact methodology automation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def process_enhanced_signal(self, webhook_data: Dict) -> Dict:
        """
        Process enhanced signal data and prepare for exact methodology implementation
        
        Args:
            webhook_data: Enhanced payload from TradingView indicator
            
        Returns:
            Processed signal data with methodology calculations
        """
        try:
            # Extract core signal data
            signal_type = webhook_data.get('signal_type')
            timestamp = webhook_data.get('timestamp')
            session = webhook_data.get('session')
            
            # Extract candle data
            signal_candle = webhook_data.get('signal_candle', {})
            previous_candle = webhook_data.get('previous_candle', {})
            historical_candles = webhook_data.get('historical_candles', [])
            
            # Extract market context
            market_context = webhook_data.get('market_context', {})
            methodology_data = webhook_data.get('methodology_data', {})
            
            # Validate session (reject invalid sessions)
            if session == "INVALID":
                self.logger.warning(f"Signal rejected - invalid session time")
                return {"status": "rejected", "reason": "invalid_session"}
            
            # Process signal based on type
            if signal_type == "Bullish":
                processed_data = self._process_bullish_signal(
                    signal_candle, historical_candles, market_context, methodology_data
                )
            elif signal_type == "Bearish":
                processed_data = self._process_bearish_signal(
                    signal_candle, historical_candles, market_context, methodology_data
                )
            else:
                return {"status": "error", "reason": "invalid_signal_type"}
            
            # Add common data
            processed_data.update({
                "signal_type": signal_type,
                "timestamp": timestamp,
                "session": session,
                "signal_candle": signal_candle,
                "market_context": market_context,
                "status": "processed"
            })
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing enhanced signal: {str(e)}")
            return {"status": "error", "reason": str(e)}
    
    def _process_bullish_signal(self, signal_candle: Dict, historical_candles: List, 
                               market_context: Dict, methodology_data: Dict) -> Dict:
        """Process bullish signal with exact methodology"""
        
        # Extract signal candle data
        signal_high = signal_candle.get('high')
        signal_low = signal_candle.get('low')
        signal_open = signal_candle.get('open')
        signal_close = signal_candle.get('close')
        
        # Find pivots for stop loss calculation
        pivot_analysis = self._analyze_pivots_for_bullish(historical_candles, signal_candle)
        
        # Calculate confirmation requirements
        confirmation_data = {
            "required": True,
            "condition": "candle_close_above_signal_high",
            "target_price": signal_high,
            "direction": "bullish"
        }
        
        # Calculate potential entry price (will be next candle open after confirmation)
        # This is estimated - actual entry will be determined when confirmation occurs
        estimated_entry = signal_high + 1  # Rough estimate
        
        # Calculate stop loss based on exact methodology
        stop_loss_data = self._calculate_bullish_stop_loss(
            signal_candle, historical_candles, pivot_analysis
        )
        
        # Calculate R-targets based on risk distance
        if stop_loss_data.get('stop_loss_price'):
            risk_distance = estimated_entry - stop_loss_data['stop_loss_price']
            r_targets = self._calculate_r_targets(estimated_entry, risk_distance, "bullish")
        else:
            r_targets = {}
        
        return {
            "confirmation_data": confirmation_data,
            "stop_loss_data": stop_loss_data,
            "pivot_analysis": pivot_analysis,
            "r_targets": r_targets,
            "estimated_entry": estimated_entry,
            "risk_distance": risk_distance if 'risk_distance' in locals() else None
        }
    
    def _process_bearish_signal(self, signal_candle: Dict, historical_candles: List,
                               market_context: Dict, methodology_data: Dict) -> Dict:
        """Process bearish signal with exact methodology"""
        
        # Extract signal candle data
        signal_high = signal_candle.get('high')
        signal_low = signal_candle.get('low')
        signal_open = signal_candle.get('open')
        signal_close = signal_candle.get('close')
        
        # Find pivots for stop loss calculation
        pivot_analysis = self._analyze_pivots_for_bearish(historical_candles, signal_candle)
        
        # Calculate confirmation requirements
        confirmation_data = {
            "required": True,
            "condition": "candle_close_below_signal_low",
            "target_price": signal_low,
            "direction": "bearish"
        }
        
        # Calculate potential entry price (will be next candle open after confirmation)
        estimated_entry = signal_low - 1  # Rough estimate
        
        # Calculate stop loss based on exact methodology
        stop_loss_data = self._calculate_bearish_stop_loss(
            signal_candle, historical_candles, pivot_analysis
        )
        
        # Calculate R-targets based on risk distance
        if stop_loss_data.get('stop_loss_price'):
            risk_distance = stop_loss_data['stop_loss_price'] - estimated_entry
            r_targets = self._calculate_r_targets(estimated_entry, risk_distance, "bearish")
        else:
            r_targets = {}
        
        return {
            "confirmation_data": confirmation_data,
            "stop_loss_data": stop_loss_data,
            "pivot_analysis": pivot_analysis,
            "r_targets": r_targets,
            "estimated_entry": estimated_entry,
            "risk_distance": risk_distance if 'risk_distance' in locals() else None
        }
    
    def _analyze_pivots_for_bullish(self, historical_candles: List, signal_candle: Dict) -> Dict:
        """Analyze pivots for bullish signal stop loss calculation"""
        
        pivots_found = []
        
        # Check historical candles for 3-candle pivots
        for i, candle in enumerate(historical_candles):
            if i > 0 and i < len(historical_candles) - 1:
                prev_candle = historical_candles[i-1]
                next_candle = historical_candles[i+1]
                
                # Check if this is a bullish pivot (low < both adjacent lows)
                if (candle['low'] < prev_candle['low'] and 
                    candle['low'] < next_candle['low']):
                    pivots_found.append({
                        "type": "bullish_pivot",
                        "price": candle['low'],
                        "index": i,
                        "candle_data": candle
                    })
        
        # Check if signal candle itself is a pivot
        signal_is_pivot = self._is_signal_candle_pivot(signal_candle, historical_candles, "bullish")
        
        return {
            "historical_pivots": pivots_found,
            "signal_is_pivot": signal_is_pivot,
            "pivot_count": len(pivots_found)
        }
    
    def _analyze_pivots_for_bearish(self, historical_candles: List, signal_candle: Dict) -> Dict:
        """Analyze pivots for bearish signal stop loss calculation"""
        
        pivots_found = []
        
        # Check historical candles for 3-candle pivots
        for i, candle in enumerate(historical_candles):
            if i > 0 and i < len(historical_candles) - 1:
                prev_candle = historical_candles[i-1]
                next_candle = historical_candles[i+1]
                
                # Check if this is a bearish pivot (high > both adjacent highs)
                if (candle['high'] > prev_candle['high'] and 
                    candle['high'] > next_candle['high']):
                    pivots_found.append({
                        "type": "bearish_pivot",
                        "price": candle['high'],
                        "index": i,
                        "candle_data": candle
                    })
        
        # Check if signal candle itself is a pivot
        signal_is_pivot = self._is_signal_candle_pivot(signal_candle, historical_candles, "bearish")
        
        return {
            "historical_pivots": pivots_found,
            "signal_is_pivot": signal_is_pivot,
            "pivot_count": len(pivots_found)
        }
    
    def _calculate_bullish_stop_loss(self, signal_candle: Dict, historical_candles: List, 
                                   pivot_analysis: Dict) -> Dict:
        """
        Calculate stop loss for bullish signal using exact methodology:
        1. Find lowest point from signal candle to confirmation candle
        2. If lowest point is 3-candle pivot: SL = pivot low - 25pts
        3. If lowest point is signal candle (and is pivot): SL = signal low - 25pts
        4. If lowest point is signal candle (not pivot): Search left 5 candles for pivot
        """
        
        signal_low = signal_candle.get('low')
        buffer_points = 25  # NASDAQ buffer
        
        # For now, we only have signal candle data (confirmation will come later)
        # We'll calculate based on available data and update when confirmation occurs
        
        stop_loss_scenarios = []
        
        # Scenario A: Check if signal candle is a pivot
        if pivot_analysis.get('signal_is_pivot'):
            stop_loss_price = signal_low - buffer_points
            stop_loss_scenarios.append({
                "scenario": "signal_candle_is_pivot",
                "stop_loss_price": stop_loss_price,
                "reasoning": "Signal candle is 3-candle pivot, SL = signal_low - 25pts"
            })
        
        # Scenario B: Find nearest historical pivot
        historical_pivots = pivot_analysis.get('historical_pivots', [])
        if historical_pivots:
            # Find closest pivot to signal candle
            closest_pivot = min(historical_pivots, 
                              key=lambda p: abs(p['price'] - signal_low))
            stop_loss_price = closest_pivot['price'] - buffer_points
            stop_loss_scenarios.append({
                "scenario": "historical_pivot_found",
                "stop_loss_price": stop_loss_price,
                "pivot_data": closest_pivot,
                "reasoning": "Using closest historical pivot - 25pts"
            })
        
        # Scenario C: Fallback to signal candle low
        fallback_stop_loss = signal_low - buffer_points
        stop_loss_scenarios.append({
            "scenario": "fallback_signal_low",
            "stop_loss_price": fallback_stop_loss,
            "reasoning": "Fallback: signal_low - 25pts (will refine after confirmation)"
        })
        
        # Use the most appropriate scenario (prefer pivot-based)
        primary_scenario = stop_loss_scenarios[0]
        
        return {
            "stop_loss_price": primary_scenario["stop_loss_price"],
            "primary_scenario": primary_scenario,
            "all_scenarios": stop_loss_scenarios,
            "buffer_points": buffer_points,
            "requires_confirmation_update": True
        }
    
    def _calculate_bearish_stop_loss(self, signal_candle: Dict, historical_candles: List,
                                   pivot_analysis: Dict) -> Dict:
        """Calculate stop loss for bearish signal using exact methodology"""
        
        signal_high = signal_candle.get('high')
        buffer_points = 25  # NASDAQ buffer
        
        stop_loss_scenarios = []
        
        # Scenario A: Check if signal candle is a pivot
        if pivot_analysis.get('signal_is_pivot'):
            stop_loss_price = signal_high + buffer_points
            stop_loss_scenarios.append({
                "scenario": "signal_candle_is_pivot",
                "stop_loss_price": stop_loss_price,
                "reasoning": "Signal candle is 3-candle pivot, SL = signal_high + 25pts"
            })
        
        # Scenario B: Find nearest historical pivot
        historical_pivots = pivot_analysis.get('historical_pivots', [])
        if historical_pivots:
            closest_pivot = min(historical_pivots, 
                              key=lambda p: abs(p['price'] - signal_high))
            stop_loss_price = closest_pivot['price'] + buffer_points
            stop_loss_scenarios.append({
                "scenario": "historical_pivot_found",
                "stop_loss_price": stop_loss_price,
                "pivot_data": closest_pivot,
                "reasoning": "Using closest historical pivot + 25pts"
            })
        
        # Scenario C: Fallback to signal candle high
        fallback_stop_loss = signal_high + buffer_points
        stop_loss_scenarios.append({
            "scenario": "fallback_signal_high",
            "stop_loss_price": fallback_stop_loss,
            "reasoning": "Fallback: signal_high + 25pts (will refine after confirmation)"
        })
        
        primary_scenario = stop_loss_scenarios[0]
        
        return {
            "stop_loss_price": primary_scenario["stop_loss_price"],
            "primary_scenario": primary_scenario,
            "all_scenarios": stop_loss_scenarios,
            "buffer_points": buffer_points,
            "requires_confirmation_update": True
        }
    
    def _calculate_r_targets(self, entry_price: float, risk_distance: float, direction: str) -> Dict:
        """Calculate R-multiple targets based on risk distance"""
        
        targets = {}
        
        # Calculate targets from 1R to 20R
        for r in range(1, 21):
            if direction == "bullish":
                target_price = entry_price + (r * risk_distance)
            else:  # bearish
                target_price = entry_price - (r * risk_distance)
            
            targets[f"{r}R"] = {
                "price": target_price,
                "r_multiple": r,
                "distance_from_entry": r * risk_distance
            }
        
        return targets
    
    def _is_signal_candle_pivot(self, signal_candle: Dict, historical_candles: List, 
                               signal_type: str) -> bool:
        """Check if signal candle forms a 3-candle pivot"""
        
        if len(historical_candles) < 2:
            return False
        
        # Get adjacent candles (previous and next)
        prev_candle = historical_candles[-1]  # Most recent historical candle
        # Next candle will be determined in real-time
        
        if signal_type == "bullish":
            # For bullish pivot: signal_low < prev_low and signal_low < next_low
            # We can only check previous candle for now
            return signal_candle['low'] < prev_candle['low']
        else:  # bearish
            # For bearish pivot: signal_high > prev_high and signal_high > next_high
            return signal_candle['high'] > prev_candle['high']

# Usage example for integration with web server
def process_enhanced_webhook(request_data):
    """
    Integration function for web server
    """
    processor = EnhancedSignalProcessor()
    
    try:
        # Parse JSON data from TradingView
        webhook_data = json.loads(request_data) if isinstance(request_data, str) else request_data
        
        # Process the enhanced signal
        processed_signal = processor.process_enhanced_signal(webhook_data)
        
        # Log the processing result
        logging.info(f"Enhanced signal processed: {processed_signal.get('status')}")
        
        return processed_signal
        
    except Exception as e:
        logging.error(f"Error in enhanced webhook processing: {str(e)}")
        return {"status": "error", "reason": str(e)}

if __name__ == "__main__":
    # Test the processor with sample data
    sample_data = {
        "signal_type": "Bullish",
        "timestamp": 1698765432000,
        "session": "NY AM",
        "signal_candle": {
            "open": 4155.0,
            "high": 4157.5,
            "low": 4154.0,
            "close": 4156.25,
            "volume": 1000,
            "timestamp": 1698765432000
        },
        "historical_candles": [
            {"open": 4150.0, "high": 4152.0, "low": 4149.0, "close": 4151.0, "volume": 800},
            {"open": 4151.0, "high": 4153.0, "low": 4150.5, "close": 4152.5, "volume": 900}
        ],
        "market_context": {
            "current_price": 4156.25,
            "atr": 15.5,
            "volume_avg": 850,
            "volatility": 12.3
        },
        "methodology_data": {
            "requires_confirmation": True,
            "confirmation_direction": "above_signal_high",
            "stop_loss_buffer": 25,
            "pivot_lookback": 5
        }
    }
    
    result = process_enhanced_webhook(sample_data)
    print(json.dumps(result, indent=2))
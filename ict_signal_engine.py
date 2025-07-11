#!/usr/bin/env python3
"""
ICT Signal Engine - Institutional Trading Concepts
Based on Patek Fynnip Methodology
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ICTSignalEngine:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')
        self.london_tz = pytz.timezone('Europe/London')
        self.utc_tz = pytz.UTC
        
        # Key Levels Storage
        self.key_levels = {
            'nwog': [],  # New Week Opening Gaps
            'ndog': [],  # New Day Opening Gaps  
            'mor': [],   # Midnight Opening Ranges
            'org': [],   # Opening Range Gaps
            'mop': [],   # Midnight Opening Prices
            'fvg': []    # Fair Value Gaps
        }
        
        # Session definitions (UTC times)
        self.sessions = {
            'london_open_kz': {'start': 2, 'end': 4},    # 2-4 AM UTC
            'ny_open_kz': {'start': 12, 'end': 14},      # 7-9 AM EST = 12-14 UTC
            'london_close': {'start': 15, 'end': 17},    # 10 AM-12 PM EST = 15-17 UTC
            'am_session': {'start': 14.5, 'end': 16.5},  # 9:30-11:30 AM EST
            'lunch': {'start': 17, 'end': 18.5},         # 12-1:30 PM EST
            'pm_session': {'start': 18.5, 'end': 21},    # 1:30-4 PM EST
            'cbdr': {'start': 21, 'end': 1},             # 4-8 PM EST
            'asia': {'start': 1, 'end': 6}               # 8 PM-1 AM EST
        }
        
        # Macro windows (EST times converted to minutes from midnight)
        self.macro_windows = [
            {'name': 'Opening_Range', 'start': 590, 'end': 610},      # 9:50-10:10 AM
            {'name': 'Pre_Lunch', 'start': 650, 'end': 670},         # 10:50-11:10 AM
            {'name': 'Lunch_Entry', 'start': 710, 'end': 730},       # 11:50 AM-12:10 PM
            {'name': 'Lunch_Exit', 'start': 770, 'end': 790},        # 12:50-1:10 PM
            {'name': 'PM_Start', 'start': 830, 'end': 850},          # 1:50-2:10 PM
            {'name': 'PM_Mid', 'start': 890, 'end': 910},            # 2:50-3:10 PM
            {'name': 'Final_Hour', 'start': 915, 'end': 945},        # 3:15-3:45 PM
            {'name': 'MOC', 'start': 945, 'end': 960}                # 3:45-4:00 PM
        ]
        
        # Current market state
        self.market_state = {
            'current_session': None,
            'active_macro': None,
            'bias': 'NEUTRAL',
            'liquidity_levels': [],
            'imbalances': [],
            'judas_swing_detected': False
        }
        
    def update_market_data(self, ohlcv_data: pd.DataFrame) -> Dict:
        """Process new market data and update all ICT concepts"""
        try:
            current_time = datetime.now(self.ny_tz)
            
            # Update key levels
            self._update_key_levels(ohlcv_data)
            
            # Determine current session
            self._update_current_session(current_time)
            
            # Check for active macro windows
            self._check_macro_windows(current_time)
            
            # Analyze market structure
            market_structure = self._analyze_market_structure(ohlcv_data)
            
            # Generate signals
            signals = self._generate_ict_signals(ohlcv_data, market_structure)
            
            return {
                'timestamp': current_time.isoformat(),
                'market_state': self.market_state,
                'key_levels': self.key_levels,
                'market_structure': market_structure,
                'signals': signals,
                'risk_assessment': self._assess_risk(ohlcv_data, signals)
            }
            
        except Exception as e:
            logger.error(f"ICT Signal Engine error: {e}")
            return {'error': str(e)}
    
    def _update_key_levels(self, data: pd.DataFrame):
        """Update all ICT key levels"""
        if len(data) < 2:
            return
            
        current_time = datetime.now(self.ny_tz)
        latest = data.iloc[-1]
        
        # Update NWOG (New Week Opening Gap)
        if current_time.weekday() == 6 and current_time.hour == 18:  # Sunday 6 PM
            friday_close = self._get_friday_close(data)
            if friday_close:
                gap_size = abs(latest['open'] - friday_close)
                self.key_levels['nwog'].append({
                    'timestamp': current_time,
                    'friday_close': friday_close,
                    'sunday_open': latest['open'],
                    'gap_size': gap_size,
                    'filled': False
                })
                # Keep only last 5
                self.key_levels['nwog'] = self.key_levels['nwog'][-5:]
        
        # Update NDOG (New Day Opening Gap)
        if current_time.hour == 18 and current_time.minute == 0:  # 6 PM daily
            prev_close = data.iloc[-2]['close'] if len(data) > 1 else latest['open']
            gap_size = abs(latest['open'] - prev_close)
            self.key_levels['ndog'].append({
                'timestamp': current_time,
                'prev_close': prev_close,
                'next_open': latest['open'],
                'gap_size': gap_size,
                'filled': False
            })
            self.key_levels['ndog'] = self.key_levels['ndog'][-5:]
        
        # Update MOR (Midnight Opening Range)
        if current_time.hour == 0 and current_time.minute <= 30:
            midnight_data = data[data.index >= current_time.replace(hour=0, minute=0)]
            if len(midnight_data) > 0:
                mor_high = midnight_data['high'].max()
                mor_low = midnight_data['low'].min()
                self.key_levels['mor'].append({
                    'timestamp': current_time,
                    'high': mor_high,
                    'low': mor_low,
                    'range_size': mor_high - mor_low
                })
                self.key_levels['mor'] = self.key_levels['mor'][-5:]
        
        # Update MOP (Midnight Opening Price)
        if current_time.hour == 0 and current_time.minute == 0:
            self.key_levels['mop'].append({
                'timestamp': current_time,
                'price': latest['open']
            })
            self.key_levels['mop'] = self.key_levels['mop'][-10:]
        
        # Detect Fair Value Gaps (FVG)
        self._detect_fvg(data)
    
    def _detect_fvg(self, data: pd.DataFrame):
        """Detect Fair Value Gaps in price action"""
        if len(data) < 3:
            return
            
        # Get last 3 candles
        candles = data.tail(3)
        c1, c2, c3 = candles.iloc[0], candles.iloc[1], candles.iloc[2]
        
        # Bullish FVG: c1_low > c3_high (gap between candle 1 and 3)
        if c1['low'] > c3['high']:
            self.key_levels['fvg'].append({
                'type': 'bullish',
                'timestamp': datetime.now(self.ny_tz),
                'top': c1['low'],
                'bottom': c3['high'],
                'filled': False
            })
        
        # Bearish FVG: c1_high < c3_low
        elif c1['high'] < c3['low']:
            self.key_levels['fvg'].append({
                'type': 'bearish',
                'timestamp': datetime.now(self.ny_tz),
                'top': c3['low'],
                'bottom': c1['high'],
                'filled': False
            })
        
        # Keep only recent FVGs
        self.key_levels['fvg'] = self.key_levels['fvg'][-20:]
    
    def _update_current_session(self, current_time: datetime):
        """Determine which trading session is currently active"""
        hour = current_time.hour
        minute = current_time.minute
        
        for session_name, times in self.sessions.items():
            start_hour = int(times['start'])
            start_min = int((times['start'] % 1) * 60)
            end_hour = int(times['end'])
            end_min = int((times['end'] % 1) * 60)
            
            # Handle sessions that cross midnight
            if start_hour > end_hour:
                if (hour > start_hour or (hour == start_hour and minute >= start_min)) or \
                   (hour < end_hour or (hour == end_hour and minute <= end_min)):
                    self.market_state['current_session'] = session_name
                    return
            else:
                if (hour > start_hour or (hour == start_hour and minute >= start_min)) and \
                   (hour < end_hour or (hour == end_hour and minute <= end_min)):
                    self.market_state['current_session'] = session_name
                    return
        
        self.market_state['current_session'] = 'off_hours'
    
    def _check_macro_windows(self, current_time: datetime):
        """Check if we're in an active macro window"""
        minutes_from_midnight = current_time.hour * 60 + current_time.minute
        
        for macro in self.macro_windows:
            if macro['start'] <= minutes_from_midnight <= macro['end']:
                self.market_state['active_macro'] = macro['name']
                return
        
        self.market_state['active_macro'] = None
    
    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict:
        """Analyze current market structure for bias and liquidity"""
        if len(data) < 20:
            return {'bias': 'NEUTRAL', 'structure': 'RANGING'}
        
        # Calculate recent highs and lows
        recent_data = data.tail(20)
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        
        # Determine market structure
        higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        higher_lows = sum(1 for i in range(1, len(lows)) if lows[i] > lows[i-1])
        lower_highs = sum(1 for i in range(1, len(highs)) if highs[i] < highs[i-1])
        lower_lows = sum(1 for i in range(1, len(lows)) if lows[i] < lows[i-1])
        
        # Determine bias
        if higher_highs >= 3 and higher_lows >= 2:
            bias = 'BULLISH'
            structure = 'UPTREND'
        elif lower_highs >= 3 and lower_lows >= 2:
            bias = 'BEARISH'
            structure = 'DOWNTREND'
        else:
            bias = 'NEUTRAL'
            structure = 'RANGING'
        
        self.market_state['bias'] = bias
        
        # Identify liquidity levels
        liquidity_levels = self._identify_liquidity_levels(data)
        
        return {
            'bias': bias,
            'structure': structure,
            'liquidity_levels': liquidity_levels,
            'recent_high': recent_data['high'].max(),
            'recent_low': recent_data['low'].min(),
            'structure_strength': max(higher_highs + higher_lows, lower_highs + lower_lows) / 10
        }
    
    def _identify_liquidity_levels(self, data: pd.DataFrame) -> List[Dict]:
        """Identify key liquidity levels (support/resistance)"""
        if len(data) < 50:
            return []
        
        liquidity_levels = []
        recent_data = data.tail(50)
        
        # Find swing highs and lows
        for i in range(2, len(recent_data) - 2):
            current = recent_data.iloc[i]
            
            # Swing high
            if (current['high'] > recent_data.iloc[i-1]['high'] and 
                current['high'] > recent_data.iloc[i-2]['high'] and
                current['high'] > recent_data.iloc[i+1]['high'] and
                current['high'] > recent_data.iloc[i+2]['high']):
                
                liquidity_levels.append({
                    'type': 'resistance',
                    'price': current['high'],
                    'timestamp': current.name,
                    'strength': self._calculate_level_strength(recent_data, current['high'])
                })
            
            # Swing low
            if (current['low'] < recent_data.iloc[i-1]['low'] and 
                current['low'] < recent_data.iloc[i-2]['low'] and
                current['low'] < recent_data.iloc[i+1]['low'] and
                current['low'] < recent_data.iloc[i+2]['low']):
                
                liquidity_levels.append({
                    'type': 'support',
                    'price': current['low'],
                    'timestamp': current.name,
                    'strength': self._calculate_level_strength(recent_data, current['low'])
                })
        
        # Sort by strength and return top levels
        liquidity_levels.sort(key=lambda x: x['strength'], reverse=True)
        return liquidity_levels[:10]
    
    def _calculate_level_strength(self, data: pd.DataFrame, level: float) -> float:
        """Calculate the strength of a support/resistance level"""
        touches = 0
        tolerance = level * 0.001  # 0.1% tolerance
        
        for _, candle in data.iterrows():
            if abs(candle['high'] - level) <= tolerance or abs(candle['low'] - level) <= tolerance:
                touches += 1
        
        return touches
    
    def _generate_ict_signals(self, data: pd.DataFrame, market_structure: Dict) -> List[Dict]:
        """Generate ICT-based trading signals"""
        signals = []
        
        if len(data) < 10:
            return signals
        
        current_time = datetime.now(self.ny_tz)
        latest = data.iloc[-1]
        current_session = self.market_state['current_session']
        active_macro = self.market_state['active_macro']
        
        # Signal generation based on session and macro windows
        if active_macro and current_session in ['am_session', 'pm_session']:
            
            # Opening Range Macro (9:50-10:10 AM)
            if active_macro == 'Opening_Range':
                signal = self._opening_range_signal(data, market_structure)
                if signal:
                    signals.append(signal)
            
            # Pre-Lunch Macro (10:50-11:10 AM)
            elif active_macro == 'Pre_Lunch':
                signal = self._pre_lunch_signal(data, market_structure)
                if signal:
                    signals.append(signal)
            
            # PM Session Macros
            elif active_macro in ['PM_Start', 'PM_Mid']:
                signal = self._pm_session_signal(data, market_structure)
                if signal:
                    signals.append(signal)
        
        # FVG-based signals
        fvg_signal = self._fvg_signal(data, latest)
        if fvg_signal:
            signals.append(fvg_signal)
        
        # Liquidity sweep signals
        sweep_signal = self._liquidity_sweep_signal(data, market_structure)
        if sweep_signal:
            signals.append(sweep_signal)
        
        return signals
    
    def _opening_range_signal(self, data: pd.DataFrame, structure: Dict) -> Optional[Dict]:
        """Generate signal during opening range macro"""
        if structure['bias'] == 'NEUTRAL':
            return None
        
        latest = data.iloc[-1]
        or_data = data.tail(20)  # Last 20 minutes of data
        
        # Look for consolidation break
        or_high = or_data['high'].max()
        or_low = or_data['low'].min()
        or_range = or_high - or_low
        
        if or_range < latest['close'] * 0.002:  # Tight consolidation
            if structure['bias'] == 'BULLISH' and latest['close'] > or_high:
                return {
                    'type': 'LONG',
                    'entry': latest['close'],
                    'stop_loss': or_low,
                    'take_profit': latest['close'] + (or_range * 2),
                    'confidence': 0.75,
                    'reason': 'Opening Range Bullish Breakout',
                    'macro': 'Opening_Range'
                }
            elif structure['bias'] == 'BEARISH' and latest['close'] < or_low:
                return {
                    'type': 'SHORT',
                    'entry': latest['close'],
                    'stop_loss': or_high,
                    'take_profit': latest['close'] - (or_range * 2),
                    'confidence': 0.75,
                    'reason': 'Opening Range Bearish Breakdown',
                    'macro': 'Opening_Range'
                }
        
        return None
    
    def _pre_lunch_signal(self, data: pd.DataFrame, structure: Dict) -> Optional[Dict]:
        """Generate signal during pre-lunch macro"""
        # Look for liquidity runs before lunch consolidation
        latest = data.iloc[-1]
        am_session_high = data.tail(60)['high'].max()
        am_session_low = data.tail(60)['low'].min()
        
        # Check for liquidity sweep
        if latest['high'] > am_session_high and structure['bias'] == 'BEARISH':
            return {
                'type': 'SHORT',
                'entry': latest['close'],
                'stop_loss': latest['high'] + (latest['close'] * 0.001),
                'take_profit': am_session_low,
                'confidence': 0.70,
                'reason': 'Pre-Lunch Liquidity Sweep Short',
                'macro': 'Pre_Lunch'
            }
        elif latest['low'] < am_session_low and structure['bias'] == 'BULLISH':
            return {
                'type': 'LONG',
                'entry': latest['close'],
                'stop_loss': latest['low'] - (latest['close'] * 0.001),
                'take_profit': am_session_high,
                'confidence': 0.70,
                'reason': 'Pre-Lunch Liquidity Sweep Long',
                'macro': 'Pre_Lunch'
            }
        
        return None
    
    def _pm_session_signal(self, data: pd.DataFrame, structure: Dict) -> Optional[Dict]:
        """Generate signal during PM session macros"""
        latest = data.iloc[-1]
        
        # Look for continuation of AM session bias or reversal
        am_data = data.between_time('09:30', '11:30') if hasattr(data.index, 'time') else data.tail(120)
        lunch_data = data.tail(30)
        
        if len(am_data) > 0 and len(lunch_data) > 0:
            am_high = am_data['high'].max()
            am_low = am_data['low'].min()
            lunch_high = lunch_data['high'].max()
            lunch_low = lunch_data['low'].min()
            
            # PM continuation signal
            if structure['bias'] == 'BULLISH' and latest['close'] > lunch_high:
                return {
                    'type': 'LONG',
                    'entry': latest['close'],
                    'stop_loss': lunch_low,
                    'take_profit': am_high + (am_high - am_low),
                    'confidence': 0.65,
                    'reason': 'PM Session Bullish Continuation',
                    'macro': self.market_state['active_macro']
                }
            elif structure['bias'] == 'BEARISH' and latest['close'] < lunch_low:
                return {
                    'type': 'SHORT',
                    'entry': latest['close'],
                    'stop_loss': lunch_high,
                    'take_profit': am_low - (am_high - am_low),
                    'confidence': 0.65,
                    'reason': 'PM Session Bearish Continuation',
                    'macro': self.market_state['active_macro']
                }
        
        return None
    
    def _fvg_signal(self, data: pd.DataFrame, latest: pd.Series) -> Optional[Dict]:
        """Generate signals based on Fair Value Gap interactions"""
        for fvg in self.key_levels['fvg']:
            if fvg['filled']:
                continue
            
            # Check if price is interacting with FVG
            if fvg['bottom'] <= latest['close'] <= fvg['top']:
                if fvg['type'] == 'bullish':
                    return {
                        'type': 'LONG',
                        'entry': latest['close'],
                        'stop_loss': fvg['bottom'] - (latest['close'] * 0.001),
                        'take_profit': fvg['top'] + (fvg['top'] - fvg['bottom']),
                        'confidence': 0.60,
                        'reason': 'Bullish FVG Interaction',
                        'fvg_level': fvg
                    }
                else:
                    return {
                        'type': 'SHORT',
                        'entry': latest['close'],
                        'stop_loss': fvg['top'] + (latest['close'] * 0.001),
                        'take_profit': fvg['bottom'] - (fvg['top'] - fvg['bottom']),
                        'confidence': 0.60,
                        'reason': 'Bearish FVG Interaction',
                        'fvg_level': fvg
                    }
        
        return None
    
    def _liquidity_sweep_signal(self, data: pd.DataFrame, structure: Dict) -> Optional[Dict]:
        """Generate signals based on liquidity sweeps"""
        if len(structure['liquidity_levels']) == 0:
            return None
        
        latest = data.iloc[-1]
        
        for level in structure['liquidity_levels']:
            tolerance = latest['close'] * 0.0005  # 0.05% tolerance
            
            # Check for liquidity sweep
            if level['type'] == 'resistance' and latest['high'] > level['price'] + tolerance:
                if structure['bias'] == 'BEARISH':
                    return {
                        'type': 'SHORT',
                        'entry': latest['close'],
                        'stop_loss': latest['high'] + tolerance,
                        'take_profit': level['price'] - (latest['high'] - level['price']),
                        'confidence': 0.70,
                        'reason': 'Resistance Liquidity Sweep',
                        'swept_level': level
                    }
            
            elif level['type'] == 'support' and latest['low'] < level['price'] - tolerance:
                if structure['bias'] == 'BULLISH':
                    return {
                        'type': 'LONG',
                        'entry': latest['close'],
                        'stop_loss': latest['low'] - tolerance,
                        'take_profit': level['price'] + (level['price'] - latest['low']),
                        'confidence': 0.70,
                        'reason': 'Support Liquidity Sweep',
                        'swept_level': level
                    }
        
        return None
    
    def _assess_risk(self, data: pd.DataFrame, signals: List[Dict]) -> Dict:
        """Assess risk for generated signals"""
        if not signals:
            return {'risk_level': 'LOW', 'max_position_size': 0}
        
        latest = data.iloc[-1]
        atr = self._calculate_atr(data.tail(14))
        
        risk_factors = []
        
        # Session risk
        if self.market_state['current_session'] in ['cbdr', 'asia']:
            risk_factors.append('OFF_HOURS_SESSION')
        
        # Volatility risk
        if atr > latest['close'] * 0.02:  # High volatility
            risk_factors.append('HIGH_VOLATILITY')
        
        # Multiple signals risk
        if len(signals) > 2:
            risk_factors.append('MULTIPLE_SIGNALS')
        
        # Calculate risk level
        if len(risk_factors) >= 3:
            risk_level = 'HIGH'
            max_position_size = 0.5
        elif len(risk_factors) >= 1:
            risk_level = 'MEDIUM'
            max_position_size = 1.0
        else:
            risk_level = 'LOW'
            max_position_size = 2.0
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'max_position_size': max_position_size,
            'atr': atr,
            'volatility_percentile': self._calculate_volatility_percentile(data)
        }
    
    def _calculate_atr(self, data: pd.DataFrame) -> float:
        """Calculate Average True Range"""
        if len(data) < 2:
            return 0.0
        
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.mean()
    
    def _calculate_volatility_percentile(self, data: pd.DataFrame) -> float:
        """Calculate current volatility percentile"""
        if len(data) < 20:
            return 50.0
        
        recent_atr = self._calculate_atr(data.tail(14))
        historical_atrs = [self._calculate_atr(data.iloc[i:i+14]) for i in range(len(data)-14)]
        
        if not historical_atrs:
            return 50.0
        
        percentile = (sum(1 for atr in historical_atrs if atr < recent_atr) / len(historical_atrs)) * 100
        return percentile
    
    def _get_friday_close(self, data: pd.DataFrame) -> Optional[float]:
        """Get Friday's closing price for NWOG calculation"""
        # This would need to be implemented based on your data structure
        # For now, return the previous close
        if len(data) > 1:
            return data.iloc[-2]['close']
        return None
    
    def get_current_analysis(self) -> Dict:
        """Get current market analysis summary"""
        return {
            'timestamp': datetime.now(self.ny_tz).isoformat(),
            'market_state': self.market_state,
            'active_levels': {
                'nwog_count': len([x for x in self.key_levels['nwog'] if not x.get('filled', True)]),
                'ndog_count': len([x for x in self.key_levels['ndog'] if not x.get('filled', True)]),
                'fvg_count': len([x for x in self.key_levels['fvg'] if not x.get('filled', True)]),
                'mor_count': len(self.key_levels['mor'])
            },
            'session_info': {
                'current': self.market_state['current_session'],
                'macro_active': self.market_state['active_macro'],
                'bias': self.market_state['bias']
            }
        }
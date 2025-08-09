#!/usr/bin/env python3
"""
Patek Fynnip ICT Trading System
Pure ICT methodology focused on key levels and Draw on Liquidity (DOL)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import yfinance as yf
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

logger = logging.getLogger(__name__)

@dataclass
class KeyLevel:
    level_type: str  # NWOG, NDOG, MOR, ORG, MOP, 1st_Pres
    timestamp: datetime
    high: float
    low: float
    open_price: Optional[float] = None
    close_price: Optional[float] = None
    filled: bool = False
    interaction_count: int = 0
    strength: str = "WEAK"  # WEAK, MEDIUM, STRONG

@dataclass
class DrawOnLiquidity:
    target_level: float
    level_type: str  # Support, Resistance, Gap_Fill, etc.
    probability: float  # 0-100%
    timeframe: str  # Daily, Weekly, Intraday
    reasoning: str
    distance_pips: float
    expected_reaction: str  # Bounce, Break, Fill

class PatekICTSystem:
    def __init__(self, symbol: str = 'NQ=F'):
        self.symbol = symbol
        self.ny_tz = pytz.timezone('America/New_York')
        
        # Key Levels Storage (Patek's focus)
        self.nwog_levels = []  # New Week Opening Gaps (last 5)
        self.ndog_levels = []  # New Day Opening Gaps (last 5)
        self.mor_levels = []   # Midnight Opening Ranges (last 5)
        self.org_levels = []   # Opening Range Gaps (current week)
        self.mop_levels = []   # Midnight Opening Prices (last 10)
        self.first_pres = []   # First Presentations/FVGs (last 5)
        
        # Current Analysis
        self.current_bias = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
        self.daily_dol = []  # Draw on Liquidity targets
        self.weekly_dol = []
        self.intraday_dol = []
        
        # Market Data
        self.weekly_data = pd.DataFrame()
        self.daily_data = pd.DataFrame()
        self.h1_data = pd.DataFrame()
        self.m15_data = pd.DataFrame()
        self.m5_data = pd.DataFrame()
        self.m1_data = pd.DataFrame()
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
        
    def update_all_timeframes(self):
        """Update all timeframe data - Patek's multi-timeframe approach"""
        try:
            ticker = yf.Ticker(self.symbol)
            
            # Weekly data for key levels and bias
            self.weekly_data = ticker.history(period='1y', interval='1wk')
            
            # Daily data for ranges and DOL
            self.daily_data = ticker.history(period='3mo', interval='1d')
            
            # Intraday data for execution
            self.h1_data = ticker.history(period='5d', interval='1h')
            self.m15_data = ticker.history(period='2d', interval='15m')
            self.m5_data = ticker.history(period='1d', interval='5m')
            self.m1_data = ticker.history(period='1d', interval='1m')
            
            # Process all key levels
            self._update_key_levels()
            
            # Analyze Draw on Liquidity
            self._analyze_draw_on_liquidity()
            
            logger.info("✅ All timeframes updated")
            
        except Exception as e:
            logger.error(f"Data update error: {e}")
    
    def _update_key_levels(self):
        """Update all ICT key levels per Patek's methodology"""
        
        # 1. NWOG - New Week Opening Gaps (Fri 5PM - Sun 6PM)
        self._update_nwog()
        
        # 2. NDOG - New Day Opening Gaps (5PM - 6PM daily)
        self._update_ndog()
        
        # 3. MOR - Midnight Opening Ranges (12:00-12:30 AM)
        self._update_mor()
        
        # 4. ORG - Opening Range Gaps (4:15PM - 9:30AM)
        self._update_org()
        
        # 5. MOP - Midnight Opening Prices
        self._update_mop()
        
        # 6. First Presentations (FVGs in opening ranges)
        self._update_first_presentations()
    
    def _update_nwog(self):
        """New Week Opening Gaps - Friday 5PM to Sunday 6PM"""
        if len(self.weekly_data) < 2:
            return
            
        self.nwog_levels = []
        
        for i in range(len(self.weekly_data) - 5, len(self.weekly_data)):
            if i <= 0:
                continue
                
            current_week = self.weekly_data.iloc[i]
            prev_week = self.weekly_data.iloc[i-1]
            
            # Gap between Friday close and Sunday open
            gap_size = abs(current_week['Open'] - prev_week['Close'])
            
            if gap_size > 0:
                level = KeyLevel(
                    level_type="NWOG",
                    timestamp=current_week.name,
                    high=max(current_week['Open'], prev_week['Close']),
                    low=min(current_week['Open'], prev_week['Close']),
                    open_price=current_week['Open'],
                    close_price=prev_week['Close']
                )
                
                # Check if gap has been filled
                level.filled = self._check_gap_filled(level, self.daily_data)
                level.strength = "STRONG" if gap_size > current_week['Close'] * 0.02 else "MEDIUM"
                
                self.nwog_levels.append(level)
        
        # Keep only last 5
        self.nwog_levels = self.nwog_levels[-5:]
    
    def _update_ndog(self):
        """New Day Opening Gaps - 5PM to 6PM daily"""
        if len(self.daily_data) < 2:
            return
            
        self.ndog_levels = []
        
        for i in range(len(self.daily_data) - 5, len(self.daily_data)):
            if i <= 0:
                continue
                
            current_day = self.daily_data.iloc[i]
            prev_day = self.daily_data.iloc[i-1]
            
            gap_size = abs(current_day['Open'] - prev_day['Close'])
            
            if gap_size > 0:
                level = KeyLevel(
                    level_type="NDOG",
                    timestamp=current_day.name,
                    high=max(current_day['Open'], prev_day['Close']),
                    low=min(current_day['Open'], prev_day['Close']),
                    open_price=current_day['Open'],
                    close_price=prev_day['Close']
                )
                
                level.filled = self._check_gap_filled(level, self.h1_data)
                level.strength = self._calculate_gap_strength(gap_size, current_day['Close'])
                
                self.ndog_levels.append(level)
        
        self.ndog_levels = self.ndog_levels[-5:]
    
    def _update_mor(self):
        """Midnight Opening Ranges - 12:00-12:30 AM"""
        if len(self.h1_data) < 24:
            return
            
        self.mor_levels = []
        
        # Look for midnight hours in hourly data
        for i in range(len(self.h1_data) - 120, len(self.h1_data)):  # Last 5 days
            if i <= 0:
                continue
                
            candle = self.h1_data.iloc[i]
            candle_time = candle.name.tz_convert(self.ny_tz)
            
            # Check if this is midnight hour (12 AM EST)
            if candle_time.hour == 0:
                # Get next 30 minutes of data for range
                end_idx = min(i + 1, len(self.h1_data) - 1)
                range_data = self.h1_data.iloc[i:end_idx + 1]
                
                level = KeyLevel(
                    level_type="MOR",
                    timestamp=candle_time,
                    high=range_data['High'].max(),
                    low=range_data['Low'].min(),
                    open_price=candle['Open']
                )
                
                level.strength = "STRONG"  # MOR always important
                self.mor_levels.append(level)
        
        self.mor_levels = self.mor_levels[-5:]
    
    def _update_org(self):
        """Opening Range Gaps - 4:15PM close to 9:30AM open"""
        if len(self.daily_data) < 7:
            return
            
        self.org_levels = []
        current_week_start = datetime.now(self.ny_tz) - timedelta(days=7)
        
        for i in range(len(self.daily_data) - 7, len(self.daily_data)):
            if i <= 0:
                continue
                
            current_day = self.daily_data.iloc[i]
            
            if current_day.name >= current_week_start:
                # This is current week data
                prev_day = self.daily_data.iloc[i-1] if i > 0 else None
                
                if prev_day is not None:
                    gap_size = abs(current_day['Open'] - prev_day['Close'])
                    
                    if gap_size > 0:
                        level = KeyLevel(
                            level_type="ORG",
                            timestamp=current_day.name,
                            high=max(current_day['Open'], prev_day['Close']),
                            low=min(current_day['Open'], prev_day['Close']),
                            open_price=current_day['Open'],
                            close_price=prev_day['Close']
                        )
                        
                        # NQ-specific gap analysis (Patek's rules)
                        level.strength = self._analyze_nq_gap(gap_size, current_day['Close'])
                        level.filled = self._check_gap_filled(level, self.h1_data)
                        
                        self.org_levels.append(level)
    
    def _update_mop(self):
        """Midnight Opening Prices"""
        if len(self.h1_data) < 24:
            return
            
        self.mop_levels = []
        
        for i in range(len(self.h1_data) - 240, len(self.h1_data)):  # Last 10 days
            if i <= 0:
                continue
                
            candle = self.h1_data.iloc[i]
            candle_time = candle.name.tz_convert(self.ny_tz)
            
            if candle_time.hour == 0 and candle_time.minute == 0:
                level = KeyLevel(
                    level_type="MOP",
                    timestamp=candle_time,
                    high=candle['Open'],
                    low=candle['Open'],
                    open_price=candle['Open']
                )
                
                # Check how many times price has reacted to this MOP
                level.interaction_count = self._count_level_interactions(candle['Open'], self.h1_data)
                level.strength = "STRONG" if level.interaction_count >= 3 else "MEDIUM"
                
                self.mop_levels.append(level)
        
        self.mop_levels = self.mop_levels[-10:]
    
    def _update_first_presentations(self):
        """First FVGs in opening ranges (9:30-10AM, 12-12:30AM, 1:30-2PM)"""
        if len(self.m15_data) < 50:
            return
            
        self.first_pres = []
        
        # Look for FVGs in key opening ranges
        opening_ranges = [
            (9.5, 10),    # 9:30-10:00 AM
            (0, 0.5),     # 12:00-12:30 AM  
            (13.5, 14)    # 1:30-2:00 PM
        ]
        
        for i in range(len(self.m15_data) - 200, len(self.m15_data) - 3):
            if i <= 2:
                continue
                
            candle_time = self.m15_data.iloc[i].name.tz_convert(self.ny_tz)
            hour_decimal = candle_time.hour + candle_time.minute / 60
            
            # Check if in opening range
            in_opening_range = any(start <= hour_decimal <= end for start, end in opening_ranges)
            
            if in_opening_range:
                # Check for FVG (3-candle pattern)
                c1 = self.m15_data.iloc[i-2]
                c2 = self.m15_data.iloc[i-1] 
                c3 = self.m15_data.iloc[i]
                
                # Bullish FVG
                if c1['Low'] > c3['High']:
                    level = KeyLevel(
                        level_type="1st_Pres_Bull",
                        timestamp=candle_time,
                        high=c1['Low'],
                        low=c3['High']
                    )
                    level.strength = "STRONG"
                    self.first_pres.append(level)
                
                # Bearish FVG
                elif c1['High'] < c3['Low']:
                    level = KeyLevel(
                        level_type="1st_Pres_Bear", 
                        timestamp=candle_time,
                        high=c3['Low'],
                        low=c1['High']
                    )
                    level.strength = "STRONG"
                    self.first_pres.append(level)
        
        self.first_pres = self.first_pres[-5:]
    
    def _analyze_draw_on_liquidity(self):
        """Analyze where price is likely to be drawn - Patek's DOL concept"""
        
        self.daily_dol = []
        self.weekly_dol = []
        self.intraday_dol = []
        
        if len(self.daily_data) < 20:
            return
        
        current_price = self.daily_data.iloc[-1]['Close']
        
        # 1. WEEKLY DOL - Major levels price wants to reach
        self._analyze_weekly_dol(current_price)
        
        # 2. DAILY DOL - Today's likely targets
        self._analyze_daily_dol(current_price)
        
        # 3. INTRADAY DOL - Session targets
        self._analyze_intraday_dol(current_price)
    
    def _analyze_weekly_dol(self, current_price: float):
        """Weekly Draw on Liquidity targets"""
        if len(self.weekly_data) < 10:
            return
        
        # Previous week high/low
        prev_week = self.weekly_data.iloc[-2]
        current_week = self.weekly_data.iloc[-1]
        
        # Weekly range analysis
        weekly_high = self.weekly_data['High'].tail(4).max()
        weekly_low = self.weekly_data['Low'].tail(4).min()
        
        # Unfilled NWOG levels
        for nwog in self.nwog_levels:
            if not nwog.filled:
                probability = 85 if nwog.strength == "STRONG" else 65
                
                self.weekly_dol.append(DrawOnLiquidity(
                    target_level=(nwog.high + nwog.low) / 2,
                    level_type="NWOG_Fill",
                    probability=probability,
                    timeframe="Weekly",
                    reasoning=f"Unfilled NWOG from {nwog.timestamp.strftime('%Y-%m-%d')}",
                    distance_pips=abs(current_price - (nwog.high + nwog.low) / 2),
                    expected_reaction="Fill_and_Reverse"
                ))
        
        # Weekly highs/lows as liquidity
        if current_price < weekly_high * 0.98:
            self.weekly_dol.append(DrawOnLiquidity(
                target_level=weekly_high,
                level_type="Weekly_High_Liquidity",
                probability=75,
                timeframe="Weekly", 
                reasoning="Weekly high liquidity sweep target",
                distance_pips=abs(current_price - weekly_high),
                expected_reaction="Sweep_and_Reverse"
            ))
    
    def _analyze_daily_dol(self, current_price: float):
        """Daily Draw on Liquidity targets"""
        if len(self.daily_data) < 5:
            return
        
        today = self.daily_data.iloc[-1]
        yesterday = self.daily_data.iloc[-2]
        
        # Previous day high/low
        prev_high = yesterday['High']
        prev_low = yesterday['Low']
        
        # Today's range
        today_high = today['High']
        today_low = today['Low']
        
        # Unfilled daily gaps
        for ndog in self.ndog_levels:
            if not ndog.filled:
                gap_mid = (ndog.high + ndog.low) / 2
                probability = self._calculate_gap_fill_probability(ndog, current_price)
                
                self.daily_dol.append(DrawOnLiquidity(
                    target_level=gap_mid,
                    level_type="NDOG_Fill",
                    probability=probability,
                    timeframe="Daily",
                    reasoning=f"Unfilled daily gap from {ndog.timestamp.strftime('%Y-%m-%d')}",
                    distance_pips=abs(current_price - gap_mid),
                    expected_reaction="Fill_and_Continue" if probability > 70 else "Fill_and_Reverse"
                ))
        
        # Previous day liquidity
        if current_price > prev_low * 1.002:  # Above yesterday's low
            self.daily_dol.append(DrawOnLiquidity(
                target_level=prev_low,
                level_type="Previous_Day_Low",
                probability=60,
                timeframe="Daily",
                reasoning="Previous day low liquidity target",
                distance_pips=abs(current_price - prev_low),
                expected_reaction="Test_and_Bounce"
            ))
        
        if current_price < prev_high * 0.998:  # Below yesterday's high
            self.daily_dol.append(DrawOnLiquidity(
                target_level=prev_high,
                level_type="Previous_Day_High", 
                probability=60,
                timeframe="Daily",
                reasoning="Previous day high liquidity target",
                distance_pips=abs(current_price - prev_high),
                expected_reaction="Test_and_Reject"
            ))
    
    def _analyze_intraday_dol(self, current_price: float):
        """Intraday Draw on Liquidity targets"""
        if len(self.h1_data) < 10:
            return
        
        # Session highs/lows
        london_session = self.h1_data.between_time('02:00', '11:00')
        ny_session = self.h1_data.between_time('09:30', '16:00')
        
        if not london_session.empty:
            london_high = london_session['High'].max()
            london_low = london_session['Low'].min()
            
            # London session liquidity
            if abs(current_price - london_high) < current_price * 0.01:
                self.intraday_dol.append(DrawOnLiquidity(
                    target_level=london_high,
                    level_type="London_High",
                    probability=70,
                    timeframe="Intraday",
                    reasoning="London session high liquidity",
                    distance_pips=abs(current_price - london_high),
                    expected_reaction="Sweep_and_Reverse"
                ))
        
        # MOP levels as magnets
        for mop in self.mop_levels[-3:]:  # Last 3 MOPs
            if abs(current_price - mop.open_price) < current_price * 0.005:
                self.intraday_dol.append(DrawOnLiquidity(
                    target_level=mop.open_price,
                    level_type="MOP_Magnet",
                    probability=65,
                    timeframe="Intraday", 
                    reasoning=f"MOP from {mop.timestamp.strftime('%m-%d %H:%M')}",
                    distance_pips=abs(current_price - mop.open_price),
                    expected_reaction="React_and_Continue"
                ))
    
    def _analyze_nq_gap(self, gap_size: float, current_price: float) -> str:
        """Analyze NQ gap per Patek's rules"""
        gap_handles = gap_size
        
        if 20 <= gap_handles <= 75:
            return "MEDIUM"  # Usually trades to overnight high/low then 50% retrace
        elif 75 <= gap_handles <= 120:
            return "STRONG"  # Sweet spot, wait for 10 AM direction
        elif gap_handles >= 120:
            return "VERY_STRONG"  # May leave unfilled or use 25% level
        else:
            return "WEAK"
    
    def _calculate_gap_fill_probability(self, gap: KeyLevel, current_price: float) -> float:
        """Calculate probability of gap fill based on Patek's analysis"""
        gap_size = gap.high - gap.low
        gap_handles = gap_size
        
        # NQ-specific probabilities
        if gap.level_type == "NDOG":
            if 20 <= gap_handles <= 75:
                return 85.0  # High probability
            elif 75 <= gap_handles <= 120:
                return 65.0  # Medium probability  
            elif gap_handles >= 120:
                return 35.0  # Low probability
        
        return 50.0  # Default
    
    def _check_gap_filled(self, gap: KeyLevel, data: pd.DataFrame) -> bool:
        """Check if gap has been filled"""
        if data.empty:
            return False
        
        gap_time = gap.timestamp
        future_data = data[data.index > gap_time]
        
        if future_data.empty:
            return False
        
        # Check if price has traded through the gap
        gap_high = gap.high
        gap_low = gap.low
        
        for _, candle in future_data.iterrows():
            if candle['Low'] <= gap_low and candle['High'] >= gap_high:
                return True
        
        return False
    
    def _count_level_interactions(self, level: float, data: pd.DataFrame) -> int:
        """Count how many times price has interacted with a level"""
        if data.empty:
            return 0
        
        tolerance = level * 0.001  # 0.1% tolerance
        interactions = 0
        
        for _, candle in data.iterrows():
            if abs(candle['High'] - level) <= tolerance or abs(candle['Low'] - level) <= tolerance:
                interactions += 1
        
        return interactions
    
    def _calculate_gap_strength(self, gap_size: float, price: float) -> str:
        """Calculate gap strength"""
        gap_percentage = (gap_size / price) * 100
        
        if gap_percentage >= 2.0:
            return "VERY_STRONG"
        elif gap_percentage >= 1.0:
            return "STRONG"
        elif gap_percentage >= 0.5:
            return "MEDIUM"
        else:
            return "WEAK"
    
    def get_current_analysis(self) -> Dict:
        """Get complete ICT analysis per Patek's method"""
        current_price = self.daily_data.iloc[-1]['Close'] if not self.daily_data.empty else 0
        
        return {
            'timestamp': datetime.now(self.ny_tz).isoformat(),
            'symbol': self.symbol,
            'current_price': current_price,
            'current_bias': self.current_bias,
            
            # Key Levels (Patek's focus)
            'key_levels': {
                'nwog': [self._level_to_dict(level) for level in self.nwog_levels],
                'ndog': [self._level_to_dict(level) for level in self.ndog_levels],
                'mor': [self._level_to_dict(level) for level in self.mor_levels],
                'org': [self._level_to_dict(level) for level in self.org_levels],
                'mop': [self._level_to_dict(level) for level in self.mop_levels],
                'first_pres': [self._level_to_dict(level) for level in self.first_pres]
            },
            
            # Draw on Liquidity (Patek's DOL concept)
            'draw_on_liquidity': {
                'weekly': [self._dol_to_dict(dol) for dol in self.weekly_dol],
                'daily': [self._dol_to_dict(dol) for dol in self.daily_dol],
                'intraday': [self._dol_to_dict(dol) for dol in self.intraday_dol]
            },
            
            # Summary
            'summary': {
                'total_key_levels': len(self.nwog_levels) + len(self.ndog_levels) + len(self.mor_levels) + len(self.org_levels) + len(self.mop_levels),
                'unfilled_gaps': len([g for g in self.nwog_levels + self.ndog_levels if not g.filled]),
                'high_probability_dol': len([d for d in self.daily_dol + self.weekly_dol if d.probability >= 70]),
                'nearest_dol': min(self.daily_dol + self.weekly_dol + self.intraday_dol, 
                                 key=lambda x: x.distance_pips, default=None)
            }
        }
    
    def _level_to_dict(self, level: KeyLevel) -> Dict:
        """Convert KeyLevel to dictionary"""
        return {
            'type': level.level_type,
            'timestamp': level.timestamp.isoformat(),
            'high': level.high,
            'low': level.low,
            'open_price': level.open_price,
            'close_price': level.close_price,
            'filled': level.filled,
            'strength': level.strength,
            'interaction_count': level.interaction_count
        }
    
    def _dol_to_dict(self, dol: DrawOnLiquidity) -> Dict:
        """Convert DrawOnLiquidity to dictionary"""
        return {
            'target_level': dol.target_level,
            'level_type': dol.level_type,
            'probability': dol.probability,
            'timeframe': dol.timeframe,
            'reasoning': dol.reasoning,
            'distance_pips': dol.distance_pips,
            'expected_reaction': dol.expected_reaction
        }
    
    def _setup_routes(self):
        """Setup Flask routes for web interface"""
        
        @self.app.route('/')
        def dashboard():
            analysis = self.get_current_analysis()
            
            dashboard_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Patek ICT Analysis Dashboard</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; background: #0a0e1a; color: #e2e8f0; margin: 0; padding: 20px; }
                    .container { max-width: 1400px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #1e293b; padding-bottom: 20px; }
                    .header h1 { color: #f1f5f9; font-size: 2.5em; margin: 0; }
                    .header p { color: #64748b; margin: 10px 0; }
                    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
                    .section { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
                    .section h2 { color: #f8fafc; margin: 0 0 15px 0; font-size: 1.3em; border-bottom: 1px solid #475569; padding-bottom: 10px; }
                    .level-item { background: #0f172a; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #3b82f6; }
                    .level-strong { border-left-color: #ef4444; }
                    .level-medium { border-left-color: #f59e0b; }
                    .level-weak { border-left-color: #6b7280; }
                    .dol-item { background: #0f172a; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #10b981; }
                    .high-prob { border-left-color: #10b981; }
                    .med-prob { border-left-color: #f59e0b; }
                    .low-prob { border-left-color: #ef4444; }
                    .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
                    .stat-box { background: #0f172a; padding: 15px; text-align: center; border-radius: 6px; }
                    .stat-box h3 { color: #94a3b8; margin: 0 0 8px 0; font-size: 0.9em; }
                    .stat-box p { color: #f1f5f9; font-size: 1.5em; font-weight: bold; margin: 0; }
                    .price { color: #10b981; font-weight: bold; }
                    .filled { opacity: 0.6; text-decoration: line-through; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏛️ PATEK ICT ANALYSIS</h1>
                        <p>Pure ICT Methodology - Key Levels & Draw on Liquidity</p>
                        <p><span class="price">${{ analysis.current_price }}</span> | Bias: {{ analysis.current_bias }}</p>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <h3>Total Key Levels</h3>
                            <p>{{ analysis.summary.total_key_levels }}</p>
                        </div>
                        <div class="stat-box">
                            <h3>Unfilled Gaps</h3>
                            <p>{{ analysis.summary.unfilled_gaps }}</p>
                        </div>
                        <div class="stat-box">
                            <h3>High Prob DOL</h3>
                            <p>{{ analysis.summary.high_probability_dol }}</p>
                        </div>
                        <div class="stat-box">
                            <h3>Nearest DOL</h3>
                            <p>{{ "%.1f"|format(analysis.summary.nearest_dol.distance_pips if analysis.summary.nearest_dol else 0) }}</p>
                        </div>
                    </div>
                    
                    <div class="grid">
                        <div class="section">
                            <h2>🎯 DRAW ON LIQUIDITY</h2>
                            <h3>Weekly Targets</h3>
                            {% for dol in analysis.draw_on_liquidity.weekly %}
                            <div class="dol-item {{ 'high-prob' if dol.probability >= 70 else 'med-prob' if dol.probability >= 50 else 'low-prob' }}">
                                <strong>{{ dol.level_type }}</strong> @ {{ "%.2f"|format(dol.target_level) }}<br>
                                <small>{{ dol.probability }}% | {{ dol.reasoning }}</small>
                            </div>
                            {% endfor %}
                            
                            <h3>Daily Targets</h3>
                            {% for dol in analysis.draw_on_liquidity.daily %}
                            <div class="dol-item {{ 'high-prob' if dol.probability >= 70 else 'med-prob' if dol.probability >= 50 else 'low-prob' }}">
                                <strong>{{ dol.level_type }}</strong> @ {{ "%.2f"|format(dol.target_level) }}<br>
                                <small>{{ dol.probability }}% | {{ dol.expected_reaction }}</small>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div class="section">
                            <h2>🔑 KEY LEVELS</h2>
                            <h3>NWOG (New Week Opening Gaps)</h3>
                            {% for level in analysis.key_levels.nwog %}
                            <div class="level-item level-{{ level.strength.lower() }} {{ 'filled' if level.filled }}">
                                {{ "%.2f"|format(level.high) }} - {{ "%.2f"|format(level.low) }}<br>
                                <small>{{ level.timestamp[:10] }} | {{ level.strength }}</small>
                            </div>
                            {% endfor %}
                            
                            <h3>NDOG (New Day Opening Gaps)</h3>
                            {% for level in analysis.key_levels.ndog %}
                            <div class="level-item level-{{ level.strength.lower() }} {{ 'filled' if level.filled }}">
                                {{ "%.2f"|format(level.high) }} - {{ "%.2f"|format(level.low) }}<br>
                                <small>{{ level.timestamp[:10] }} | {{ level.strength }}</small>
                            </div>
                            {% endfor %}
                            
                            <h3>MOP (Midnight Opening Prices)</h3>
                            {% for level in analysis.key_levels.mop[-3:] %}
                            <div class="level-item level-{{ level.strength.lower() }}">
                                {{ "%.2f"|format(level.open_price) }}<br>
                                <small>{{ level.timestamp[:16] }} | {{ level.interaction_count }} interactions</small>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            from jinja2 import Template
            from markupsafe import escape
            template = Template(dashboard_html, autoescape=True)
            return template.render(analysis=analysis)
        
        @self.app.route('/api/analysis')
        def api_analysis():
            return jsonify(self.get_current_analysis())
        
        @self.app.route('/api/update')
        def api_update():
            self.update_all_timeframes()
            return jsonify({'status': 'updated', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    import os
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize system
    patek_system = PatekICTSystem('NQ=F')
    
    # Update data
    print("🔄 Updating all timeframes...")
    patek_system.update_all_timeframes()
    
    # Start web interface
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Patek ICT System on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    
    patek_system.app.run(host='127.0.0.1', port=port, debug=False)
#!/usr/bin/env python3
"""
Ultimate ICT Trading System
Combines state-tracker + ssv6 + Patek methodology + AI enhancement
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json

logger = logging.getLogger(__name__)

@dataclass
class MarketState:
    timeframe: str
    state: str  # BULL_ERL_TO_IRL, BULL_IRL_TO_ERL, BEAR_ERL_TO_IRL, BEAR_IRL_TO_ERL
    trend: str  # Pro, Counter
    confidence: float
    timestamp: datetime

@dataclass
class StructureZone:
    zone_type: str  # FVG, OB, Liquidity
    direction: str  # BULL, BEAR
    top: float
    bottom: float
    timestamp: datetime
    active: bool
    strength: float
    interactions: int = 0

@dataclass
class TradingOpportunity:
    signal_type: str  # LONG, SHORT
    strength: str  # STRONG, WEAK, COUNTER
    entry_zone: StructureZone
    confluence_score: float
    timeframe_alignment: List[str]
    risk_reward: float
    probability: float
    reasoning: str

class UltimateICTSystem:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')
        
        # Multi-timeframe states (from state-tracker)
        self.market_states = {
            'M': MarketState('M', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now()),
            'W': MarketState('W', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now()),
            'D': MarketState('D', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now()),
            '4H': MarketState('4H', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now()),
            '1H': MarketState('1H', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now()),
            '15M': MarketState('15M', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now()),
            '5M': MarketState('5M', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now()),
            '1M': MarketState('1M', 'BULL_ERL_TO_IRL', 'Counter', 0.0, datetime.now())
        }
        
        # Structure zones (from ssv6)
        self.active_zones = []
        self.liquidity_levels = []
        
        # Patek ICT levels
        self.ict_levels = {
            'nwog': [],
            'ndog': [],
            'mor': [],
            'org': [],
            'mop': []
        }
        
        # Current opportunities
        self.opportunities = []
        
        # Market data
        self.current_price = 0.0
        self.symbol = 'NQ1!'
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
    
    def receive_state_data(self, data: Dict):
        """Receive multi-timeframe state data from state-tracker"""
        try:
            for tf in ['M', 'W', 'D', '4H', '1H', '15M', '5M', '1M']:
                if f'state_{tf}' in data:
                    state_str = data[f'state_{tf}']
                    trend = self._get_trend_from_state(state_str)
                    confidence = self._calculate_state_confidence(state_str, tf)
                    
                    self.market_states[tf] = MarketState(
                        timeframe=tf,
                        state=state_str,
                        trend=trend,
                        confidence=confidence,
                        timestamp=datetime.now(self.ny_tz)
                    )
            
            logger.info("✅ Multi-timeframe states updated")
            self._analyze_opportunities()
            return True
            
        except Exception as e:
            logger.error(f"State data processing error: {e}")
            return False
    
    def receive_structure_data(self, data: Dict):
        """Receive structure data from ssv6 (FVGs, OBs, Pivots)"""
        try:
            # Process FVGs
            if 'fvgs' in data:
                for fvg_data in data['fvgs']:
                    zone = StructureZone(
                        zone_type='FVG',
                        direction=fvg_data['direction'],
                        top=fvg_data['top'],
                        bottom=fvg_data['bottom'],
                        timestamp=datetime.fromisoformat(fvg_data['timestamp']),
                        active=fvg_data['active'],
                        strength=fvg_data.get('strength', 0.5)
                    )
                    self.active_zones.append(zone)
            
            # Process Order Blocks
            if 'order_blocks' in data:
                for ob_data in data['order_blocks']:
                    zone = StructureZone(
                        zone_type='OB',
                        direction=ob_data['direction'],
                        top=ob_data['top'],
                        bottom=ob_data['bottom'],
                        timestamp=datetime.fromisoformat(ob_data['timestamp']),
                        active=ob_data['active'],
                        strength=ob_data.get('strength', 0.7)
                    )
                    self.active_zones.append(zone)
            
            # Process Liquidity Levels
            if 'liquidity_levels' in data:
                for liq_data in data['liquidity_levels']:
                    zone = StructureZone(
                        zone_type='Liquidity',
                        direction=liq_data['direction'],
                        top=liq_data['price'] + 1,  # Small range around level
                        bottom=liq_data['price'] - 1,
                        timestamp=datetime.fromisoformat(liq_data['timestamp']),
                        active=True,
                        strength=liq_data.get('strength', 0.8)
                    )
                    self.liquidity_levels.append(zone)
            
            # Update current price
            if 'current_price' in data:
                self.current_price = float(data['current_price'])
            
            logger.info("✅ Structure data updated")
            self._analyze_opportunities()
            return True
            
        except Exception as e:
            logger.error(f"Structure data processing error: {e}")
            return False
    
    def receive_ict_levels(self, data: Dict):
        """Receive Patek ICT key levels"""
        try:
            for level_type in ['nwog', 'ndog', 'mor', 'org', 'mop']:
                if level_type in data:
                    self.ict_levels[level_type] = data[level_type]
            
            logger.info("✅ ICT levels updated")
            self._analyze_opportunities()
            return True
            
        except Exception as e:
            logger.error(f"ICT levels processing error: {e}")
            return False
    
    def _analyze_opportunities(self):
        """Core analysis engine - combines all data sources"""
        self.opportunities = []
        
        # Get timeframe alignments
        alignments = self._get_timeframe_alignments()
        
        # Analyze each active zone for opportunities
        for zone in self.active_zones:
            if not zone.active:
                continue
            
            # Check if price is near zone
            distance = self._calculate_zone_distance(zone)
            if distance > 50:  # Too far away
                continue
            
            # Calculate confluence
            confluence = self._calculate_confluence(zone, alignments)
            
            if confluence['score'] >= 0.6:  # Minimum confluence threshold
                opportunity = TradingOpportunity(
                    signal_type='LONG' if zone.direction == 'BULL' else 'SHORT',
                    strength=confluence['strength'],
                    entry_zone=zone,
                    confluence_score=confluence['score'],
                    timeframe_alignment=confluence['aligned_timeframes'],
                    risk_reward=self._calculate_risk_reward(zone),
                    probability=self._calculate_probability(confluence['score'], zone.strength),
                    reasoning=confluence['reasoning']
                )
                self.opportunities.append(opportunity)
        
        # Sort by confluence score
        self.opportunities.sort(key=lambda x: x.confluence_score, reverse=True)
        
        logger.info(f"🎯 Found {len(self.opportunities)} trading opportunities")
    
    def _get_timeframe_alignments(self) -> Dict:
        """Analyze timeframe alignments for confluence"""
        alignments = {
            'strong_bullish': [],
            'strong_bearish': [],
            'weak_bullish': [],
            'weak_bearish': [],
            'counter': []
        }
        
        # Check each timeframe pair (higher → lower)
        tf_pairs = [
            ('M', 'W'), ('W', 'D'), ('D', '4H'), ('4H', '1H'),
            ('1H', '15M'), ('15M', '5M'), ('5M', '1M')
        ]
        
        for higher_tf, lower_tf in tf_pairs:
            higher_state = self.market_states[higher_tf].state
            lower_state = self.market_states[lower_tf].state
            
            # Strong alignments
            if higher_state == 'BULL_IRL_TO_ERL' and lower_state == 'BULL_IRL_TO_ERL':
                alignments['strong_bullish'].append(f"{higher_tf}-{lower_tf}")
            elif higher_state == 'BEAR_IRL_TO_ERL' and lower_state == 'BEAR_IRL_TO_ERL':
                alignments['strong_bearish'].append(f"{higher_tf}-{lower_tf}")
            
            # Weak alignments
            elif higher_state == 'BULL_ERL_TO_IRL' and lower_state == 'BULL_IRL_TO_ERL':
                alignments['weak_bullish'].append(f"{higher_tf}-{lower_tf}")
            elif higher_state == 'BEAR_ERL_TO_IRL' and lower_state == 'BEAR_IRL_TO_ERL':
                alignments['weak_bearish'].append(f"{higher_tf}-{lower_tf}")
            
            # Counter trends
            elif (higher_state == 'BULL_ERL_TO_IRL' and lower_state == 'BULL_ERL_TO_IRL') or \
                 (higher_state == 'BEAR_ERL_TO_IRL' and lower_state == 'BEAR_ERL_TO_IRL'):
                alignments['counter'].append(f"{higher_tf}-{lower_tf}")
        
        return alignments
    
    def _calculate_confluence(self, zone: StructureZone, alignments: Dict) -> Dict:
        """Calculate confluence score for a zone"""
        score = 0.0
        reasoning = []
        aligned_timeframes = []
        
        # Base zone strength
        score += zone.strength * 0.3
        reasoning.append(f"{zone.zone_type} strength: {zone.strength:.2f}")
        
        # Flexible timeframe alignment scoring
        if zone.direction == 'BULL':
            strong_count = len(alignments['strong_bullish'])
            weak_count = len(alignments['weak_bullish'])
            counter_count = len(alignments['counter'])
            
            # STRONG: 2+ strong alignments OR 1 strong + 2 weak
            if strong_count >= 2 or (strong_count >= 1 and weak_count >= 2):
                score += 0.4
                reasoning.append(f"Strong bullish alignment ({strong_count}S + {weak_count}W pairs)")
                aligned_timeframes.extend(alignments['strong_bullish'] + alignments['weak_bullish'])
                strength = 'STRONG'
            
            # WEAK: 1 strong OR 2+ weak OR minimal counter-trend
            elif strong_count >= 1 or weak_count >= 2 or (weak_count >= 1 and counter_count <= 1):
                score += 0.2
                reasoning.append(f"Moderate bullish alignment ({strong_count}S + {weak_count}W)")
                aligned_timeframes.extend(alignments['strong_bullish'] + alignments['weak_bullish'])
                strength = 'WEAK'
            
            # COUNTER: Too many opposing timeframes
            else:
                score += 0.1  # Still some value if structure is strong
                reasoning.append(f"Counter-trend setup ({counter_count} opposing)")
                strength = 'COUNTER'
        
        else:  # BEAR
            strong_count = len(alignments['strong_bearish'])
            weak_count = len(alignments['weak_bearish'])
            counter_count = len(alignments['counter'])
            
            # STRONG: 2+ strong alignments OR 1 strong + 2 weak
            if strong_count >= 2 or (strong_count >= 1 and weak_count >= 2):
                score += 0.4
                reasoning.append(f"Strong bearish alignment ({strong_count}S + {weak_count}W pairs)")
                aligned_timeframes.extend(alignments['strong_bearish'] + alignments['weak_bearish'])
                strength = 'STRONG'
            
            # WEAK: 1 strong OR 2+ weak OR minimal counter-trend
            elif strong_count >= 1 or weak_count >= 2 or (weak_count >= 1 and counter_count <= 1):
                score += 0.2
                reasoning.append(f"Moderate bearish alignment ({strong_count}S + {weak_count}W)")
                aligned_timeframes.extend(alignments['strong_bearish'] + alignments['weak_bearish'])
                strength = 'WEAK'
            
            # COUNTER: Too many opposing timeframes
            else:
                score += 0.1  # Still some value if structure is strong
                reasoning.append(f"Counter-trend setup ({counter_count} opposing)")
                strength = 'COUNTER'
        
        # ICT level confluence
        ict_confluence = self._check_ict_confluence(zone)
        score += ict_confluence * 0.3
        if ict_confluence > 0:
            reasoning.append(f"ICT level confluence: {ict_confluence:.2f}")
        
        return {
            'score': min(score, 1.0),
            'strength': strength,
            'aligned_timeframes': aligned_timeframes,
            'reasoning': ' | '.join(reasoning)
        }
    
    def _check_ict_confluence(self, zone: StructureZone) -> float:
        """Check if zone aligns with ICT key levels"""
        confluence = 0.0
        zone_mid = (zone.top + zone.bottom) / 2
        
        # Check all ICT levels
        for level_type, levels in self.ict_levels.items():
            for level in levels:
                if isinstance(level, dict):
                    level_price = level.get('high', level.get('low', level.get('price', 0)))
                    if abs(zone_mid - level_price) < zone_mid * 0.005:  # Within 0.5%
                        confluence += 0.2
                        break
        
        return min(confluence, 1.0)
    
    def _calculate_zone_distance(self, zone: StructureZone) -> float:
        """Calculate distance from current price to zone"""
        if self.current_price == 0:
            return 999
        
        zone_mid = (zone.top + zone.bottom) / 2
        return abs(self.current_price - zone_mid)
    
    def _calculate_risk_reward(self, zone: StructureZone) -> float:
        """Calculate risk/reward ratio"""
        zone_size = zone.top - zone.bottom
        stop_distance = zone_size * 1.2  # Stop beyond zone
        target_distance = zone_size * 3   # 3:1 target
        
        return target_distance / stop_distance if stop_distance > 0 else 0
    
    def _calculate_probability(self, confluence_score: float, zone_strength: float) -> float:
        """Calculate success probability"""
        base_prob = 0.5
        confluence_boost = confluence_score * 0.3
        strength_boost = zone_strength * 0.2
        
        return min(base_prob + confluence_boost + strength_boost, 0.95)
    
    def _get_trend_from_state(self, state: str) -> str:
        """Extract trend direction from state"""
        if 'IRL_TO_ERL' in state:
            return 'Pro'
        else:
            return 'Counter'
    
    def _calculate_state_confidence(self, state: str, timeframe: str) -> float:
        """Calculate confidence in state based on timeframe"""
        base_confidence = 0.7
        
        # Higher timeframes get higher confidence
        tf_multipliers = {
            'M': 1.0, 'W': 0.95, 'D': 0.9, '4H': 0.85,
            '1H': 0.8, '15M': 0.75, '5M': 0.7, '1M': 0.65
        }
        
        return base_confidence * tf_multipliers.get(timeframe, 0.7)
    
    def get_analysis(self) -> Dict:
        """Get complete system analysis"""
        return {
            'timestamp': datetime.now(self.ny_tz).isoformat(),
            'symbol': self.symbol,
            'current_price': self.current_price,
            
            # Multi-timeframe states
            'market_states': {
                tf: {
                    'state': state.state,
                    'trend': state.trend,
                    'confidence': state.confidence
                } for tf, state in self.market_states.items()
            },
            
            # Active opportunities
            'opportunities': [
                {
                    'signal_type': opp.signal_type,
                    'strength': opp.strength,
                    'confluence_score': opp.confluence_score,
                    'probability': opp.probability,
                    'risk_reward': opp.risk_reward,
                    'entry_zone': {
                        'type': opp.entry_zone.zone_type,
                        'top': opp.entry_zone.top,
                        'bottom': opp.entry_zone.bottom,
                        'direction': opp.entry_zone.direction
                    },
                    'timeframe_alignment': opp.timeframe_alignment,
                    'reasoning': opp.reasoning
                } for opp in self.opportunities[:5]  # Top 5
            ],
            
            # Summary stats
            'summary': {
                'total_opportunities': len(self.opportunities),
                'strong_signals': len([o for o in self.opportunities if o.strength == 'STRONG']),
                'active_zones': len([z for z in self.active_zones if z.active]),
                'bullish_bias': len([s for s in self.market_states.values() if 'BULL' in s.state]),
                'bearish_bias': len([s for s in self.market_states.values() if 'BEAR' in s.state])
            }
        }
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            analysis = self.get_analysis()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ultimate ICT Trading System</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; background: #0a0e1a; color: #e2e8f0; margin: 0; padding: 20px; }
                    .container { max-width: 1600px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #1e293b; padding-bottom: 20px; }
                    .header h1 { color: #f1f5f9; font-size: 2.5em; margin: 0; }
                    .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }
                    .section { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
                    .section h2 { color: #f8fafc; margin: 0 0 15px 0; font-size: 1.3em; border-bottom: 1px solid #475569; padding-bottom: 10px; }
                    .opportunity { background: #0f172a; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #10b981; }
                    .strong { border-left-color: #10b981; }
                    .weak { border-left-color: #f59e0b; }
                    .counter { border-left-color: #ef4444; }
                    .state-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
                    .state-box { background: #0f172a; padding: 10px; text-align: center; border-radius: 4px; }
                    .bull { border-left: 3px solid #10b981; }
                    .bear { border-left: 3px solid #ef4444; }
                    .price { color: #10b981; font-weight: bold; font-size: 1.5em; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎯 ULTIMATE ICT TRADING SYSTEM</h1>
                        <p>Multi-Timeframe State Analysis + Structure Zones + ICT Levels + AI Enhancement</p>
                        <p><strong>{{ analysis.symbol }}</strong> - <span class="price">${{ "%.2f"|format(analysis.current_price) }}</span></p>
                    </div>
                    
                    <div class="grid">
                        <div class="section">
                            <h2>🚀 TOP OPPORTUNITIES</h2>
                            {% for opp in analysis.opportunities %}
                            <div class="opportunity {{ opp.strength.lower() }}">
                                <strong>{{ opp.signal_type }} - {{ opp.strength }}</strong><br>
                                <small>Confluence: {{ "%.0f"|format(opp.confluence_score * 100) }}% | 
                                Probability: {{ "%.0f"|format(opp.probability * 100) }}% | 
                                R:R {{ "%.1f"|format(opp.risk_reward) }}:1</small><br>
                                <small>{{ opp.entry_zone.type }} @ {{ "%.2f"|format(opp.entry_zone.top) }}-{{ "%.2f"|format(opp.entry_zone.bottom) }}</small><br>
                                <small>{{ opp.reasoning }}</small>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div class="section">
                            <h2>📊 MARKET STATES</h2>
                            <div class="state-grid">
                                {% for tf, state in analysis.market_states.items() %}
                                <div class="state-box {{ 'bull' if 'BULL' in state.state else 'bear' }}">
                                    <strong>{{ tf }}</strong><br>
                                    <small>{{ state.trend }}</small><br>
                                    <small>{{ "%.0f"|format(state.confidence * 100) }}%</small>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <div class="section">
                            <h2>📈 SYSTEM SUMMARY</h2>
                            <p><strong>Total Opportunities:</strong> {{ analysis.summary.total_opportunities }}</p>
                            <p><strong>Strong Signals:</strong> {{ analysis.summary.strong_signals }}</p>
                            <p><strong>Active Zones:</strong> {{ analysis.summary.active_zones }}</p>
                            <p><strong>Bullish Timeframes:</strong> {{ analysis.summary.bullish_bias }}/8</p>
                            <p><strong>Bearish Timeframes:</strong> {{ analysis.summary.bearish_bias }}/8</p>
                            
                            <h3>🔗 Data Feeds</h3>
                            <p><strong>State Tracker:</strong> /receive_states</p>
                            <p><strong>Structure Data:</strong> /receive_structure</p>
                            <p><strong>ICT Levels:</strong> /receive_ict</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            from jinja2 import Template
            template = Template(html)
            return template.render(analysis=analysis)
        
        @self.app.route('/receive_states', methods=['POST'])
        def receive_states():
            try:
                data = request.json
                success = self.receive_state_data(data)
                return jsonify({'status': 'success' if success else 'error'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/receive_structure', methods=['POST'])
        def receive_structure():
            try:
                data = request.json
                success = self.receive_structure_data(data)
                return jsonify({'status': 'success' if success else 'error'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/receive_ict', methods=['POST'])
        def receive_ict():
            try:
                data = request.json
                success = self.receive_ict_levels(data)
                return jsonify({'status': 'success' if success else 'error'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analysis')
        def api_analysis():
            return jsonify(self.get_analysis())

if __name__ == '__main__':
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    system = UltimateICTSystem()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Ultimate ICT System on port {port}")
    print(f"🎯 Dashboard: http://localhost:{port}")
    
    system.app.run(host='0.0.0.0', port=port, debug=False)
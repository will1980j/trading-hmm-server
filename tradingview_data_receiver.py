#!/usr/bin/env python3
"""
TradingView Data Receiver - Gets real CME data from TradingView
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json

logger = logging.getLogger(__name__)

class TradingViewDataReceiver:
    def __init__(self):
        self.ny_tz = pytz.timezone('America/New_York')
        
        # Real market data from TradingView
        self.current_data = {
            'symbol': 'NQ1!',
            'current_price': 0.0,
            'daily_data': [],
            'weekly_data': [],
            'h1_data': [],
            'last_update': None
        }
        
        # ICT Key Levels
        self.key_levels = {
            'nwog': [],  # New Week Opening Gaps
            'ndog': [],  # New Day Opening Gaps  
            'mor': [],   # Midnight Opening Ranges
            'org': [],   # Opening Range Gaps
            'mop': [],   # Midnight Opening Prices
        }
        
        # Draw on Liquidity targets
        self.dol_targets = []
        
        # Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
    
    def receive_tradingview_data(self, data: Dict):
        """Receive real-time data from TradingView Pine Script"""
        try:
            # Update current market data
            self.current_data['symbol'] = data.get('symbol', 'NQ1!')
            self.current_data['current_price'] = float(data.get('close', 0))
            self.current_data['last_update'] = datetime.now(self.ny_tz)
            
            # Store OHLCV data
            candle_data = {
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'open': float(data.get('open', 0)),
                'high': float(data.get('high', 0)),
                'low': float(data.get('low', 0)),
                'close': float(data.get('close', 0)),
                'volume': int(data.get('volume', 0))
            }
            
            # Add to appropriate timeframe
            timeframe = data.get('timeframe', '1D')
            if timeframe in ['1D', 'D']:
                self.current_data['daily_data'].append(candle_data)
                # Keep last 90 days
                if len(self.current_data['daily_data']) > 90:
                    self.current_data['daily_data'] = self.current_data['daily_data'][-90:]
            elif timeframe in ['1W', 'W']:
                self.current_data['weekly_data'].append(candle_data)
                # Keep last 52 weeks
                if len(self.current_data['weekly_data']) > 52:
                    self.current_data['weekly_data'] = self.current_data['weekly_data'][-52:]
            elif timeframe in ['1H', 'H']:
                self.current_data['h1_data'].append(candle_data)
                # Keep last 120 hours (5 days)
                if len(self.current_data['h1_data']) > 120:
                    self.current_data['h1_data'] = self.current_data['h1_data'][-120:]
            
            # Process ICT levels with real data
            self._update_ict_levels()
            
            logger.info(f"✅ Received TradingView data: {self.current_data['symbol']} @ {self.current_data['current_price']}")
            
            return True
            
        except Exception as e:
            logger.error(f"TradingView data processing error: {e}")
            return False
    
    def _update_ict_levels(self):
        """Update ICT key levels with real TradingView data"""
        
        # 1. NWOG - New Week Opening Gaps
        self._calculate_nwog()
        
        # 2. NDOG - New Day Opening Gaps  
        self._calculate_ndog()
        
        # 3. MOR - Midnight Opening Ranges
        self._calculate_mor()
        
        # 4. ORG - Opening Range Gaps
        self._calculate_org()
        
        # 5. MOP - Midnight Opening Prices
        self._calculate_mop()
        
        # 6. Calculate Draw on Liquidity
        self._calculate_dol_targets()
    
    def _calculate_nwog(self):
        """Calculate New Week Opening Gaps from real data"""
        if len(self.current_data['weekly_data']) < 2:
            return
        
        self.key_levels['nwog'] = []
        weekly_data = self.current_data['weekly_data']
        
        # Get last 5 weeks
        for i in range(max(0, len(weekly_data) - 5), len(weekly_data)):
            if i == 0:
                continue
                
            current_week = weekly_data[i]
            prev_week = weekly_data[i-1]
            
            # Gap between Friday close and Sunday open
            gap_size = abs(current_week['open'] - prev_week['close'])
            
            if gap_size > 0:
                self.key_levels['nwog'].append({
                    'type': 'NWOG',
                    'timestamp': current_week['timestamp'],
                    'high': max(current_week['open'], prev_week['close']),
                    'low': min(current_week['open'], prev_week['close']),
                    'gap_size': gap_size,
                    'filled': False,  # Would need to check against daily data
                    'strength': 'STRONG' if gap_size > prev_week['close'] * 0.01 else 'MEDIUM'
                })
    
    def _calculate_ndog(self):
        """Calculate New Day Opening Gaps from real data"""
        if len(self.current_data['daily_data']) < 2:
            return
        
        self.key_levels['ndog'] = []
        daily_data = self.current_data['daily_data']
        
        # Get last 5 days
        for i in range(max(0, len(daily_data) - 5), len(daily_data)):
            if i == 0:
                continue
                
            current_day = daily_data[i]
            prev_day = daily_data[i-1]
            
            # Gap between previous close and current open
            gap_size = abs(current_day['open'] - prev_day['close'])
            
            if gap_size > 0:
                self.key_levels['ndog'].append({
                    'type': 'NDOG',
                    'timestamp': current_day['timestamp'],
                    'high': max(current_day['open'], prev_day['close']),
                    'low': min(current_day['open'], prev_day['close']),
                    'gap_size': gap_size,
                    'filled': False,
                    'strength': self._get_nq_gap_strength(gap_size)
                })
    
    def _calculate_mor(self):
        """Calculate Midnight Opening Ranges from real data"""
        if len(self.current_data['h1_data']) < 24:
            return
        
        self.key_levels['mor'] = []
        # This would need hourly data with proper timestamps
        # For now, placeholder
        
    def _calculate_org(self):
        """Calculate Opening Range Gaps from real data"""
        if len(self.current_data['daily_data']) < 7:
            return
        
        self.key_levels['org'] = []
        # Current week ORGs - would need proper date filtering
        
    def _calculate_mop(self):
        """Calculate Midnight Opening Prices from real data"""
        if len(self.current_data['h1_data']) < 24:
            return
        
        self.key_levels['mop'] = []
        # Would need hourly data with midnight timestamps
    
    def _calculate_dol_targets(self):
        """Calculate Draw on Liquidity targets from real levels"""
        self.dol_targets = []
        current_price = self.current_data['current_price']
        
        if current_price == 0:
            return
        
        # Unfilled NWOG targets
        for nwog in self.key_levels['nwog']:
            if not nwog['filled']:
                gap_mid = (nwog['high'] + nwog['low']) / 2
                distance = abs(current_price - gap_mid)
                
                self.dol_targets.append({
                    'target_level': gap_mid,
                    'type': 'NWOG_Fill',
                    'probability': 85 if nwog['strength'] == 'STRONG' else 65,
                    'distance': distance,
                    'reasoning': f"Unfilled NWOG from {nwog['timestamp'][:10]}"
                })
        
        # Unfilled NDOG targets
        for ndog in self.key_levels['ndog']:
            if not ndog['filled']:
                gap_mid = (ndog['high'] + ndog['low']) / 2
                distance = abs(current_price - gap_mid)
                
                probability = self._get_gap_fill_probability(ndog['gap_size'])
                
                self.dol_targets.append({
                    'target_level': gap_mid,
                    'type': 'NDOG_Fill',
                    'probability': probability,
                    'distance': distance,
                    'reasoning': f"Unfilled NDOG from {ndog['timestamp'][:10]}"
                })
    
    def _get_nq_gap_strength(self, gap_size: float) -> str:
        """Get NQ gap strength per Patek's rules"""
        if 20 <= gap_size <= 75:
            return "MEDIUM"  # Usually fills to 50%
        elif 75 <= gap_size <= 120:
            return "STRONG"  # Sweet spot
        elif gap_size >= 120:
            return "VERY_STRONG"  # May not fill
        else:
            return "WEAK"
    
    def _get_gap_fill_probability(self, gap_size: float) -> float:
        """Get gap fill probability per Patek's NQ rules"""
        if 20 <= gap_size <= 75:
            return 85.0
        elif 75 <= gap_size <= 120:
            return 65.0
        elif gap_size >= 120:
            return 35.0
        else:
            return 50.0
    
    def get_analysis(self) -> Dict:
        """Get current ICT analysis from real TradingView data"""
        return {
            'timestamp': datetime.now(self.ny_tz).isoformat(),
            'symbol': self.current_data['symbol'],
            'current_price': self.current_data['current_price'],
            'last_update': self.current_data['last_update'].isoformat() if self.current_data['last_update'] else None,
            'data_source': 'TradingView CME Feed',
            'key_levels': self.key_levels,
            'dol_targets': sorted(self.dol_targets, key=lambda x: x['distance'])[:10],  # Nearest 10
            'summary': {
                'total_levels': sum(len(levels) for levels in self.key_levels.values()),
                'unfilled_gaps': len([g for g in self.key_levels['nwog'] + self.key_levels['ndog'] if not g.get('filled', True)]),
                'high_prob_dol': len([d for d in self.dol_targets if d['probability'] >= 70]),
                'data_points': len(self.current_data['daily_data'])
            }
        }
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            analysis = self.get_analysis()
            
            html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>TradingView ICT Analysis</title>
                <style>
                    body {{ font-family: 'Segoe UI', sans-serif; background: #0a0e1a; color: #e2e8f0; margin: 0; padding: 20px; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ text-align: center; margin-bottom: 30px; border-bottom: 2px solid #1e293b; padding-bottom: 20px; }}
                    .header h1 {{ color: #f1f5f9; font-size: 2.2em; margin: 0; }}
                    .status {{ background: #1e293b; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                    .price {{ color: #10b981; font-weight: bold; font-size: 1.5em; }}
                    .section {{ background: #1e293b; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .level-item {{ background: #0f172a; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #3b82f6; }}
                    .dol-item {{ background: #0f172a; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #10b981; }}
                    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 TRADINGVIEW ICT ANALYSIS</h1>
                        <p>Real CME Data Feed - Patek ICT Methodology</p>
                    </div>
                    
                    <div class="status">
                        <h2>{{ analysis.symbol }} - <span class="price">${{ "%.2f"|format(analysis.current_price) }}</span></h2>
                        <p>Data Source: {{ analysis.data_source }}</p>
                        <p>Last Update: {{ analysis.last_update or "Waiting for TradingView data..." }}</p>
                        <p>Data Points: {{ analysis.summary.data_points }} | Levels: {{ analysis.summary.total_levels }} | High Prob DOL: {{ analysis.summary.high_prob_dol }}</p>
                    </div>
                    
                    <div class="grid">
                        <div class="section">
                            <h2>🎯 DRAW ON LIQUIDITY</h2>
                            {% for dol in analysis.dol_targets[:5] %}
                            <div class="dol-item">
                                <strong>{{ dol.type }}</strong> @ {{ "%.2f"|format(dol.target_level) }}<br>
                                <small>{{ dol.probability }}% | Distance: {{ "%.1f"|format(dol.distance) }} | {{ dol.reasoning }}</small>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div class="section">
                            <h2>🔑 KEY LEVELS</h2>
                            <h3>NWOG (New Week Opening Gaps)</h3>
                            {% for level in analysis.key_levels.nwog %}
                            <div class="level-item">
                                {{ "%.2f"|format(level.high) }} - {{ "%.2f"|format(level.low) }}<br>
                                <small>{{ level.timestamp[:10] }} | {{ level.strength }} | Gap: {{ "%.1f"|format(level.gap_size) }}</small>
                            </div>
                            {% endfor %}
                            
                            <h3>NDOG (New Day Opening Gaps)</h3>
                            {% for level in analysis.key_levels.ndog %}
                            <div class="level-item">
                                {{ "%.2f"|format(level.high) }} - {{ "%.2f"|format(level.low) }}<br>
                                <small>{{ level.timestamp[:10] }} | {{ level.strength }} | Gap: {{ "%.1f"|format(level.gap_size) }}</small>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>📡 TradingView Integration</h2>
                        <p><strong>Webhook URL:</strong> <code>https://your-app.railway.app/tradingview_data</code></p>
                        <p><strong>Status:</strong> {{ "✅ Receiving Data" if analysis.current_price > 0 else "⏳ Waiting for Data" }}</p>
                        <p>Send OHLCV data from your TradingView Pine Script to get real-time ICT analysis.</p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            from jinja2 import Template
            template = Template(html)
            return template.render(analysis=analysis)
        
        @self.app.route('/tradingview_data', methods=['POST'])
        def receive_data():
            try:
                data = request.json
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                success = self.receive_tradingview_data(data)
                
                if success:
                    return jsonify({
                        'status': 'success',
                        'message': 'Data received and processed',
                        'current_price': self.current_data['current_price'],
                        'levels_updated': sum(len(levels) for levels in self.key_levels.values())
                    })
                else:
                    return jsonify({'error': 'Data processing failed'}), 500
                    
            except Exception as e:
                logger.error(f"Data reception error: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analysis')
        def api_analysis():
            return jsonify(self.get_analysis())

if __name__ == '__main__':
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize TradingView data receiver
    tv_receiver = TradingViewDataReceiver()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting TradingView ICT System on port {port}")
    print(f"📊 Dashboard: http://localhost:{port}")
    print(f"📡 Webhook: http://localhost:{port}/tradingview_data")
    print("📈 Configure TradingView Pine Script to send data to webhook URL")
    
    tv_receiver.app.run(host='0.0.0.0', port=port, debug=False)
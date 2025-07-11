#!/usr/bin/env python3
"""
Institutional Grade Intraday Trading System
Integrates ICT concepts with AI/ML for daily profit extraction
"""

import asyncio
import websockets
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass
import yfinance as yf
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time

from ict_signal_engine import ICTSignalEngine
from ai_learning_engine import AILearningEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    timestamp: datetime
    symbol: str
    signal_type: str  # LONG/SHORT
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    reason: str
    risk_reward: float
    position_size: float
    session: str
    macro_window: Optional[str] = None
    ict_levels: Optional[Dict] = None

@dataclass
class Trade:
    signal: TradingSignal
    entry_time: datetime
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: float = 0.0
    status: str = 'OPEN'  # OPEN, CLOSED, STOPPED
    max_favorable: float = 0.0
    max_adverse: float = 0.0
    duration_minutes: int = 0

class InstitutionalTradingSystem:
    def __init__(self, symbols: List[str] = ['ES=F', 'NQ=F']):
        self.symbols = symbols
        self.ict_engine = ICTSignalEngine()
        self.ai_engine = AILearningEngine()
        
        # Trading state
        self.active_trades = {}
        self.trade_history = []
        self.daily_pnl = 0.0
        self.max_daily_loss = -500.0  # Risk management
        self.max_daily_profit = 1000.0  # Profit target
        
        # Market data storage
        self.market_data = {symbol: pd.DataFrame() for symbol in symbols}
        self.last_update = {}
        
        # Performance tracking
        self.performance_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'avg_rr': 0.0,
            'daily_stats': []
        }
        
        # Risk management
        self.risk_manager = RiskManager()
        
        # Flask app for API
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
        
        # Data feed
        self.data_feed_active = False
        
    def start_system(self):
        """Start the complete trading system"""
        logger.info("🚀 Starting Institutional Trading System...")
        
        # Start data feed
        self._start_data_feed()
        
        # Start signal processing
        self._start_signal_processor()
        
        # Start trade management
        self._start_trade_manager()
        
        # Start AI learning
        self._start_ai_learning()
        
        # Start Flask API
        self._start_api_server()
        
        logger.info("✅ All systems operational")
    
    def _start_data_feed(self):
        """Start real-time data feed"""
        def data_feed_worker():
            self.data_feed_active = True
            while self.data_feed_active:
                try:
                    for symbol in self.symbols:
                        # Get latest data (in production, use real-time feed)
                        data = self._fetch_market_data(symbol)
                        if not data.empty:
                            self.market_data[symbol] = data
                            self.last_update[symbol] = datetime.now()
                    
                    time.sleep(60)  # Update every minute
                    
                except Exception as e:
                    logger.error(f"Data feed error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=data_feed_worker, daemon=True)
        thread.start()
        logger.info("📊 Data feed started")
    
    def _start_signal_processor(self):
        """Start signal processing engine"""
        def signal_processor():
            while True:
                try:
                    current_time = datetime.now(pytz.timezone('America/New_York'))
                    
                    # Only trade during market hours
                    if not self._is_market_hours(current_time):
                        time.sleep(300)  # Check every 5 minutes when closed
                        continue
                    
                    # Check daily limits
                    if self.daily_pnl <= self.max_daily_loss:
                        logger.warning("Daily loss limit reached. Stopping trading.")
                        time.sleep(3600)  # Wait 1 hour
                        continue
                    
                    if self.daily_pnl >= self.max_daily_profit:
                        logger.info("Daily profit target reached. Stopping trading.")
                        time.sleep(3600)  # Wait 1 hour
                        continue
                    
                    # Process signals for each symbol
                    for symbol in self.symbols:
                        if symbol in self.market_data and not self.market_data[symbol].empty:
                            self._process_symbol_signals(symbol)
                    
                    time.sleep(30)  # Process every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Signal processor error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=signal_processor, daemon=True)
        thread.start()
        logger.info("🎯 Signal processor started")
    
    def _start_trade_manager(self):
        """Start trade management system"""
        def trade_manager():
            while True:
                try:
                    self._manage_active_trades()
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.error(f"Trade manager error: {e}")
                    time.sleep(30)
        
        thread = threading.Thread(target=trade_manager, daemon=True)
        thread.start()
        logger.info("📈 Trade manager started")
    
    def _start_ai_learning(self):
        """Start AI learning system"""
        def ai_learner():
            while True:
                try:
                    # Learn from completed trades every hour
                    if len(self.trade_history) >= 10:
                        self._update_ai_models()
                    time.sleep(3600)  # Update every hour
                except Exception as e:
                    logger.error(f"AI learning error: {e}")
                    time.sleep(1800)  # Retry in 30 minutes
        
        thread = threading.Thread(target=ai_learner, daemon=True)
        thread.start()
        logger.info("🤖 AI learning system started")
    
    def _start_api_server(self):
        """Start Flask API server"""
        def run_server():
            self.app.run(host='0.0.0.0', port=5001, debug=False)
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        logger.info("🌐 API server started on port 5001")
    
    def _fetch_market_data(self, symbol: str, period: str = '1d', interval: str = '1m') -> pd.DataFrame:
        """Fetch market data (replace with real-time feed in production)"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if not data.empty:
                # Ensure we have the required columns
                data = data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
                data.columns = ['open', 'high', 'low', 'close', 'volume']
                data.index = pd.to_datetime(data.index)
                
            return data
            
        except Exception as e:
            logger.error(f"Data fetch error for {symbol}: {e}")
            return pd.DataFrame()
    
    def _process_symbol_signals(self, symbol: str):
        """Process signals for a specific symbol"""
        try:
            data = self.market_data[symbol]
            if len(data) < 50:  # Need sufficient data
                return
            
            # Get ICT analysis
            ict_analysis = self.ict_engine.update_market_data(data)
            
            if 'error' in ict_analysis:
                return
            
            # Generate signals
            signals = ict_analysis.get('signals', [])
            
            for signal_data in signals:
                # Create trading signal
                signal = self._create_trading_signal(symbol, signal_data, data.iloc[-1])
                
                if signal and self._validate_signal(signal):
                    # Get AI confidence
                    ai_analysis = self._get_ai_signal_analysis(signal, data)
                    
                    # Adjust confidence based on AI
                    signal.confidence = (signal.confidence + ai_analysis.get('combined_confidence', 0.5)) / 2
                    
                    # Execute if confidence is high enough
                    if signal.confidence >= 0.65:
                        self._execute_signal(signal)
            
        except Exception as e:
            logger.error(f"Signal processing error for {symbol}: {e}")
    
    def _create_trading_signal(self, symbol: str, signal_data: Dict, latest_candle: pd.Series) -> Optional[TradingSignal]:
        """Create a trading signal from ICT analysis"""
        try:
            # Calculate position size based on risk
            risk_amount = 100.0  # Risk $100 per trade
            stop_distance = abs(signal_data['entry'] - signal_data['stop_loss'])
            position_size = risk_amount / stop_distance if stop_distance > 0 else 0
            
            # Calculate risk-reward ratio
            profit_distance = abs(signal_data['take_profit'] - signal_data['entry'])
            risk_reward = profit_distance / stop_distance if stop_distance > 0 else 0
            
            return TradingSignal(
                timestamp=datetime.now(pytz.timezone('America/New_York')),
                symbol=symbol,
                signal_type=signal_data['type'],
                entry_price=signal_data['entry'],
                stop_loss=signal_data['stop_loss'],
                take_profit=signal_data['take_profit'],
                confidence=signal_data['confidence'],
                reason=signal_data['reason'],
                risk_reward=risk_reward,
                position_size=position_size,
                session=self.ict_engine.market_state['current_session'],
                macro_window=signal_data.get('macro'),
                ict_levels=signal_data.get('fvg_level') or signal_data.get('swept_level')
            )
            
        except Exception as e:
            logger.error(f"Signal creation error: {e}")
            return None
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validate signal before execution"""
        # Risk-reward check
        if signal.risk_reward < 1.5:
            return False
        
        # Position size check
        if signal.position_size <= 0 or signal.position_size > 1000:
            return False
        
        # Confidence check
        if signal.confidence < 0.5:
            return False
        
        # Check if we already have a position in this symbol
        if signal.symbol in self.active_trades:
            return False
        
        # Daily trade limit
        today_trades = len([t for t in self.trade_history if t.entry_time.date() == datetime.now().date()])
        if today_trades >= 10:  # Max 10 trades per day
            return False
        
        return True
    
    def _get_ai_signal_analysis(self, signal: TradingSignal, data: pd.DataFrame) -> Dict:
        """Get AI analysis of the signal"""
        try:
            # Prepare features for AI analysis
            latest_candle = data.iloc[-1]
            
            features = {
                'price_momentum_5': (latest_candle['close'] - data.iloc[-6]['close']) / data.iloc[-6]['close'] if len(data) > 6 else 0,
                'signal_confidence': signal.confidence,
                'risk_reward_planned': signal.risk_reward,
                'hour': signal.timestamp.hour,
                'is_london_session': 1 if 2 <= signal.timestamp.hour <= 11 else 0,
                'is_ny_session': 1 if 13 <= signal.timestamp.hour <= 21 else 0,
                'macro_active': 1 if signal.macro_window else 0,
                'volume_ratio': latest_candle['volume'] / data['volume'].tail(20).mean() if len(data) > 20 else 1.0
            }
            
            return self.ai_engine.predict_signal_quality(features)
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {'combined_confidence': 0.5}
    
    def _execute_signal(self, signal: TradingSignal):
        """Execute a trading signal"""
        try:
            # Create trade
            trade = Trade(
                signal=signal,
                entry_time=signal.timestamp,
                max_favorable=signal.entry_price,
                max_adverse=signal.entry_price
            )
            
            # Add to active trades
            self.active_trades[signal.symbol] = trade
            
            logger.info(f"🎯 SIGNAL EXECUTED: {signal.symbol} {signal.signal_type} @ {signal.entry_price:.2f} "
                       f"(Confidence: {signal.confidence:.2f}, R:R: {signal.risk_reward:.2f})")
            
            # Log to trade history for learning
            self.trade_history.append(trade)
            
        except Exception as e:
            logger.error(f"Signal execution error: {e}")
    
    def _manage_active_trades(self):
        """Manage active trades"""
        for symbol, trade in list(self.active_trades.items()):
            try:
                if symbol not in self.market_data or self.market_data[symbol].empty:
                    continue
                
                current_price = self.market_data[symbol].iloc[-1]['close']
                
                # Update MAE/MFE
                if trade.signal.signal_type == 'LONG':
                    trade.max_favorable = max(trade.max_favorable, current_price)
                    trade.max_adverse = min(trade.max_adverse, current_price)
                    
                    # Check exit conditions
                    if current_price <= trade.signal.stop_loss:
                        self._close_trade(trade, current_price, 'STOPPED')
                    elif current_price >= trade.signal.take_profit:
                        self._close_trade(trade, current_price, 'TARGET')
                        
                else:  # SHORT
                    trade.max_favorable = min(trade.max_favorable, current_price)
                    trade.max_adverse = max(trade.max_adverse, current_price)
                    
                    # Check exit conditions
                    if current_price >= trade.signal.stop_loss:
                        self._close_trade(trade, current_price, 'STOPPED')
                    elif current_price <= trade.signal.take_profit:
                        self._close_trade(trade, current_price, 'TARGET')
                
                # Time-based exit (max 4 hours)
                if (datetime.now() - trade.entry_time).total_seconds() > 14400:
                    self._close_trade(trade, current_price, 'TIME')
                    
            except Exception as e:
                logger.error(f"Trade management error for {symbol}: {e}")
    
    def _close_trade(self, trade: Trade, exit_price: float, reason: str):
        """Close a trade"""
        try:
            trade.exit_time = datetime.now()
            trade.exit_price = exit_price
            trade.status = 'CLOSED'
            trade.duration_minutes = int((trade.exit_time - trade.entry_time).total_seconds() / 60)
            
            # Calculate P&L
            if trade.signal.signal_type == 'LONG':
                trade.pnl = (exit_price - trade.signal.entry_price) * trade.signal.position_size
            else:
                trade.pnl = (trade.signal.entry_price - exit_price) * trade.signal.position_size
            
            # Update daily P&L
            self.daily_pnl += trade.pnl
            
            # Update performance stats
            self._update_performance_stats(trade)
            
            # Remove from active trades
            if trade.signal.symbol in self.active_trades:
                del self.active_trades[trade.signal.symbol]
            
            logger.info(f"💰 TRADE CLOSED: {trade.signal.symbol} {trade.signal.signal_type} "
                       f"P&L: ${trade.pnl:.2f} ({reason}) Duration: {trade.duration_minutes}min")
            
        except Exception as e:
            logger.error(f"Trade closing error: {e}")
    
    def _update_performance_stats(self, trade: Trade):
        """Update performance statistics"""
        self.performance_stats['total_trades'] += 1
        self.performance_stats['total_pnl'] += trade.pnl
        
        if trade.pnl > 0:
            self.performance_stats['winning_trades'] += 1
        else:
            self.performance_stats['losing_trades'] += 1
        
        # Calculate win rate
        if self.performance_stats['total_trades'] > 0:
            self.performance_stats['win_rate'] = (
                self.performance_stats['winning_trades'] / self.performance_stats['total_trades'] * 100
            )
        
        # Calculate average R:R
        completed_trades = [t for t in self.trade_history if t.status == 'CLOSED']
        if completed_trades:
            rr_ratios = []
            for t in completed_trades:
                if t.signal.signal_type == 'LONG':
                    actual_rr = (t.exit_price - t.signal.entry_price) / (t.signal.entry_price - t.signal.stop_loss)
                else:
                    actual_rr = (t.signal.entry_price - t.exit_price) / (t.signal.stop_loss - t.signal.entry_price)
                rr_ratios.append(actual_rr)
            
            self.performance_stats['avg_rr'] = np.mean(rr_ratios)
    
    def _update_ai_models(self):
        """Update AI models with recent trade data"""
        try:
            # Prepare training data from completed trades
            completed_trades = [t for t in self.trade_history if t.status == 'CLOSED']
            
            if len(completed_trades) < 10:
                return
            
            # Create features and targets
            training_data = []
            for trade in completed_trades[-100:]:  # Use last 100 trades
                symbol = trade.signal.symbol
                if symbol in self.market_data and not self.market_data[symbol].empty:
                    # Get market data at trade time
                    trade_data = self.market_data[symbol]
                    
                    # Prepare features
                    features = self.ai_engine.prepare_features(
                        trade_data, [trade.signal.__dict__], [trade.__dict__]
                    )
                    
                    if not features.empty:
                        training_data.append(features)
            
            if training_data:
                combined_data = pd.concat(training_data, ignore_index=True)
                result = self.ai_engine.train_models(combined_data)
                
                if result.get('status') == 'success':
                    logger.info(f"🤖 AI models updated with {len(combined_data)} samples")
                    
        except Exception as e:
            logger.error(f"AI model update error: {e}")
    
    def _is_market_hours(self, current_time: datetime) -> bool:
        """Check if market is open"""
        # Simplified - in production, use proper market calendar
        weekday = current_time.weekday()
        hour = current_time.hour
        
        # Monday-Friday, 9:30 AM - 4:00 PM EST
        return weekday < 5 and 9.5 <= hour < 16
    
    def _setup_routes(self):
        """Setup Flask API routes"""
        
        @self.app.route('/', methods=['GET'])
        def dashboard():
            return jsonify({
                'system_status': 'OPERATIONAL',
                'active_trades': len(self.active_trades),
                'daily_pnl': self.daily_pnl,
                'performance': self.performance_stats,
                'ai_status': 'TRAINED' if self.ai_engine.is_trained else 'LEARNING'
            })
        
        @self.app.route('/signals', methods=['GET'])
        def get_signals():
            signals = []
            for symbol in self.symbols:
                if symbol in self.market_data and not self.market_data[symbol].empty:
                    ict_analysis = self.ict_engine.update_market_data(self.market_data[symbol])
                    signals.extend(ict_analysis.get('signals', []))
            
            return jsonify({'signals': signals, 'count': len(signals)})
        
        @self.app.route('/trades', methods=['GET'])
        def get_trades():
            active = [
                {
                    'symbol': trade.signal.symbol,
                    'type': trade.signal.signal_type,
                    'entry_price': trade.signal.entry_price,
                    'current_pnl': trade.pnl,
                    'duration': int((datetime.now() - trade.entry_time).total_seconds() / 60)
                }
                for trade in self.active_trades.values()
            ]
            
            recent_closed = [
                {
                    'symbol': trade.signal.symbol,
                    'type': trade.signal.signal_type,
                    'pnl': trade.pnl,
                    'duration': trade.duration_minutes,
                    'exit_reason': trade.status
                }
                for trade in self.trade_history[-10:] if trade.status == 'CLOSED'
            ]
            
            return jsonify({
                'active_trades': active,
                'recent_closed': recent_closed,
                'daily_pnl': self.daily_pnl
            })
        
        @self.app.route('/performance', methods=['GET'])
        def get_performance():
            return jsonify(self.performance_stats)
        
        @self.app.route('/ai_status', methods=['GET'])
        def get_ai_status():
            return jsonify({
                'is_trained': self.ai_engine.is_trained,
                'model_performance': self.ai_engine.model_performance,
                'feature_importance': self.ai_engine.get_feature_importance(),
                'learning_history': self.ai_engine.learning_history[-5:]
            })

class RiskManager:
    """Risk management system"""
    
    def __init__(self):
        self.max_daily_loss = -500.0
        self.max_daily_profit = 1000.0
        self.max_position_size = 1000.0
        self.max_concurrent_trades = 3
    
    def validate_trade(self, signal: TradingSignal, current_pnl: float, active_trades: int) -> bool:
        """Validate if trade meets risk criteria"""
        # Daily P&L limits
        if current_pnl <= self.max_daily_loss:
            return False
        
        if current_pnl >= self.max_daily_profit:
            return False
        
        # Position size limit
        if signal.position_size > self.max_position_size:
            return False
        
        # Concurrent trades limit
        if active_trades >= self.max_concurrent_trades:
            return False
        
        return True

if __name__ == '__main__':
    # Initialize and start the trading system
    trading_system = InstitutionalTradingSystem(['ES=F', 'NQ=F'])
    trading_system.start_system()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)
            # Print daily summary every hour
            if datetime.now().minute == 0:
                logger.info(f"📊 Daily P&L: ${trading_system.daily_pnl:.2f} | "
                           f"Active Trades: {len(trading_system.active_trades)} | "
                           f"Win Rate: {trading_system.performance_stats['win_rate']:.1f}%")
    except KeyboardInterrupt:
        logger.info("🛑 Trading system shutdown")
        trading_system.data_feed_active = False
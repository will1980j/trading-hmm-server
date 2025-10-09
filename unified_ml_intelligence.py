"""
Unified ML Intelligence System
Centralized ML that learns from ALL your trading data and provides insights to ALL dashboards
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import json
import threading
import time

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, mean_absolute_error
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

class UnifiedMLIntelligence:
    """
    Central ML system that learns from ALL your data:
    - 300+ backtest trades
    - Live signals
    - Market context
    - Session patterns
    - News impact
    
    Provides predictions and insights to ALL dashboards
    """
    
    def __init__(self, db):
        self.db = db
        self.models = {}
        self.scalers = {}
        self.is_trained = False
        self.training_data_count = 0
        self.last_training = None
        self.auto_retrain_threshold = 50  # Retrain every 50 new trades
        
    def train_on_all_data(self) -> Dict:
        """Train ML models on ALL available trading data"""
        
        if not ML_AVAILABLE:
            return {'error': 'ML dependencies not available'}
        
        try:
            # Get ALL training data
            trades = self._get_all_trades()
            
            if len(trades) < 20:
                return {'error': f'Insufficient data: {len(trades)} trades (need 20+)'}
            
            logger.info(f"🎯 Training ML on {len(trades)} trades...")
            
            # Prepare features and targets
            X, y_mfe, y_success = self._prepare_training_data(trades)
            
            if len(X) < 20:
                return {'error': 'Insufficient valid training samples'}
            
            # Split data
            X_train, X_test, y_mfe_train, y_mfe_test, y_success_train, y_success_test = train_test_split(
                X, y_mfe, y_success, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scalers['main'] = StandardScaler()
            X_train_scaled = self.scalers['main'].fit_transform(X_train)
            X_test_scaled = self.scalers['main'].transform(X_test)
            
            # Train MFE predictor (regression)
            self.models['mfe_predictor'] = GradientBoostingRegressor(
                n_estimators=100, max_depth=5, random_state=42
            )
            self.models['mfe_predictor'].fit(X_train_scaled, y_mfe_train)
            
            # Train success classifier
            self.models['success_classifier'] = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42
            )
            self.models['success_classifier'].fit(X_train_scaled, y_success_train)
            
            # Evaluate
            mfe_pred = self.models['mfe_predictor'].predict(X_test_scaled)
            success_pred = self.models['success_classifier'].predict(X_test_scaled)
            
            mfe_mae = mean_absolute_error(y_mfe_test, mfe_pred)
            success_accuracy = accuracy_score(y_success_test, success_pred)
            
            self.is_trained = True
            self.training_data_count = len(trades)
            self.last_training = datetime.now()
            
            logger.info(f"✅ ML Training Complete: MAE={mfe_mae:.3f}R, Accuracy={success_accuracy*100:.1f}%")
            
            return {
                'status': 'success',
                'training_samples': len(trades),
                'mfe_mae': float(mfe_mae),
                'success_accuracy': float(success_accuracy * 100),
                'models_trained': list(self.models.keys()),
                'last_training': self.last_training.isoformat()
            }
            
        except Exception as e:
            logger.error(f"ML training error: {str(e)}")
            return {'error': str(e)}
    
    def predict_signal_quality(self, signal_data: Dict, market_context: Dict) -> Dict:
        """Predict signal quality using trained ML models"""
        
        # Auto-train on first signal or when needed
        if not self.is_trained:
            logger.info("🎯 First signal received - training ML on all historical data...")
            training_result = self.train_on_all_data()
            if 'error' in training_result:
                logger.warning(f"⚠️ ML training failed: {training_result['error']}")
                return {
                    'predicted_mfe': 0.0,
                    'success_probability': 0.0,
                    'confidence': 0.0,
                    'recommendation': 'ML not trained - insufficient data'
                }
            logger.info(f"✅ ML trained on first signal: {training_result['training_samples']} trades")
        elif self._should_retrain():
            logger.info("🔄 Auto-retraining ML models (24h or 50 trades threshold)...")
            training_result = self.train_on_all_data()
            if 'error' in training_result:
                logger.warning(f"⚠️ Auto-retrain failed: {training_result['error']}")
        
        try:
            # Extract features
            features = self._extract_features(signal_data, market_context)
            
            # Scale features
            features_scaled = self.scalers['main'].transform([features])
            
            # Predict MFE
            predicted_mfe = self.models['mfe_predictor'].predict(features_scaled)[0]
            
            # Predict success probability
            success_proba = self.models['success_classifier'].predict_proba(features_scaled)[0]
            success_probability = success_proba[1] if len(success_proba) > 1 else 0.5
            
            # Calculate confidence based on model agreement
            confidence = min(success_probability * 100, 95)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(predicted_mfe, success_probability)
            
            return {
                'predicted_mfe': float(predicted_mfe),
                'success_probability': float(success_probability * 100),
                'confidence': float(confidence),
                'recommendation': recommendation,
                'models_used': 2,
                'training_samples': self.training_data_count
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'predicted_mfe': 0.0,
                'success_probability': 0.0,
                'confidence': 0.0,
                'recommendation': f'Prediction error: {str(e)}'
            }
    
    def get_fundamental_insights(self) -> Dict:
        """Answer fundamental questions about your trading using ML"""
        
        try:
            trades = self._get_all_trades()
            
            if len(trades) < 10:
                return {'error': 'Insufficient data for insights'}
            
            df = pd.DataFrame(trades)
            
            insights = {
                'best_sessions': self._analyze_best_sessions(df),
                'best_signal_types': self._analyze_best_signals(df),
                'optimal_targets': self._analyze_optimal_targets(df),
                'news_impact': self._analyze_news_impact(df),
                'bias_performance': self._analyze_bias_performance(df),
                'breakeven_effectiveness': self._analyze_breakeven(df),
                'key_recommendations': []
            }
            
            # Generate key recommendations
            insights['key_recommendations'] = self._generate_key_recommendations(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Insights error: {str(e)}")
            return {'error': str(e)}
    
    def _get_all_trades(self) -> List[Dict]:
        """Get ALL trades from signal lab tables"""
        
        cursor = self.db.conn.cursor()
        
        # Get 1M trades
        cursor.execute("""
            SELECT date, time, bias, session, signal_type,
                   COALESCE(mfe_none, mfe, 0) as mfe,
                   COALESCE(be1_hit, false) as be1_hit,
                   COALESCE(be2_hit, false) as be2_hit,
                   COALESCE(mfe1, 0) as mfe1,
                   COALESCE(mfe2, 0) as mfe2,
                   news_proximity, news_event,
                   market_context, context_quality_score
            FROM signal_lab_trades
            WHERE COALESCE(mfe_none, mfe, 0) != 0
            ORDER BY date DESC, time DESC
        """)
        
        trades_1m = [dict(row) for row in cursor.fetchall()]
        
        # Get 15M trades
        cursor.execute("""
            SELECT date, time, bias, session, signal_type,
                   COALESCE(mfe_none, 0) as mfe,
                   COALESCE(be1_hit, false) as be1_hit,
                   COALESCE(be2_hit, false) as be2_hit,
                   COALESCE(mfe1, 0) as mfe1,
                   COALESCE(mfe2, 0) as mfe2,
                   news_proximity, news_event
            FROM signal_lab_15m_trades
            WHERE COALESCE(mfe_none, 0) != 0
            ORDER BY date DESC, time DESC
        """)
        
        trades_15m = [dict(row) for row in cursor.fetchall()]
        
        # Mark timeframe
        for trade in trades_1m:
            trade['timeframe'] = '1M'
        for trade in trades_15m:
            trade['timeframe'] = '15M'
        
        all_trades = trades_1m + trades_15m
        
        logger.info(f"📊 Loaded {len(trades_1m)} 1M trades + {len(trades_15m)} 15M trades = {len(all_trades)} total")
        
        return all_trades
    
    def _prepare_training_data(self, trades: List[Dict]):
        """Prepare features and targets for ML training"""
        
        X = []
        y_mfe = []
        y_success = []
        
        for trade in trades:
            try:
                # Extract features
                features = self._extract_features_from_trade(trade)
                
                # Target: MFE
                mfe = float(trade.get('mfe', 0))
                
                # Target: Success (1R+ = success)
                success = 1 if mfe >= 1.0 else 0
                
                X.append(features)
                y_mfe.append(mfe)
                y_success.append(success)
                
            except Exception as e:
                logger.warning(f"Skipping trade due to error: {str(e)}")
                continue
        
        return np.array(X), np.array(y_mfe), np.array(y_success)
    
    def _extract_features_from_trade(self, trade: Dict) -> List[float]:
        """Extract ML features from a trade"""
        
        features = []
        
        # Bias (0=Bearish, 1=Bullish)
        features.append(1.0 if trade.get('bias') == 'Bullish' else 0.0)
        
        # Session encoding
        session = trade.get('session', 'Unknown')
        features.append(1.0 if session == 'London' else 0.0)
        features.append(1.0 if session == 'NY AM' else 0.0)
        features.append(1.0 if session == 'NY PM' else 0.0)
        
        # Signal type encoding
        signal_type = trade.get('signal_type', '')
        features.append(1.0 if 'FVG' in signal_type else 0.0)
        features.append(1.0 if 'IFVG' in signal_type else 0.0)
        
        # News proximity
        news = trade.get('news_proximity', 'None')
        features.append(1.0 if news == 'High' else 0.0)
        features.append(1.0 if news == 'Medium' else 0.0)
        
        # Timeframe
        features.append(1.0 if trade.get('timeframe') == '1M' else 0.0)
        
        # Market context quality (if available)
        context_quality = trade.get('context_quality_score', 0.5)
        features.append(float(context_quality))
        
        return features
    
    def _extract_features(self, signal_data: Dict, market_context: Dict) -> List[float]:
        """Extract features from live signal"""
        
        features = []
        
        # Bias
        features.append(1.0 if signal_data.get('bias') == 'Bullish' else 0.0)
        
        # Session
        session = signal_data.get('session', 'Unknown')
        features.append(1.0 if session == 'London' else 0.0)
        features.append(1.0 if session == 'NY AM' else 0.0)
        features.append(1.0 if session == 'NY PM' else 0.0)
        
        # Signal type
        signal_type = signal_data.get('signal_type', '')
        features.append(1.0 if 'FVG' in signal_type else 0.0)
        features.append(1.0 if 'IFVG' in signal_type else 0.0)
        
        # News (default to None)
        features.append(0.0)  # High news
        features.append(0.0)  # Medium news
        
        # Timeframe (assume 1M for live signals)
        features.append(1.0)
        
        # Market context quality
        context_quality = market_context.get('context_quality_score', 0.5)
        features.append(float(context_quality))
        
        return features
    
    def _generate_recommendation(self, predicted_mfe: float, success_prob: float) -> str:
        """Generate trading recommendation"""
        
        if predicted_mfe >= 2.0 and success_prob >= 0.7:
            return "STRONG TAKE - High probability 2R+ setup"
        elif predicted_mfe >= 1.5 and success_prob >= 0.6:
            return "TAKE - Good probability setup"
        elif predicted_mfe >= 1.0 and success_prob >= 0.5:
            return "CONSIDER - Moderate probability"
        else:
            return "SKIP - Low probability setup"
    
    def _analyze_best_sessions(self, df: pd.DataFrame) -> Dict:
        """Find best trading sessions"""
        
        session_stats = df.groupby('session').agg({
            'mfe': ['count', 'mean', 'std']
        }).round(3)
        
        best_session = session_stats['mfe']['mean'].idxmax()
        
        return {
            'best_session': best_session,
            'avg_mfe': float(session_stats.loc[best_session, ('mfe', 'mean')]),
            'trade_count': int(session_stats.loc[best_session, ('mfe', 'count')]),
            'all_sessions': session_stats.to_dict()
        }
    
    def _analyze_best_signals(self, df: pd.DataFrame) -> Dict:
        """Find best signal types"""
        
        signal_stats = df.groupby('signal_type').agg({
            'mfe': ['count', 'mean']
        }).round(3)
        
        # Filter signals with at least 5 occurrences
        signal_stats = signal_stats[signal_stats[('mfe', 'count')] >= 5]
        
        if len(signal_stats) == 0:
            return {'error': 'No signal types with sufficient data'}
        
        best_signal = signal_stats['mfe']['mean'].idxmax()
        
        return {
            'best_signal_type': best_signal,
            'avg_mfe': float(signal_stats.loc[best_signal, ('mfe', 'mean')]),
            'trade_count': int(signal_stats.loc[best_signal, ('mfe', 'count')])
        }
    
    def _analyze_optimal_targets(self, df: pd.DataFrame) -> Dict:
        """Analyze optimal R targets"""
        
        # Calculate hit rates for different R targets
        targets = {}
        
        for r_target in [1.0, 1.5, 2.0, 2.5, 3.0]:
            hit_rate = (df['mfe'] >= r_target).mean() * 100
            avg_when_hit = df[df['mfe'] >= r_target]['mfe'].mean() if (df['mfe'] >= r_target).any() else 0
            
            targets[f'{r_target}R'] = {
                'hit_rate': float(hit_rate),
                'avg_when_hit': float(avg_when_hit)
            }
        
        return targets
    
    def _analyze_news_impact(self, df: pd.DataFrame) -> Dict:
        """Analyze news proximity impact"""
        
        if 'news_proximity' not in df.columns:
            return {'error': 'No news data'}
        
        news_stats = df.groupby('news_proximity').agg({
            'mfe': ['count', 'mean']
        }).round(3)
        
        return news_stats.to_dict()
    
    def _analyze_bias_performance(self, df: pd.DataFrame) -> Dict:
        """Analyze bias performance"""
        
        bias_stats = df.groupby('bias').agg({
            'mfe': ['count', 'mean']
        }).round(3)
        
        return {
            'bullish': {
                'count': int(bias_stats.loc['Bullish', ('mfe', 'count')]) if 'Bullish' in bias_stats.index else 0,
                'avg_mfe': float(bias_stats.loc['Bullish', ('mfe', 'mean')]) if 'Bullish' in bias_stats.index else 0
            },
            'bearish': {
                'count': int(bias_stats.loc['Bearish', ('mfe', 'count')]) if 'Bearish' in bias_stats.index else 0,
                'avg_mfe': float(bias_stats.loc['Bearish', ('mfe', 'mean')]) if 'Bearish' in bias_stats.index else 0
            }
        }
    
    def _analyze_breakeven(self, df: pd.DataFrame) -> Dict:
        """Analyze breakeven strategy effectiveness"""
        
        if 'be1_hit' not in df.columns:
            return {'error': 'No breakeven data'}
        
        be1_hit_rate = df['be1_hit'].mean() * 100
        be2_hit_rate = df['be2_hit'].mean() * 100 if 'be2_hit' in df.columns else 0
        
        return {
            'be1_hit_rate': float(be1_hit_rate),
            'be2_hit_rate': float(be2_hit_rate),
            'recommendation': 'Use BE1' if be1_hit_rate > 60 else 'Consider no BE'
        }
    
    def _should_retrain(self) -> bool:
        """Check if ML should retrain based on new data"""
        
        if not self.is_trained:
            return True
        
        # Retrain if last training was more than 24 hours ago
        if self.last_training:
            hours_since_training = (datetime.now() - self.last_training).total_seconds() / 3600
            if hours_since_training > 24:
                logger.info(f"⏰ Auto-retrain: {hours_since_training:.1f} hours since last training")
                return True
        
        # Retrain if we have significantly more data
        try:
            current_trades = self._get_all_trades()
            new_trades = len(current_trades) - self.training_data_count
            
            if new_trades >= self.auto_retrain_threshold:
                logger.info(f"📊 Auto-retrain: {new_trades} new trades since last training")
                return True
        except:
            pass
        
        return False
    
    def _generate_key_recommendations(self, insights: Dict) -> List[str]:
        """Generate key trading recommendations"""
        
        recommendations = []
        
        # Session recommendation
        if 'best_sessions' in insights and 'best_session' in insights['best_sessions']:
            best = insights['best_sessions']
            recommendations.append(
                f"✅ Trade during {best['best_session']} session (avg {best['avg_mfe']:.2f}R from {best['trade_count']} trades)"
            )
        
        # Signal type recommendation
        if 'best_signal_types' in insights and 'best_signal_type' in insights['best_signal_types']:
            best = insights['best_signal_types']
            recommendations.append(
                f"✅ Focus on {best['best_signal_type']} signals (avg {best['avg_mfe']:.2f}R)"
            )
        
        # Target recommendation
        if 'optimal_targets' in insights:
            targets = insights['optimal_targets']
            best_target = max(targets.items(), key=lambda x: x[1]['hit_rate'] * x[1].get('avg_when_hit', 0))
            recommendations.append(
                f"✅ Optimal target: {best_target[0]} ({best_target[1]['hit_rate']:.1f}% hit rate)"
            )
        
        # Bias recommendation
        if 'bias_performance' in insights:
            bias = insights['bias_performance']
            if bias['bullish']['avg_mfe'] > bias['bearish']['avg_mfe']:
                recommendations.append(
                    f"✅ Bullish bias performs better ({bias['bullish']['avg_mfe']:.2f}R vs {bias['bearish']['avg_mfe']:.2f}R)"
                )
            else:
                recommendations.append(
                    f"✅ Bearish bias performs better ({bias['bearish']['avg_mfe']:.2f}R vs {bias['bullish']['avg_mfe']:.2f}R)"
                )
        
        return recommendations

# Global instance
_unified_ml = None
_auto_trainer_thread = None

def get_unified_ml(db):
    """Get or create unified ML instance"""
    global _unified_ml, _auto_trainer_thread
    
    if _unified_ml is None:
        _unified_ml = UnifiedMLIntelligence(db)
        
        # Start auto-trainer thread
        if _auto_trainer_thread is None:
            _auto_trainer_thread = threading.Thread(
                target=_auto_trainer_loop,
                args=(_unified_ml,),
                daemon=True
            )
            _auto_trainer_thread.start()
            logger.info("🤖 Auto-trainer thread started")
    
    return _unified_ml

def _auto_trainer_loop(ml_instance):
    """Background thread that checks for retraining every hour"""
    while True:
        try:
            time.sleep(3600)  # Check every hour
            
            if ml_instance._should_retrain():
                logger.info("🔄 Auto-trainer: Retraining ML models...")
                result = ml_instance.train_on_all_data()
                
                if 'error' not in result:
                    logger.info(f"✅ Auto-trainer: Training complete - {result['training_samples']} samples, {result['success_accuracy']:.1f}% accuracy")
                else:
                    logger.error(f"❌ Auto-trainer: Training failed - {result['error']}")
        except Exception as e:
            logger.error(f"❌ Auto-trainer error: {str(e)}")
            time.sleep(3600)  # Wait an hour before retrying

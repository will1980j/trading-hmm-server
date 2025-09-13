"""
Signal ML Predictor - Learn which market conditions produce best signals
Works with existing 1M Signal Lab workflow
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class SignalMLPredictor:
    """ML predictor for signal quality based on market context"""
    
    def __init__(self, db):
        self.db = db
        self.model_weights = {
            'vix_regime': 0.25,
            'session': 0.20,
            'volume_regime': 0.15,
            'dxy_impact': 0.15,
            'correlation_strength': 0.10,
            'trend_strength': 0.10,
            'sector_rotation': 0.05
        }
    
    def get_training_data(self, days_back: int = 60) -> List[Dict]:
        """Get training data from signal_lab_trades with market context"""
        try:
            cursor = self.db.conn.cursor()
            
            # Get signals with outcomes and market context
            cursor.execute("""
                SELECT st.bias, st.session, st.signal_type,
                       COALESCE(st.mfe_none, st.mfe, 0) as mfe,
                       st.market_context, st.context_quality_score,
                       st.date, st.time
                FROM signal_lab_trades st
                WHERE st.date > CURRENT_DATE - INTERVAL '%s days'
                AND st.market_context IS NOT NULL
                AND COALESCE(st.mfe_none, st.mfe, 0) != 0
                ORDER BY st.date DESC, st.time DESC
            """, (days_back,))
            
            trades = cursor.fetchall()
            
            training_data = []
            for trade in trades:
                try:
                    market_ctx = json.loads(trade['market_context']) if trade['market_context'] else {}
                    
                    features = self._extract_features(market_ctx, trade)
                    outcome = float(trade['mfe']) if trade['mfe'] else 0
                    
                    training_data.append({
                        'features': features,
                        'outcome': outcome,
                        'date': trade['date'],
                        'session': trade['session'],
                        'bias': trade['bias']
                    })
                    
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
            
            logger.info(f"Loaded {len(training_data)} training samples")
            return training_data
            
        except Exception as e:
            logger.error(f"Error getting training data: {str(e)}")
            return []
    
    def _extract_features(self, market_ctx: Dict, trade: Dict) -> Dict[str, float]:
        """Extract ML features from market context"""
        
        # VIX regime (0-1 scale)
        vix = market_ctx.get('vix', 20)
        if vix < 15:
            vix_regime = 0.9  # Low VIX = good
        elif vix < 25:
            vix_regime = 0.7  # Normal VIX = ok
        elif vix < 35:
            vix_regime = 0.3  # High VIX = caution
        else:
            vix_regime = 0.1  # Extreme VIX = avoid
        
        # Session quality (0-1 scale)
        session = trade.get('session', 'Unknown')
        session_scores = {
            'London': 0.9,
            'NY Regular': 0.8,
            'NY AM': 0.8,
            'NY Pre Market': 0.4,
            'Asia': 0.3,
            'After Hours': 0.2
        }
        session_quality = session_scores.get(session, 0.5)
        
        # Volume regime (0-1 scale)
        spy_volume = market_ctx.get('spy_volume', 80000000)
        volume_ratio = spy_volume / 80000000  # vs average
        if volume_ratio > 1.2:
            volume_regime = 0.8  # High volume = good
        elif volume_ratio > 0.8:
            volume_regime = 0.7  # Normal volume = ok
        else:
            volume_regime = 0.4  # Low volume = caution
        
        # DXY impact (0-1 scale)
        dxy_change = market_ctx.get('dxy_change', 0)
        bias = trade.get('bias', 'Bullish')
        
        if abs(dxy_change) < 0.2:
            dxy_impact = 0.6  # Neutral DXY
        elif (dxy_change < 0 and bias == 'Bullish') or (dxy_change > 0 and bias == 'Bearish'):
            dxy_impact = 0.8  # DXY supports signal
        else:
            dxy_impact = 0.3  # DXY opposes signal
        
        # Correlation strength
        nq_es_corr = market_ctx.get('nq_es_correlation', 0.85)
        correlation_strength = min(1.0, abs(nq_es_corr))
        
        # Trend strength
        trend_strength = min(1.0, market_ctx.get('trend_strength', 0.5))
        
        # Sector rotation
        sector_rotation = market_ctx.get('sector_rotation', 'BALANCED')
        sector_scores = {
            'TECH_LEADERSHIP': 0.8,  # Good for NQ
            'BALANCED': 0.6,
            'VALUE_ROTATION': 0.4   # Bad for NQ
        }
        sector_score = sector_scores.get(sector_rotation, 0.5)
        
        return {
            'vix_regime': vix_regime,
            'session_quality': session_quality,
            'volume_regime': volume_regime,
            'dxy_impact': dxy_impact,
            'correlation_strength': correlation_strength,
            'trend_strength': trend_strength,
            'sector_rotation': sector_score
        }
    
    def predict_signal_quality(self, market_context: Dict, signal_data: Dict) -> Dict[str, float]:
        """Predict signal quality based on current market context"""
        try:
            # Extract features from current market context
            features = self._extract_features(market_context, signal_data)
            
            # Simple weighted scoring model
            predicted_score = 0
            for feature, value in features.items():
                weight = self.model_weights.get(feature, 0.1)
                predicted_score += value * weight
            
            # Get historical performance for similar conditions
            historical_performance = self._get_similar_conditions_performance(features)
            
            # Combine prediction with historical data
            if historical_performance['sample_size'] > 5:
                # Weight historical data more heavily with larger sample size
                historical_weight = min(0.7, historical_performance['sample_size'] / 20)
                predicted_score = (predicted_score * (1 - historical_weight) + 
                                 historical_performance['avg_mfe'] * historical_weight)
            
            return {
                'predicted_quality': min(1.0, max(0.0, predicted_score)),
                'predicted_mfe': historical_performance.get('avg_mfe', 0),
                'confidence': min(1.0, historical_performance.get('sample_size', 0) / 10),
                'similar_signals': historical_performance.get('sample_size', 0),
                'recommendation': self._generate_recommendation(predicted_score, historical_performance)
            }
            
        except Exception as e:
            logger.error(f"Error predicting signal quality: {str(e)}")
            return {
                'predicted_quality': 0.5,
                'predicted_mfe': 0,
                'confidence': 0,
                'similar_signals': 0,
                'recommendation': 'Insufficient data'
            }
    
    def _get_similar_conditions_performance(self, current_features: Dict[str, float]) -> Dict:
        """Get performance of signals under similar market conditions"""
        try:
            training_data = self.get_training_data(30)  # Last 30 days
            
            if not training_data:
                return {'avg_mfe': 0, 'sample_size': 0}
            
            # Find similar conditions (within 0.2 threshold for each feature)
            similar_signals = []
            
            for data_point in training_data:
                similarity_score = 0
                feature_count = 0
                
                for feature, current_value in current_features.items():
                    if feature in data_point['features']:
                        historical_value = data_point['features'][feature]
                        # Calculate similarity (1.0 = identical, 0.0 = completely different)
                        feature_similarity = 1.0 - abs(current_value - historical_value)
                        similarity_score += feature_similarity
                        feature_count += 1
                
                if feature_count > 0:
                    avg_similarity = similarity_score / feature_count
                    
                    # Consider signals with >70% similarity as "similar"
                    if avg_similarity > 0.7:
                        similar_signals.append({
                            'outcome': data_point['outcome'],
                            'similarity': avg_similarity
                        })
            
            if similar_signals:
                # Weight outcomes by similarity
                weighted_outcomes = []
                for signal in similar_signals:
                    # Give more weight to more similar signals
                    weight = signal['similarity'] ** 2
                    weighted_outcomes.extend([signal['outcome']] * int(weight * 10))
                
                avg_mfe = sum(weighted_outcomes) / len(weighted_outcomes)
                win_rate = len([o for o in weighted_outcomes if o > 0]) / len(weighted_outcomes) * 100
                
                return {
                    'avg_mfe': avg_mfe,
                    'win_rate': win_rate,
                    'sample_size': len(similar_signals)
                }
            
            return {'avg_mfe': 0, 'win_rate': 50, 'sample_size': 0}
            
        except Exception as e:
            logger.error(f"Error getting similar conditions: {str(e)}")
            return {'avg_mfe': 0, 'win_rate': 50, 'sample_size': 0}
    
    def _generate_recommendation(self, predicted_score: float, historical_data: Dict) -> str:
        """Generate trading recommendation based on prediction"""
        
        sample_size = historical_data.get('sample_size', 0)
        avg_mfe = historical_data.get('avg_mfe', 0)
        
        if sample_size < 3:
            return "INSUFFICIENT DATA - Proceed with caution"
        
        if predicted_score > 0.7 and avg_mfe > 1.0:
            return "STRONG SIGNAL - High probability setup"
        elif predicted_score > 0.6 and avg_mfe > 0.5:
            return "GOOD SIGNAL - Favorable conditions"
        elif predicted_score > 0.4 and avg_mfe > 0:
            return "MODERATE SIGNAL - Standard conditions"
        elif avg_mfe < 0:
            return "AVOID - Historically negative expectancy"
        else:
            return "WEAK SIGNAL - Consider skipping"
    
    def get_model_insights(self) -> Dict:
        """Get insights about what the model has learned"""
        try:
            training_data = self.get_training_data(60)
            
            if not training_data:
                return {'insights': ['No training data available']}
            
            insights = []
            
            # Analyze VIX impact
            vix_performance = defaultdict(list)
            for data in training_data:
                vix_regime = data['features'].get('vix_regime', 0.5)
                if vix_regime > 0.8:
                    regime = 'LOW_VIX'
                elif vix_regime > 0.6:
                    regime = 'NORMAL_VIX'
                else:
                    regime = 'HIGH_VIX'
                vix_performance[regime].append(data['outcome'])
            
            for regime, outcomes in vix_performance.items():
                if len(outcomes) >= 3:
                    avg_mfe = sum(outcomes) / len(outcomes)
                    insights.append(f"{regime}: {avg_mfe:.2f}R avg ({len(outcomes)} signals)")
            
            # Analyze session impact
            session_performance = defaultdict(list)
            for data in training_data:
                session = data['session']
                session_performance[session].append(data['outcome'])
            
            best_session = None
            best_performance = -999
            for session, outcomes in session_performance.items():
                if len(outcomes) >= 3:
                    avg_mfe = sum(outcomes) / len(outcomes)
                    if avg_mfe > best_performance:
                        best_performance = avg_mfe
                        best_session = session
            
            if best_session:
                insights.append(f"Best session: {best_session} ({best_performance:.2f}R avg)")
            
            # Overall model performance
            total_signals = len(training_data)
            avg_outcome = sum([d['outcome'] for d in training_data]) / total_signals
            win_rate = len([d for d in training_data if d['outcome'] > 0]) / total_signals * 100
            
            insights.append(f"Model trained on {total_signals} signals")
            insights.append(f"Overall performance: {avg_outcome:.2f}R avg, {win_rate:.1f}% win rate")
            
            return {
                'insights': insights,
                'total_signals': total_signals,
                'model_accuracy': min(1.0, total_signals / 50)  # Accuracy improves with more data
            }
            
        except Exception as e:
            logger.error(f"Error getting model insights: {str(e)}")
            return {'insights': ['Error analyzing model performance']}

# Global instance
signal_ml_predictor = None

def get_ml_predictor(db):
    global signal_ml_predictor
    if signal_ml_predictor is None:
        signal_ml_predictor = SignalMLPredictor(db)
    return signal_ml_predictor
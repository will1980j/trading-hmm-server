import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier, IsolationForest
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.cluster import DBSCAN
import xgboost as xgb
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedMLEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_accuracy = {}
        self.last_training = None
        
        # Advanced ML Models
        self.success_predictor = None  # Predicts if signal will hit 2R+
        self.mfe_predictor = None      # Predicts maximum favorable excursion
        self.session_optimizer = None   # Optimizes by session context
        self.anomaly_detector = None   # Detects unusual market conditions
        self.pattern_classifier = None # Classifies signal patterns
        
        # Feature engineering components
        self.price_scaler = StandardScaler()
        self.session_encoder = LabelEncoder()
        self.signal_encoder = LabelEncoder()
        
    def extract_comprehensive_features(self, signal_data: Dict) -> Dict:
        """Extract 50+ features from signal and market context"""
        try:
            cursor = self.db.conn.cursor()
            
            # Get historical context (last 100 signals)
            cursor.execute("""
                SELECT date, time, bias, session, signal_type, entry_price, 
                       COALESCE(mfe_none, 0) as mfe, 
                       COALESCE(be1_hit, false) as be1_hit,
                       COALESCE(be2_hit, false) as be2_hit,
                       created_at
                FROM signal_lab_trades 
                ORDER BY created_at DESC 
                LIMIT 100
            """)
            
            historical_data = cursor.fetchall()
            
            if len(historical_data) < 10:
                return self._basic_features(signal_data)
            
            # Convert to DataFrame for advanced analysis
            df = pd.DataFrame(historical_data)
            df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'].astype(str))
            df['mfe'] = pd.to_numeric(df['mfe'], errors='coerce').fillna(0)
            df['entry_price'] = pd.to_numeric(df['entry_price'], errors='coerce').fillna(0)
            
            features = {}
            
            # === TEMPORAL FEATURES ===
            current_time = datetime.now()
            features['hour'] = current_time.hour
            features['minute'] = current_time.minute
            features['day_of_week'] = current_time.weekday()
            features['is_london_session'] = 1 if 2 <= current_time.hour <= 7 else 0
            features['is_ny_session'] = 1 if 9 <= current_time.hour <= 16 else 0
            features['is_overlap'] = 1 if 8 <= current_time.hour <= 9 else 0
            
            # === PRICE ACTION FEATURES ===
            recent_prices = df['entry_price'].tail(20).values
            if len(recent_prices) > 5:
                features['price_momentum'] = np.mean(np.diff(recent_prices))
                features['price_volatility'] = np.std(recent_prices)
                features['price_trend'] = (recent_prices[-1] - recent_prices[0]) / recent_prices[0]
                features['price_acceleration'] = np.mean(np.diff(np.diff(recent_prices)))
                
                # Support/Resistance levels
                features['near_resistance'] = self._calculate_resistance_proximity(signal_data.get('price', 0), recent_prices)
                features['near_support'] = self._calculate_support_proximity(signal_data.get('price', 0), recent_prices)
            
            # === SIGNAL SEQUENCE FEATURES ===
            recent_signals = df.tail(10)
            if len(recent_signals) > 3:
                features['consecutive_same_bias'] = self._count_consecutive_bias(recent_signals, signal_data.get('bias'))
                features['bias_change_frequency'] = self._calculate_bias_changes(recent_signals)
                features['signal_density'] = len(recent_signals) / max(1, (recent_signals['datetime'].max() - recent_signals['datetime'].min()).total_seconds() / 3600)
                
                # Pattern recognition
                features['reversal_pattern'] = self._detect_reversal_pattern(recent_signals, signal_data.get('bias'))
                features['continuation_pattern'] = self._detect_continuation_pattern(recent_signals, signal_data.get('bias'))
            
            # === SESSION-SPECIFIC FEATURES ===
            session = signal_data.get('session', 'Unknown')
            session_data = df[df['session'] == session]
            if len(session_data) > 5:
                features['session_success_rate'] = (session_data['mfe'] > 2).mean()
                features['session_avg_mfe'] = session_data['mfe'].mean()
                features['session_volatility'] = session_data['mfe'].std()
                features['session_trade_count'] = len(session_data)
                
                # Session-specific bias performance
                bias_session_data = session_data[session_data['bias'] == signal_data.get('bias')]
                if len(bias_session_data) > 2:
                    features['session_bias_success'] = (bias_session_data['mfe'] > 2).mean()
                    features['session_bias_avg_mfe'] = bias_session_data['mfe'].mean()
            
            # === SIGNAL TYPE FEATURES ===
            signal_type = signal_data.get('signal_type', 'UNKNOWN')
            type_data = df[df['signal_type'] == signal_type]
            if len(type_data) > 3:
                features['signal_type_success'] = (type_data['mfe'] > 2).mean()
                features['signal_type_avg_mfe'] = type_data['mfe'].mean()
                features['signal_type_consistency'] = 1 - type_data['mfe'].std() / max(0.1, type_data['mfe'].mean())
            
            # === MARKET MICROSTRUCTURE FEATURES ===
            features['recent_win_rate'] = (df.tail(20)['mfe'] > 0).mean()
            features['recent_big_win_rate'] = (df.tail(20)['mfe'] > 2).mean()
            features['recent_avg_mfe'] = df.tail(20)['mfe'].mean()
            features['recent_max_mfe'] = df.tail(20)['mfe'].max()
            features['recent_drawdown'] = self._calculate_recent_drawdown(df.tail(20))
            
            # === BREAKEVEN ANALYSIS FEATURES ===
            features['be1_hit_rate'] = df['be1_hit'].mean()
            features['be2_hit_rate'] = df['be2_hit'].mean()
            features['be_efficiency'] = self._calculate_be_efficiency(df)
            
            # === ADVANCED STATISTICAL FEATURES ===
            mfe_series = df['mfe'].values
            if len(mfe_series) > 10:
                features['mfe_skewness'] = pd.Series(mfe_series).skew()
                features['mfe_kurtosis'] = pd.Series(mfe_series).kurtosis()
                features['mfe_autocorr'] = pd.Series(mfe_series).autocorr(lag=1)
                
                # Regime detection
                features['high_volatility_regime'] = 1 if np.std(mfe_series[-10:]) > np.std(mfe_series) * 1.5 else 0
                features['trending_regime'] = 1 if abs(np.mean(np.diff(mfe_series[-10:]))) > np.std(np.diff(mfe_series)) else 0
            
            # === HTF ALIGNMENT FEATURES ===
            htf_status = signal_data.get('htf_status', '')
            features['htf_timeframes_aligned'] = len([x for x in htf_status.split() if 'Bullish' in x or 'Bearish' in x])
            features['htf_strength'] = signal_data.get('strength', 50) / 100.0
            features['htf_aligned'] = 1 if signal_data.get('htf_aligned', False) else 0
            
            # === CLUSTERING FEATURES ===
            if len(df) > 20:
                cluster_features = self._extract_cluster_features(df, signal_data)
                features.update(cluster_features)
            
            # === ANOMALY DETECTION FEATURES ===
            features['is_anomaly'] = self._detect_signal_anomaly(signal_data, df)
            
            # Fill any missing values
            for key, value in features.items():
                if pd.isna(value) or np.isinf(value):
                    features[key] = 0.0
                    
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return self._basic_features(signal_data)
    
    def _basic_features(self, signal_data: Dict) -> Dict:
        """Fallback basic features when insufficient data"""
        return {
            'hour': datetime.now().hour,
            'is_london': 1 if 2 <= datetime.now().hour <= 7 else 0,
            'htf_aligned': 1 if signal_data.get('htf_aligned', False) else 0,
            'strength': signal_data.get('strength', 50) / 100.0,
            'price': signal_data.get('price', 0),
            'bias_bullish': 1 if signal_data.get('bias') == 'Bullish' else 0
        }
    
    def _calculate_resistance_proximity(self, current_price: float, price_history: np.ndarray) -> float:
        """Calculate proximity to resistance levels"""
        if len(price_history) < 5:
            return 0.5
        
        # Find local maxima as resistance
        resistance_levels = []
        for i in range(2, len(price_history) - 2):
            if (price_history[i] > price_history[i-1] and 
                price_history[i] > price_history[i-2] and
                price_history[i] > price_history[i+1] and 
                price_history[i] > price_history[i+2]):
                resistance_levels.append(price_history[i])
        
        if not resistance_levels:
            return 0.5
            
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
        distance = abs(nearest_resistance - current_price) / current_price
        return max(0, 1 - distance * 100)  # Closer = higher score
    
    def _calculate_support_proximity(self, current_price: float, price_history: np.ndarray) -> float:
        """Calculate proximity to support levels"""
        if len(price_history) < 5:
            return 0.5
            
        # Find local minima as support
        support_levels = []
        for i in range(2, len(price_history) - 2):
            if (price_history[i] < price_history[i-1] and 
                price_history[i] < price_history[i-2] and
                price_history[i] < price_history[i+1] and 
                price_history[i] < price_history[i+2]):
                support_levels.append(price_history[i])
        
        if not support_levels:
            return 0.5
            
        nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
        distance = abs(nearest_support - current_price) / current_price
        return max(0, 1 - distance * 100)
    
    def _count_consecutive_bias(self, recent_signals: pd.DataFrame, current_bias: str) -> int:
        """Count consecutive signals with same bias"""
        count = 0
        for _, signal in recent_signals.iloc[::-1].iterrows():
            if signal['bias'] == current_bias:
                count += 1
            else:
                break
        return count
    
    def _calculate_bias_changes(self, recent_signals: pd.DataFrame) -> float:
        """Calculate frequency of bias changes"""
        if len(recent_signals) < 2:
            return 0
        
        changes = 0
        for i in range(1, len(recent_signals)):
            if recent_signals.iloc[i]['bias'] != recent_signals.iloc[i-1]['bias']:
                changes += 1
        
        return changes / len(recent_signals)
    
    def _detect_reversal_pattern(self, recent_signals: pd.DataFrame, current_bias: str) -> float:
        """Detect reversal pattern strength"""
        if len(recent_signals) < 4:
            return 0
        
        # Look for 3+ consecutive opposite bias followed by current bias
        opposite_bias = 'Bearish' if current_bias == 'Bullish' else 'Bullish'
        
        consecutive_opposite = 0
        for _, signal in recent_signals.iloc[::-1].iterrows():
            if signal['bias'] == opposite_bias:
                consecutive_opposite += 1
            else:
                break
        
        return min(1.0, consecutive_opposite / 3.0)
    
    def _detect_continuation_pattern(self, recent_signals: pd.DataFrame, current_bias: str) -> float:
        """Detect continuation pattern strength"""
        if len(recent_signals) < 3:
            return 0
        
        same_bias_count = sum(1 for _, signal in recent_signals.iterrows() if signal['bias'] == current_bias)
        return min(1.0, same_bias_count / len(recent_signals))
    
    def _calculate_recent_drawdown(self, recent_data: pd.DataFrame) -> float:
        """Calculate recent drawdown"""
        if len(recent_data) < 3:
            return 0
        
        cumulative = recent_data['mfe'].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max).min()
        return abs(drawdown)
    
    def _calculate_be_efficiency(self, df: pd.DataFrame) -> float:
        """Calculate breakeven strategy efficiency"""
        if len(df) < 10:
            return 0.5
        
        be1_trades = df[df['be1_hit'] == True]
        be2_trades = df[df['be2_hit'] == True]
        
        if len(be1_trades) == 0 and len(be2_trades) == 0:
            return 0.5
        
        be1_success = be1_trades['mfe'].mean() if len(be1_trades) > 0 else 0
        be2_success = be2_trades['mfe'].mean() if len(be2_trades) > 0 else 0
        
        return (be1_success + be2_success) / 2.0
    
    def _extract_cluster_features(self, df: pd.DataFrame, signal_data: Dict) -> Dict:
        """Extract clustering-based features"""
        try:
            # Prepare data for clustering
            cluster_data = df[['entry_price', 'mfe', 'hour']].copy()
            cluster_data['hour'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.hour
            cluster_data = cluster_data.dropna()
            
            if len(cluster_data) < 10:
                return {'cluster_id': 0, 'cluster_success_rate': 0.5}
            
            # DBSCAN clustering
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(cluster_data)
            
            clustering = DBSCAN(eps=0.5, min_samples=3).fit(scaled_data)
            
            # Find which cluster current signal belongs to
            current_hour = datetime.now().hour
            current_point = scaler.transform([[signal_data.get('price', 0), 0, current_hour]])
            
            # Find nearest cluster
            cluster_distances = []
            for cluster_id in set(clustering.labels_):
                if cluster_id == -1:  # Noise
                    continue
                cluster_points = scaled_data[clustering.labels_ == cluster_id]
                if len(cluster_points) > 0:
                    distance = np.min(np.linalg.norm(cluster_points - current_point, axis=1))
                    cluster_distances.append((cluster_id, distance))
            
            if not cluster_distances:
                return {'cluster_id': -1, 'cluster_success_rate': 0.5}
            
            nearest_cluster = min(cluster_distances, key=lambda x: x[1])[0]
            
            # Calculate success rate for this cluster
            cluster_mask = clustering.labels_ == nearest_cluster
            cluster_mfes = df.loc[cluster_data.index[cluster_mask], 'mfe']
            success_rate = (cluster_mfes > 2).mean() if len(cluster_mfes) > 0 else 0.5
            
            return {
                'cluster_id': nearest_cluster,
                'cluster_success_rate': success_rate,
                'cluster_size': sum(cluster_mask)
            }
            
        except Exception as e:
            logger.error(f"Clustering error: {str(e)}")
            return {'cluster_id': 0, 'cluster_success_rate': 0.5}
    
    def _detect_signal_anomaly(self, signal_data: Dict, df: pd.DataFrame) -> float:
        """Detect if current signal is anomalous"""
        try:
            if len(df) < 20:
                return 0
            
            # Use Isolation Forest for anomaly detection
            features = ['entry_price', 'mfe']
            data = df[features].dropna()
            
            if len(data) < 10:
                return 0
            
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            iso_forest.fit(data)
            
            # Check if current signal is anomaly
            current_features = [[signal_data.get('price', 0), 0]]  # MFE unknown for new signal
            anomaly_score = iso_forest.decision_function(current_features)[0]
            
            # Convert to 0-1 scale (higher = more anomalous)
            return max(0, min(1, (0.5 - anomaly_score) * 2))
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return 0
    
    def train_models(self) -> Dict:
        """Train all ML models with current data"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT date, time, bias, session, signal_type, entry_price,
                       COALESCE(mfe_none, 0) as mfe,
                       COALESCE(be1_hit, false) as be1_hit,
                       COALESCE(be2_hit, false) as be2_hit,
                       created_at
                FROM signal_lab_trades 
                WHERE COALESCE(mfe_none, 0) != 0
                ORDER BY created_at DESC
                LIMIT 500
            """)
            
            training_data = cursor.fetchall()
            
            if len(training_data) < 50:
                return {"error": "Insufficient training data", "required": 50, "available": len(training_data)}
            
            # Prepare training dataset
            X_features = []
            y_success = []  # Binary: hit 2R+
            y_mfe = []      # Regression: actual MFE
            
            for i, trade in enumerate(training_data):
                # Create signal_data dict for feature extraction
                signal_data = {
                    'bias': trade['bias'],
                    'session': trade['session'],
                    'signal_type': trade['signal_type'],
                    'price': float(trade['entry_price']) if trade['entry_price'] else 0,
                    'htf_aligned': True,  # Assume aligned for training
                    'strength': 75  # Default strength
                }
                
                features = self.extract_comprehensive_features(signal_data)
                feature_vector = list(features.values())
                
                X_features.append(feature_vector)
                y_success.append(1 if float(trade['mfe']) >= 2.0 else 0)
                y_mfe.append(float(trade['mfe']))
            
            X = np.array(X_features)
            y_success = np.array(y_success)
            y_mfe = np.array(y_mfe)
            
            # Train Success Predictor (Classification)
            self.success_predictor = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            success_scores = cross_val_score(self.success_predictor, X, y_success, cv=tscv, scoring='accuracy')
            
            self.success_predictor.fit(X, y_success)
            self.model_accuracy['success_predictor'] = success_scores.mean()
            
            # Train MFE Predictor (Regression)
            self.mfe_predictor = xgb.XGBRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            mfe_scores = cross_val_score(self.mfe_predictor, X, y_mfe, cv=tscv, scoring='neg_mean_squared_error')
            self.mfe_predictor.fit(X, y_mfe)
            self.model_accuracy['mfe_predictor'] = -mfe_scores.mean()
            
            # Train Anomaly Detector
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.anomaly_detector.fit(X)
            
            # Store feature importance
            if hasattr(self.success_predictor, 'feature_importances_'):
                feature_names = list(self.extract_comprehensive_features(signal_data).keys())
                self.feature_importance = dict(zip(feature_names, self.success_predictor.feature_importances_))
            
            self.last_training = datetime.now()
            
            return {
                "status": "success",
                "models_trained": 3,
                "training_samples": len(training_data),
                "success_accuracy": self.model_accuracy.get('success_predictor', 0),
                "mfe_rmse": np.sqrt(self.model_accuracy.get('mfe_predictor', 0)),
                "last_training": self.last_training.isoformat(),
                "top_features": sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            }
            
        except Exception as e:
            logger.error(f"Model training error: {str(e)}")
            return {"error": str(e)}
    
    def predict_signal_quality(self, signal_data: Dict) -> Dict:
        """Predict signal quality and provide actionable insights"""
        try:
            if not self.success_predictor or not self.mfe_predictor:
                # Auto-train if models don't exist
                training_result = self.train_models()
                if "error" in training_result:
                    return {"error": "Models not trained", "details": training_result}
            
            # Extract features for current signal
            features = self.extract_comprehensive_features(signal_data)
            feature_vector = np.array([list(features.values())])
            
            # Predictions
            success_probability = self.success_predictor.predict_proba(feature_vector)[0][1] * 100
            predicted_mfe = self.mfe_predictor.predict(feature_vector)[0]
            
            # Anomaly detection
            anomaly_score = self.anomaly_detector.decision_function(feature_vector)[0]
            is_anomaly = anomaly_score < -0.1
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                success_probability, predicted_mfe, features, is_anomaly
            )
            
            # Calculate confidence intervals
            confidence_interval = self._calculate_confidence_interval(feature_vector)
            
            return {
                "success_probability": round(success_probability, 1),
                "predicted_mfe": round(predicted_mfe, 2),
                "confidence_interval": confidence_interval,
                "recommendation": recommendation,
                "is_anomaly": is_anomaly,
                "anomaly_score": round(anomaly_score, 3),
                "key_factors": self._identify_key_factors(features),
                "model_accuracy": round(self.model_accuracy.get('success_predictor', 0) * 100, 1),
                "feature_count": len(features),
                "prediction_confidence": self._calculate_prediction_confidence(success_probability, predicted_mfe)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {"error": str(e)}
    
    def _generate_recommendation(self, success_prob: float, predicted_mfe: float, 
                               features: Dict, is_anomaly: bool) -> str:
        """Generate actionable trading recommendation"""
        
        if is_anomaly:
            return "AVOID - Unusual market conditions detected"
        
        if success_prob >= 80 and predicted_mfe >= 2.5:
            return "STRONG BUY - High probability + High reward potential"
        elif success_prob >= 70 and predicted_mfe >= 2.0:
            return "BUY - Good probability with solid reward"
        elif success_prob >= 60 and predicted_mfe >= 1.5:
            return "MODERATE - Consider smaller position size"
        elif success_prob >= 50:
            return "WEAK - Low conviction, consider waiting"
        else:
            return "AVOID - Low probability of success"
    
    def _identify_key_factors(self, features: Dict) -> List[str]:
        """Identify key factors driving the prediction"""
        if not self.feature_importance:
            return ["Model training required"]
        
        # Get top contributing features for this signal
        key_factors = []
        
        # Sort features by importance and value
        sorted_features = sorted(
            [(name, importance, features.get(name, 0)) 
             for name, importance in self.feature_importance.items()],
            key=lambda x: x[1] * abs(x[2]), reverse=True
        )
        
        for name, importance, value in sorted_features[:5]:
            if importance > 0.05:  # Only significant features
                factor_desc = self._describe_feature(name, value)
                if factor_desc:
                    key_factors.append(factor_desc)
        
        return key_factors[:3]  # Top 3 factors
    
    def _describe_feature(self, feature_name: str, value: float) -> str:
        """Convert feature name and value to human-readable description"""
        descriptions = {
            'session_success_rate': f"Session success rate: {value:.1%}",
            'htf_aligned': "HTF aligned" if value > 0.5 else "HTF not aligned",
            'is_london_session': "London session" if value > 0.5 else "Non-London session",
            'consecutive_same_bias': f"{int(value)} consecutive same bias signals",
            'recent_win_rate': f"Recent win rate: {value:.1%}",
            'price_momentum': "Strong price momentum" if abs(value) > 0.5 else "Weak momentum",
            'reversal_pattern': "Strong reversal pattern" if value > 0.7 else None,
            'cluster_success_rate': f"Similar signals succeed {value:.1%} of time"
        }
        
        return descriptions.get(feature_name)
    
    def _calculate_confidence_interval(self, feature_vector: np.ndarray) -> Dict:
        """Calculate prediction confidence intervals"""
        try:
            # Use ensemble predictions for confidence estimation
            n_bootstrap = 50
            predictions = []
            
            for _ in range(n_bootstrap):
                # Add small random noise to simulate uncertainty
                noisy_features = feature_vector + np.random.normal(0, 0.01, feature_vector.shape)
                pred = self.mfe_predictor.predict(noisy_features)[0]
                predictions.append(pred)
            
            predictions = np.array(predictions)
            
            return {
                "lower_bound": round(np.percentile(predictions, 25), 2),
                "upper_bound": round(np.percentile(predictions, 75), 2),
                "std_dev": round(np.std(predictions), 2)
            }
            
        except Exception:
            return {"lower_bound": 0, "upper_bound": 0, "std_dev": 0}
    
    def _calculate_prediction_confidence(self, success_prob: float, predicted_mfe: float) -> str:
        """Calculate overall prediction confidence"""
        if not self.model_accuracy:
            return "LOW"
        
        model_acc = self.model_accuracy.get('success_predictor', 0)
        
        if model_acc > 0.8 and (success_prob > 80 or success_prob < 20):
            return "HIGH"
        elif model_acc > 0.7 and (success_prob > 70 or success_prob < 30):
            return "MEDIUM"
        else:
            return "LOW"
    
    def get_performance_analytics(self) -> Dict:
        """Get comprehensive performance analytics"""
        try:
            cursor = self.db.conn.cursor()
            
            # Get recent performance data
            cursor.execute("""
                SELECT date, time, bias, session, signal_type, entry_price,
                       COALESCE(mfe_none, 0) as mfe,
                       COALESCE(be1_hit, false) as be1_hit,
                       COALESCE(be2_hit, false) as be2_hit,
                       created_at
                FROM signal_lab_trades 
                WHERE created_at > NOW() - INTERVAL '30 days'
                ORDER BY created_at DESC
            """)
            
            recent_data = cursor.fetchall()
            
            if len(recent_data) < 10:
                return {"error": "Insufficient data for analytics"}
            
            df = pd.DataFrame(recent_data)
            df['mfe'] = pd.to_numeric(df['mfe'], errors='coerce').fillna(0)
            
            analytics = {}
            
            # === OVERALL PERFORMANCE ===
            analytics['total_trades'] = len(df)
            analytics['win_rate'] = (df['mfe'] > 0).mean() * 100
            analytics['big_win_rate'] = (df['mfe'] >= 2).mean() * 100
            analytics['avg_mfe'] = df['mfe'].mean()
            analytics['max_mfe'] = df['mfe'].max()
            analytics['expectancy'] = df['mfe'].mean()
            
            # === SESSION ANALYSIS ===
            session_stats = df.groupby('session').agg({
                'mfe': ['count', 'mean', lambda x: (x >= 2).mean() * 100]
            }).round(2)
            
            analytics['session_performance'] = {}
            for session in session_stats.index:
                analytics['session_performance'][session] = {
                    'trades': int(session_stats.loc[session, ('mfe', 'count')]),
                    'avg_mfe': float(session_stats.loc[session, ('mfe', 'mean')]),
                    'success_rate': float(session_stats.loc[session, ('mfe', '<lambda>')])
                }
            
            # === BIAS ANALYSIS ===
            bias_stats = df.groupby('bias').agg({
                'mfe': ['count', 'mean', lambda x: (x >= 2).mean() * 100]
            }).round(2)
            
            analytics['bias_performance'] = {}
            for bias in bias_stats.index:
                analytics['bias_performance'][bias] = {
                    'trades': int(bias_stats.loc[bias, ('mfe', 'count')]),
                    'avg_mfe': float(bias_stats.loc[bias, ('mfe', 'mean')]),
                    'success_rate': float(bias_stats.loc[bias, ('mfe', '<lambda>')])
                }
            
            # === TIME-BASED ANALYSIS ===
            df['hour'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.hour
            hourly_stats = df.groupby('hour')['mfe'].agg(['count', 'mean']).round(2)
            
            analytics['hourly_performance'] = {}
            for hour in hourly_stats.index:
                if hourly_stats.loc[hour, 'count'] >= 3:  # Minimum sample size
                    analytics['hourly_performance'][int(hour)] = {
                        'trades': int(hourly_stats.loc[hour, 'count']),
                        'avg_mfe': float(hourly_stats.loc[hour, 'mean'])
                    }
            
            # === PATTERN RECOGNITION ===
            analytics['patterns'] = self._analyze_patterns(df)
            
            # === RECOMMENDATIONS ===
            analytics['recommendations'] = self._generate_performance_recommendations(analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze trading patterns"""
        patterns = {}
        
        # Streak analysis
        df['win'] = df['mfe'] > 0
        df['streak'] = df['win'].groupby((df['win'] != df['win'].shift()).cumsum()).cumcount() + 1
        
        patterns['max_win_streak'] = df[df['win']]['streak'].max() if df['win'].any() else 0
        patterns['max_loss_streak'] = df[~df['win']]['streak'].max() if (~df['win']).any() else 0
        
        # Consecutive bias analysis
        df['bias_change'] = df['bias'] != df['bias'].shift()
        patterns['avg_bias_run_length'] = df.groupby(df['bias_change'].cumsum()).size().mean()
        
        # Recovery analysis
        losing_trades = df[df['mfe'] <= 0]
        if len(losing_trades) > 0:
            recovery_times = []
            for idx in losing_trades.index:
                next_trades = df[df.index > idx]
                if len(next_trades) > 0:
                    first_win_idx = next_trades[next_trades['mfe'] > 0].index
                    if len(first_win_idx) > 0:
                        recovery_times.append(first_win_idx[0] - idx)
            
            patterns['avg_recovery_time'] = np.mean(recovery_times) if recovery_times else 0
        
        return patterns
    
    def _generate_performance_recommendations(self, analytics: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Session recommendations
        if 'session_performance' in analytics:
            best_session = max(analytics['session_performance'].items(), 
                             key=lambda x: x[1]['avg_mfe'])
            worst_session = min(analytics['session_performance'].items(), 
                              key=lambda x: x[1]['avg_mfe'])
            
            if best_session[1]['avg_mfe'] > worst_session[1]['avg_mfe'] * 1.5:
                recommendations.append(
                    f"Focus on {best_session[0]} session (avg MFE: {best_session[1]['avg_mfe']:.2f}R) "
                    f"vs {worst_session[0]} (avg MFE: {worst_session[1]['avg_mfe']:.2f}R)"
                )
        
        # Bias recommendations
        if 'bias_performance' in analytics:
            bias_perf = analytics['bias_performance']
            if 'Bullish' in bias_perf and 'Bearish' in bias_perf:
                bull_mfe = bias_perf['Bullish']['avg_mfe']
                bear_mfe = bias_perf['Bearish']['avg_mfe']
                
                if abs(bull_mfe - bear_mfe) > 0.5:
                    better_bias = 'Bullish' if bull_mfe > bear_mfe else 'Bearish'
                    recommendations.append(
                        f"{better_bias} signals perform better "
                        f"({max(bull_mfe, bear_mfe):.2f}R vs {min(bull_mfe, bear_mfe):.2f}R)"
                    )
        
        # Win rate recommendations
        win_rate = analytics.get('win_rate', 0)
        if win_rate < 50:
            recommendations.append("Consider tighter entry criteria - win rate below 50%")
        elif win_rate > 80:
            recommendations.append("Consider increasing position size - high win rate indicates conservative entries")
        
        return recommendations
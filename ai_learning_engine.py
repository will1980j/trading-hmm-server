#!/usr/bin/env python3
"""
AI Learning Engine - Continuous Learning and Optimization
Uses advanced ML techniques to improve trading performance
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score
import xgboost as xgb
import tensorflow as tf
from tensorflow import keras
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AILearningEngine:
    def __init__(self):
        self.models = {
            'signal_classifier': None,
            'profit_predictor': None,
            'risk_assessor': None,
            'pattern_detector': None,
            'market_regime': None
        }
        
        self.scalers = {
            'features': StandardScaler(),
            'targets': StandardScaler()
        }
        
        self.encoders = {
            'session': LabelEncoder(),
            'macro': LabelEncoder(),
            'signal_type': LabelEncoder()
        }
        
        self.feature_importance = {}
        self.model_performance = {}
        self.learning_history = []
        
        # Neural network for complex pattern recognition
        self.neural_net = None
        self.is_trained = False
        
    def prepare_features(self, market_data: pd.DataFrame, ict_signals: List[Dict], 
                        trade_history: List[Dict]) -> pd.DataFrame:
        """Prepare comprehensive feature set for ML models"""
        try:
            features = []
            
            for i, signal in enumerate(ict_signals):
                if i >= len(market_data):
                    continue
                    
                candle = market_data.iloc[i]
                
                # Price action features
                price_features = self._extract_price_features(market_data, i)
                
                # Volume features
                volume_features = self._extract_volume_features(market_data, i)
                
                # Technical indicator features
                tech_features = self._extract_technical_features(market_data, i)
                
                # ICT-specific features
                ict_features = self._extract_ict_features(signal, market_data, i)
                
                # Time-based features
                time_features = self._extract_time_features(signal.get('timestamp', datetime.now()))
                
                # Market microstructure features
                microstructure_features = self._extract_microstructure_features(market_data, i)
                
                # Combine all features
                combined_features = {
                    **price_features,
                    **volume_features,
                    **tech_features,
                    **ict_features,
                    **time_features,
                    **microstructure_features
                }
                
                # Add target variables if trade history available
                if trade_history and i < len(trade_history):
                    trade = trade_history[i]
                    combined_features.update({
                        'profit_target': trade.get('pnl', 0),
                        'success': 1 if trade.get('result') == 'WIN' else 0,
                        'risk_reward_actual': trade.get('actual_rr', 0),
                        'duration_minutes': trade.get('duration_minutes', 0)
                    })
                
                features.append(combined_features)
            
            return pd.DataFrame(features)
            
        except Exception as e:
            logger.error(f"Feature preparation error: {e}")
            return pd.DataFrame()
    
    def _extract_price_features(self, data: pd.DataFrame, index: int) -> Dict:
        """Extract price action features"""
        if index < 20:
            return {}
        
        current = data.iloc[index]
        recent = data.iloc[max(0, index-20):index+1]
        
        return {
            'price_momentum_5': (current['close'] - data.iloc[index-5]['close']) / data.iloc[index-5]['close'],
            'price_momentum_10': (current['close'] - data.iloc[index-10]['close']) / data.iloc[index-10]['close'],
            'price_momentum_20': (current['close'] - data.iloc[index-20]['close']) / data.iloc[index-20]['close'],
            'body_size': abs(current['close'] - current['open']) / current['open'],
            'upper_wick': (current['high'] - max(current['open'], current['close'])) / current['open'],
            'lower_wick': (min(current['open'], current['close']) - current['low']) / current['open'],
            'price_position': (current['close'] - recent['low'].min()) / (recent['high'].max() - recent['low'].min()),
            'volatility_ratio': recent['high'].std() / recent['close'].mean(),
            'range_position': (current['close'] - current['low']) / (current['high'] - current['low']) if current['high'] != current['low'] else 0.5
        }
    
    def _extract_volume_features(self, data: pd.DataFrame, index: int) -> Dict:
        """Extract volume-based features"""
        if index < 10 or 'volume' not in data.columns:
            return {'volume_ratio': 1.0, 'volume_trend': 0.0}
        
        current = data.iloc[index]
        recent = data.iloc[max(0, index-10):index+1]
        
        avg_volume = recent['volume'].mean()
        volume_ratio = current['volume'] / avg_volume if avg_volume > 0 else 1.0
        
        return {
            'volume_ratio': volume_ratio,
            'volume_trend': (recent['volume'].iloc[-3:].mean() - recent['volume'].iloc[:3].mean()) / recent['volume'].mean(),
            'volume_price_trend': np.corrcoef(recent['volume'], recent['close'])[0, 1] if len(recent) > 1 else 0
        }
    
    def _extract_technical_features(self, data: pd.DataFrame, index: int) -> Dict:
        """Extract technical indicator features"""
        if index < 20:
            return {}
        
        recent = data.iloc[max(0, index-20):index+1]
        current = data.iloc[index]
        
        # RSI
        rsi = self._calculate_rsi(recent['close'])
        
        # Moving averages
        sma_5 = recent['close'].tail(5).mean()
        sma_10 = recent['close'].tail(10).mean()
        sma_20 = recent['close'].tail(20).mean()
        
        # MACD
        macd_line, macd_signal = self._calculate_macd(recent['close'])
        
        return {
            'rsi': rsi,
            'rsi_oversold': 1 if rsi < 30 else 0,
            'rsi_overbought': 1 if rsi > 70 else 0,
            'price_vs_sma5': (current['close'] - sma_5) / sma_5,
            'price_vs_sma10': (current['close'] - sma_10) / sma_10,
            'price_vs_sma20': (current['close'] - sma_20) / sma_20,
            'sma_alignment': 1 if sma_5 > sma_10 > sma_20 else -1 if sma_5 < sma_10 < sma_20 else 0,
            'macd_signal': 1 if macd_line > macd_signal else -1,
            'macd_momentum': macd_line - macd_signal
        }
    
    def _extract_ict_features(self, signal: Dict, data: pd.DataFrame, index: int) -> Dict:
        """Extract ICT-specific features"""
        return {
            'signal_confidence': signal.get('confidence', 0.5),
            'macro_active': 1 if signal.get('macro') else 0,
            'fvg_interaction': 1 if 'fvg' in signal.get('reason', '').lower() else 0,
            'liquidity_sweep': 1 if 'sweep' in signal.get('reason', '').lower() else 0,
            'session_alignment': 1 if signal.get('macro') in ['Opening_Range', 'Pre_Lunch', 'PM_Start'] else 0,
            'risk_reward_planned': abs(signal.get('take_profit', 0) - signal.get('entry', 0)) / abs(signal.get('entry', 0) - signal.get('stop_loss', 0)) if signal.get('stop_loss') != signal.get('entry') else 0
        }
    
    def _extract_time_features(self, timestamp) -> Dict:
        """Extract time-based features"""
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        return {
            'hour': timestamp.hour,
            'minute': timestamp.minute,
            'day_of_week': timestamp.weekday(),
            'is_monday': 1 if timestamp.weekday() == 0 else 0,
            'is_friday': 1 if timestamp.weekday() == 4 else 0,
            'is_london_session': 1 if 2 <= timestamp.hour <= 11 else 0,
            'is_ny_session': 1 if 13 <= timestamp.hour <= 21 else 0,
            'is_overlap': 1 if 13 <= timestamp.hour <= 16 else 0
        }
    
    def _extract_microstructure_features(self, data: pd.DataFrame, index: int) -> Dict:
        """Extract market microstructure features"""
        if index < 5:
            return {}
        
        recent = data.iloc[max(0, index-5):index+1]
        
        # Order flow approximation
        buying_pressure = sum(1 for i in range(len(recent)-1) if recent.iloc[i+1]['close'] > recent.iloc[i]['close'])
        selling_pressure = sum(1 for i in range(len(recent)-1) if recent.iloc[i+1]['close'] < recent.iloc[i]['close'])
        
        return {
            'buying_pressure': buying_pressure / len(recent),
            'selling_pressure': selling_pressure / len(recent),
            'price_efficiency': len(recent) / (recent['high'].max() - recent['low'].min()) if recent['high'].max() != recent['low'].min() else 1,
            'consolidation_factor': recent['close'].std() / recent['close'].mean()
        }
    
    def train_models(self, features_df: pd.DataFrame) -> Dict:
        """Train all ML models with prepared features"""
        try:
            if len(features_df) < 50:
                return {'status': 'insufficient_data', 'samples': len(features_df)}
            
            # Prepare data
            feature_cols = [col for col in features_df.columns if col not in ['profit_target', 'success', 'risk_reward_actual', 'duration_minutes']]
            X = features_df[feature_cols].fillna(0)
            
            # Scale features
            X_scaled = self.scalers['features'].fit_transform(X)
            
            results = {}
            
            # Train signal classifier (predict success/failure)
            if 'success' in features_df.columns:
                y_class = features_df['success'].fillna(0)
                self.models['signal_classifier'] = self._train_classifier(X_scaled, y_class, 'signal_classifier')
                results['signal_classifier'] = self.model_performance.get('signal_classifier', {})
            
            # Train profit predictor
            if 'profit_target' in features_df.columns:
                y_profit = features_df['profit_target'].fillna(0)
                self.models['profit_predictor'] = self._train_regressor(X_scaled, y_profit, 'profit_predictor')
                results['profit_predictor'] = self.model_performance.get('profit_predictor', {})
            
            # Train risk assessor
            if 'risk_reward_actual' in features_df.columns:
                y_risk = features_df['risk_reward_actual'].fillna(0)
                self.models['risk_assessor'] = self._train_regressor(X_scaled, y_risk, 'risk_assessor')
                results['risk_assessor'] = self.model_performance.get('risk_assessor', {})
            
            # Train neural network for pattern detection
            self._train_neural_network(X_scaled, features_df)
            
            self.is_trained = True
            
            # Log learning event
            self.learning_history.append({
                'timestamp': datetime.now().isoformat(),
                'samples_trained': len(features_df),
                'models_updated': list(results.keys()),
                'performance': results
            })
            
            return {
                'status': 'success',
                'models_trained': list(results.keys()),
                'samples_used': len(features_df),
                'performance': results
            }
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _train_classifier(self, X: np.ndarray, y: np.ndarray, model_name: str):
        """Train classification model"""
        try:
            # Use ensemble of classifiers
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
            xgb_model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Train and evaluate Random Forest
            rf_scores = cross_val_score(rf_model, X, y, cv=tscv, scoring='accuracy')
            rf_model.fit(X, y)
            
            # Train and evaluate XGBoost
            xgb_scores = cross_val_score(xgb_model, X, y, cv=tscv, scoring='accuracy')
            xgb_model.fit(X, y)
            
            # Choose best model
            if rf_scores.mean() > xgb_scores.mean():
                best_model = rf_model
                best_score = rf_scores.mean()
                model_type = 'RandomForest'
            else:
                best_model = xgb_model
                best_score = xgb_scores.mean()
                model_type = 'XGBoost'
            
            # Store performance metrics
            self.model_performance[model_name] = {
                'accuracy': best_score,
                'model_type': model_type,
                'cv_scores': rf_scores.tolist() if model_type == 'RandomForest' else xgb_scores.tolist(),
                'feature_importance': best_model.feature_importances_.tolist() if hasattr(best_model, 'feature_importances_') else []
            }
            
            return best_model
            
        except Exception as e:
            logger.error(f"Classifier training error: {e}")
            return None
    
    def _train_regressor(self, X: np.ndarray, y: np.ndarray, model_name: str):
        """Train regression model"""
        try:
            # Use ensemble of regressors
            gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            xgb_model = xgb.XGBRegressor(random_state=42)
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Train and evaluate models
            gb_scores = cross_val_score(gb_model, X, y, cv=tscv, scoring='r2')
            gb_model.fit(X, y)
            
            xgb_scores = cross_val_score(xgb_model, X, y, cv=tscv, scoring='r2')
            xgb_model.fit(X, y)
            
            # Choose best model
            if gb_scores.mean() > xgb_scores.mean():
                best_model = gb_model
                best_score = gb_scores.mean()
                model_type = 'GradientBoosting'
            else:
                best_model = xgb_model
                best_score = xgb_scores.mean()
                model_type = 'XGBoost'
            
            # Store performance metrics
            self.model_performance[model_name] = {
                'r2_score': best_score,
                'model_type': model_type,
                'cv_scores': gb_scores.tolist() if model_type == 'GradientBoosting' else xgb_scores.tolist(),
                'feature_importance': best_model.feature_importances_.tolist() if hasattr(best_model, 'feature_importances_') else []
            }
            
            return best_model
            
        except Exception as e:
            logger.error(f"Regressor training error: {e}")
            return None
    
    def _train_neural_network(self, X: np.ndarray, features_df: pd.DataFrame):
        """Train neural network for complex pattern recognition"""
        try:
            if 'success' not in features_df.columns:
                return
            
            y = features_df['success'].fillna(0).values
            
            # Build neural network
            model = keras.Sequential([
                keras.layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dropout(0.2),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(1, activation='sigmoid')
            ])
            
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            # Train with early stopping
            early_stopping = keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
            
            # Split data for validation
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            history = model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_data=(X_val, y_val),
                callbacks=[early_stopping],
                verbose=0
            )
            
            self.neural_net = model
            
            # Store performance
            val_accuracy = max(history.history['val_accuracy'])
            self.model_performance['neural_network'] = {
                'val_accuracy': val_accuracy,
                'epochs_trained': len(history.history['loss']),
                'final_loss': history.history['val_loss'][-1]
            }
            
        except Exception as e:
            logger.error(f"Neural network training error: {e}")
    
    def predict_signal_quality(self, features: Dict) -> Dict:
        """Predict signal quality using trained models"""
        try:
            if not self.is_trained:
                return {'confidence': 0.5, 'predicted_success': 0.5, 'source': 'default'}
            
            # Prepare features
            feature_vector = self._dict_to_vector(features)
            feature_vector_scaled = self.scalers['features'].transform([feature_vector])
            
            predictions = {}
            
            # Signal classifier prediction
            if self.models['signal_classifier']:
                success_prob = self.models['signal_classifier'].predict_proba(feature_vector_scaled)[0][1]
                predictions['success_probability'] = success_prob
            
            # Profit predictor
            if self.models['profit_predictor']:
                predicted_profit = self.models['profit_predictor'].predict(feature_vector_scaled)[0]
                predictions['predicted_profit'] = predicted_profit
            
            # Risk assessor
            if self.models['risk_assessor']:
                predicted_rr = self.models['risk_assessor'].predict(feature_vector_scaled)[0]
                predictions['predicted_risk_reward'] = predicted_rr
            
            # Neural network prediction
            if self.neural_net:
                nn_prediction = self.neural_net.predict(feature_vector_scaled, verbose=0)[0][0]
                predictions['neural_confidence'] = float(nn_prediction)
            
            # Combine predictions
            combined_confidence = np.mean([
                predictions.get('success_probability', 0.5),
                predictions.get('neural_confidence', 0.5)
            ])
            
            return {
                'combined_confidence': combined_confidence,
                'individual_predictions': predictions,
                'model_count': len([m for m in self.models.values() if m is not None]),
                'source': 'ml_ensemble'
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {'confidence': 0.5, 'error': str(e), 'source': 'error'}
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance across all models"""
        importance_summary = {}
        
        for model_name, performance in self.model_performance.items():
            if 'feature_importance' in performance and performance['feature_importance']:
                importance_summary[model_name] = performance['feature_importance']
        
        return importance_summary
    
    def optimize_hyperparameters(self, features_df: pd.DataFrame) -> Dict:
        """Optimize model hyperparameters using grid search"""
        # This would implement hyperparameter optimization
        # For now, return current performance
        return self.model_performance
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else 50.0
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[float, float]:
        """Calculate MACD indicator"""
        if len(prices) < 26:
            return 0.0, 0.0
        
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        
        return macd_line.iloc[-1], signal_line.iloc[-1]
    
    def _dict_to_vector(self, features: Dict) -> List[float]:
        """Convert feature dictionary to vector"""
        # This should match the feature extraction order
        expected_features = [
            'price_momentum_5', 'price_momentum_10', 'price_momentum_20',
            'body_size', 'upper_wick', 'lower_wick', 'price_position',
            'volatility_ratio', 'range_position', 'volume_ratio', 'volume_trend',
            'volume_price_trend', 'rsi', 'rsi_oversold', 'rsi_overbought',
            'price_vs_sma5', 'price_vs_sma10', 'price_vs_sma20', 'sma_alignment',
            'macd_signal', 'macd_momentum', 'signal_confidence', 'macro_active',
            'fvg_interaction', 'liquidity_sweep', 'session_alignment',
            'risk_reward_planned', 'hour', 'minute', 'day_of_week',
            'is_monday', 'is_friday', 'is_london_session', 'is_ny_session',
            'is_overlap', 'buying_pressure', 'selling_pressure',
            'price_efficiency', 'consolidation_factor'
        ]
        
        return [features.get(feature, 0.0) for feature in expected_features]
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'encoders': self.encoders,
                'performance': self.model_performance,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
            logger.info(f"Models saved to {filepath}")
        except Exception as e:
            logger.error(f"Model save error: {e}")
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        try:
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.encoders = model_data['encoders']
            self.model_performance = model_data['performance']
            self.is_trained = model_data['is_trained']
            logger.info(f"Models loaded from {filepath}")
        except Exception as e:
            logger.error(f"Model load error: {e}")
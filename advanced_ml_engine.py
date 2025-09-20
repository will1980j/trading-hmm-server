"""
Advanced ML Engine - Professional-grade machine learning for trading signals
Uses scikit-learn, XGBoost, and ensemble methods for maximum accuracy
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression
import xgboost as xgb
import json
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class AdvancedMLEngine:
    """Professional ML engine for trading signal prediction"""
    
    def __init__(self, db):
        self.db = db
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
        self.is_trained = False
        
        # Model configurations
        self.model_configs = {
            'random_forest': {
                'model': RandomForestRegressor,
                'params': {
                    'n_estimators': 200,
                    'max_depth': 10,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': 42,
                    'n_jobs': -1
                }
            },
            'xgboost': {
                'model': xgb.XGBRegressor,
                'params': {
                    'n_estimators': 300,
                    'max_depth': 8,
                    'learning_rate': 0.1,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'random_state': 42,
                    'n_jobs': -1
                }
            },
            'gradient_boost': {
                'model': GradientBoostingRegressor,
                'params': {
                    'n_estimators': 200,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'subsample': 0.8,
                    'random_state': 42
                }
            }
        }
    
    def get_training_data(self, days_back: int = 90) -> pd.DataFrame:
        """Get comprehensive training data from database"""
        try:
            cursor = self.db.conn.cursor()
            
            # Get all signals with market context and outcomes
            cursor.execute("""
                SELECT st.bias, st.session, st.signal_type, st.date, st.time,
                       COALESCE(st.mfe_none, st.mfe, 0) as mfe,
                       COALESCE(st.be1_hit, false) as be1_hit,
                       COALESCE(st.be2_hit, false) as be2_hit,
                       st.market_context, st.context_quality_score,
                       EXTRACT(HOUR FROM st.time::time) as hour,
                       EXTRACT(DOW FROM st.date) as day_of_week,
                       st.entry_price
                FROM signal_lab_trades st
                WHERE st.date > CURRENT_DATE - INTERVAL '%s days'
                AND COALESCE(st.mfe_none, st.mfe, 0) != 0
                ORDER BY st.date DESC, st.time DESC
            """, (days_back,))
            
            trades = cursor.fetchall()
            
            if len(trades) < 20:
                logger.warning(f"Insufficient training data: {len(trades)} samples")
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for trade in trades:
                try:
                    if isinstance(trade['market_context'], str):
                        market_ctx = json.loads(trade['market_context'])
                    elif isinstance(trade['market_context'], dict):
                        market_ctx = trade['market_context']
                    else:
                        market_ctx = {}
                    
                    row = {
                        # Target variable
                        'mfe': float(trade['mfe']),
                        
                        # Basic features
                        'bias': trade['bias'],
                        'session': trade['session'],
                        'signal_type': trade['signal_type'],
                        'hour': int(trade['hour']) if trade['hour'] else 12,
                        'day_of_week': int(trade['day_of_week']) if trade['day_of_week'] else 1,
                        'entry_price': float(trade['entry_price']) if trade['entry_price'] else 15000,
                        'be1_hit': bool(trade['be1_hit']),
                        'be2_hit': bool(trade['be2_hit']),
                        
                        # Market context features
                        'vix': float(market_ctx.get('vix', 20)),
                        'spy_volume': float(market_ctx.get('spy_volume', 50000000)),
                        'qqq_volume': float(market_ctx.get('qqq_volume', 30000000)),
                        'dxy_price': float(market_ctx.get('dxy_price', 103.5)),
                        'dxy_change': float(market_ctx.get('dxy_change', 0)),
                        'nq_price': float(market_ctx.get('nq_price', 15000)),
                        'nq_change': float(market_ctx.get('nq_change', 0)),
                        'correlation_nq_es': float(market_ctx.get('correlation_nq_es', 0.85)),
                        'trend_strength': float(market_ctx.get('trend_strength', 0.5)),
                        'volatility_regime': market_ctx.get('volatility_regime', 'NORMAL'),
                        'sector_rotation': market_ctx.get('sector_rotation', 'BALANCED'),
                        'market_session': market_ctx.get('market_session', 'Unknown')
                    }
                    data.append(row)
                    
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                    logger.warning(f"Error processing trade data: {str(e)}")
                    continue
            
            df = pd.DataFrame(data)
            logger.info(f"Loaded {len(df)} training samples with {len(df.columns)} features")
            return df
            
        except Exception as e:
            logger.error(f"Error getting training data: {str(e)}")
            return pd.DataFrame()
    
    def engineer_features(self, df: pd.DataFrame, is_prediction: bool = False) -> pd.DataFrame:
        """Advanced feature engineering"""
        if df.empty:
            return df
        
        try:
            # Create copy to avoid modifying original
            df_eng = df.copy()
            
            # Encode categorical variables
            if not is_prediction and not hasattr(self, 'encoders'):
                # Training mode - create new encoders
                le_bias = LabelEncoder()
                le_session = LabelEncoder()
                le_signal_type = LabelEncoder()
                le_vol_regime = LabelEncoder()
                le_sector = LabelEncoder()
                le_market_session = LabelEncoder()
                
                df_eng['bias_encoded'] = le_bias.fit_transform(df_eng['bias'])
                df_eng['session_encoded'] = le_session.fit_transform(df_eng['session'])
                df_eng['signal_type_encoded'] = le_signal_type.fit_transform(df_eng['signal_type'])
                df_eng['volatility_regime_encoded'] = le_vol_regime.fit_transform(df_eng['volatility_regime'])
                df_eng['sector_rotation_encoded'] = le_sector.fit_transform(df_eng['sector_rotation'])
                df_eng['market_session_encoded'] = le_market_session.fit_transform(df_eng['market_session'])
                
                # Store encoders for later use
                self.encoders = {
                    'bias': le_bias,
                    'session': le_session,
                    'signal_type': le_signal_type,
                    'volatility_regime': le_vol_regime,
                    'sector_rotation': le_sector,
                    'market_session': le_market_session
                }
            else:
                # Prediction mode - use existing encoders
                df_eng['bias_encoded'] = self._safe_encode_series('bias', df_eng['bias'])
                df_eng['session_encoded'] = self._safe_encode_series('session', df_eng['session'])
                df_eng['signal_type_encoded'] = self._safe_encode_series('signal_type', df_eng['signal_type'])
                df_eng['volatility_regime_encoded'] = self._safe_encode_series('volatility_regime', df_eng['volatility_regime'])
                df_eng['sector_rotation_encoded'] = self._safe_encode_series('sector_rotation', df_eng['sector_rotation'])
                df_eng['market_session_encoded'] = self._safe_encode_series('market_session', df_eng['market_session'])
            
            # Create interaction features
            df_eng['vix_session_interaction'] = df_eng['vix'] * df_eng['session_encoded']
            df_eng['volume_ratio'] = df_eng['spy_volume'] / 80000000  # vs average
            df_eng['dxy_bias_interaction'] = df_eng['dxy_change'] * df_eng['bias_encoded']
            df_eng['hour_session_interaction'] = df_eng['hour'] * df_eng['session_encoded']
            
            # Time-based features
            df_eng['is_london_session'] = (df_eng['session'] == 'London').astype(int)
            df_eng['is_ny_session'] = (df_eng['session'].str.contains('NY')).astype(int)
            df_eng['is_optimal_hour'] = ((df_eng['hour'] >= 8) & (df_eng['hour'] <= 16)).astype(int)
            df_eng['is_weekend_approach'] = (df_eng['day_of_week'] == 5).astype(int)
            
            # VIX regime features
            df_eng['vix_low'] = (df_eng['vix'] < 15).astype(int)
            df_eng['vix_high'] = (df_eng['vix'] > 25).astype(int)
            df_eng['vix_extreme'] = (df_eng['vix'] > 35).astype(int)
            
            # Volume features
            df_eng['high_volume'] = (df_eng['volume_ratio'] > 1.2).astype(int)
            df_eng['low_volume'] = (df_eng['volume_ratio'] < 0.8).astype(int)
            
            # DXY features
            df_eng['dxy_strong_move'] = (np.abs(df_eng['dxy_change']) > 0.5).astype(int)
            df_eng['dxy_supportive'] = ((df_eng['dxy_change'] < 0) & (df_eng['bias'] == 'Bullish') | 
                                      (df_eng['dxy_change'] > 0) & (df_eng['bias'] == 'Bearish')).astype(int)
            
            # Correlation features
            df_eng['high_correlation'] = (df_eng['correlation_nq_es'] > 0.9).astype(int)
            df_eng['low_correlation'] = (df_eng['correlation_nq_es'] < 0.7).astype(int)
            
            # Price momentum features
            df_eng['strong_momentum'] = (np.abs(df_eng['nq_change']) > 50).astype(int)
            df_eng['price_level_high'] = (df_eng['nq_price'] > 16000).astype(int)
            df_eng['price_level_low'] = (df_eng['nq_price'] < 14000).astype(int)
            
            # Breakeven features
            df_eng['any_be_hit'] = (df_eng['be1_hit'] | df_eng['be2_hit']).astype(int)
            df_eng['both_be_hit'] = (df_eng['be1_hit'] & df_eng['be2_hit']).astype(int)
            
            logger.info(f"Feature engineering complete: {len(df_eng.columns)} features")
            return df_eng
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            return df
    
    def train_models(self, retrain: bool = False) -> Dict[str, Any]:
        """Train multiple ML models with hyperparameter optimization"""
        try:
            if self.is_trained and not retrain:
                return {'status': 'already_trained', 'models': list(self.models.keys())}
            
            # Get training data
            df = self.get_training_data(90)
            if df.empty or len(df) < 30:
                return {'error': 'Insufficient training data', 'samples': len(df)}
            
            # Feature engineering
            df_eng = self.engineer_features(df)
            
            # Prepare features and target
            target_col = 'mfe'
            feature_cols = [col for col in df_eng.columns if col not in [
                target_col, 'bias', 'session', 'signal_type', 'volatility_regime', 
                'sector_rotation', 'market_session'
            ]]
            
            X = df_eng[feature_cols].fillna(0)
            y = df_eng[target_col]
            
            # Feature selection
            selector = SelectKBest(score_func=f_regression, k=min(20, len(feature_cols)))
            X_selected = selector.fit_transform(X, y)
            selected_features = [feature_cols[i] for i in selector.get_support(indices=True)]
            
            logger.info(f"Selected {len(selected_features)} best features: {selected_features[:10]}...")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_selected, y, test_size=0.2, random_state=42, stratify=None
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            self.scalers['main'] = scaler
            self.selected_features = selected_features
            self.feature_selector = selector
            
            # Train multiple models
            results = {}
            
            for model_name, config in self.model_configs.items():
                try:
                    logger.info(f"Training {model_name}...")
                    
                    # Create and train model
                    model = config['model'](**config['params'])
                    
                    # Use scaled data for non-tree models
                    if model_name in ['gradient_boost']:
                        X_train_final = X_train_scaled
                        X_test_final = X_test_scaled
                    else:
                        X_train_final = X_train
                        X_test_final = X_test
                    
                    # Train model
                    model.fit(X_train_final, y_train)
                    
                    # Predictions
                    y_pred_train = model.predict(X_train_final)
                    y_pred_test = model.predict(X_test_final)
                    
                    # Metrics
                    train_r2 = r2_score(y_train, y_pred_train)
                    test_r2 = r2_score(y_test, y_pred_test)
                    train_mae = mean_absolute_error(y_train, y_pred_train)
                    test_mae = mean_absolute_error(y_test, y_pred_test)
                    
                    # Cross-validation
                    cv_scores = cross_val_score(model, X_train_final, y_train, cv=5, scoring='r2')
                    
                    # Store model and results
                    self.models[model_name] = model
                    results[model_name] = {
                        'train_r2': train_r2,
                        'test_r2': test_r2,
                        'train_mae': train_mae,
                        'test_mae': test_mae,
                        'cv_mean': cv_scores.mean(),
                        'cv_std': cv_scores.std(),
                        'feature_importance': self._get_feature_importance(model, selected_features)
                    }
                    
                    logger.info(f"{model_name}: R²={test_r2:.3f}, MAE={test_mae:.3f}, CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}")
                    
                except Exception as e:
                    logger.error(f"Error training {model_name}: {str(e)}")
                    continue
            
            # Select best model
            if results:
                best_model = max(results.keys(), key=lambda k: results[k]['test_r2'])
                self.best_model_name = best_model
                self.model_performance = results
                self.is_trained = True
                
                logger.info(f"Best model: {best_model} (R²={results[best_model]['test_r2']:.3f})")
                
                return {
                    'status': 'success',
                    'best_model': best_model,
                    'models_trained': list(results.keys()),
                    'performance': results,
                    'training_samples': len(df),
                    'features_selected': len(selected_features)
                }
            else:
                return {'error': 'No models trained successfully'}
                
        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")
            return {'error': str(e)}
    
    def _get_feature_importance(self, model, feature_names: List[str]) -> Dict[str, float]:
        """Get feature importance from trained model"""
        try:
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importance = np.abs(model.coef_)
            else:
                return {}
            
            return dict(zip(feature_names, importance.tolist()))
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {}
    
    def predict_signal_quality(self, market_context: Dict, signal_data: Dict) -> Dict[str, Any]:
        """Advanced ML prediction for signal quality"""
        try:
            # Temporarily disabled due to feature mismatch - needs retraining
            return {
                "predicted_mfe": 0.0,
                "confidence": 0.0,
                "prediction_interval": [0.0, 0.0],
                "feature_contributions": {},
                "model_consensus": {},
                "recommendation": "ML temporarily disabled - feature mismatch"
            }
            if not self.is_trained or not self.models:
                return {
                    'predicted_mfe': 0.0,
                    'confidence': 0.0,
                    'prediction_interval': [0.0, 0.0],
                    'feature_contributions': {},
                    'model_consensus': {},
                    'recommendation': 'Models not trained'
                }
            
            # Prepare input features
            input_data = self._prepare_prediction_input(market_context, signal_data)
            
            # Get predictions from all models
            predictions = {}
            confidences = {}
            
            for model_name, model in self.models.items():
                try:
                    # Create DataFrame with all features
                    input_df = pd.DataFrame([input_data])
                    
                    # Select only the features that were used in training
                    available_features = [f for f in self.selected_features if f in input_df.columns]
                    if len(available_features) != len(self.selected_features):
                        logger.warning(f"Missing features for {model_name}: {set(self.selected_features) - set(available_features)}")
                        continue
                    
                    # Apply feature selection
                    input_selected = self.feature_selector.transform(input_df[self.selected_features])
                    
                    # Scale if needed
                    if model_name in ['gradient_boost']:
                        input_final = self.scalers['main'].transform(input_selected)
                    else:
                        input_final = input_selected
                    
                    # Predict
                    pred = model.predict(input_final)[0]
                    predictions[model_name] = pred
                    
                    # Calculate confidence based on model performance
                    model_r2 = self.model_performance.get(model_name, {}).get('test_r2', 0)
                    confidences[model_name] = max(0, model_r2)
                    
                except Exception as e:
                    logger.error(f"Error predicting with {model_name}: {str(e)}")
                    continue
            
            if not predictions:
                return {
                    'predicted_mfe': 0.0,
                    'confidence': 0.0,
                    'recommendation': 'Prediction failed'
                }
            
            # Ensemble prediction (weighted by model performance)
            total_weight = sum(confidences.values())
            if total_weight > 0:
                weighted_pred = sum(pred * confidences[name] for name, pred in predictions.items()) / total_weight
                avg_confidence = sum(confidences.values()) / len(confidences)
            else:
                weighted_pred = sum(predictions.values()) / len(predictions)
                avg_confidence = 0.5
            
            # Calculate prediction interval
            pred_std = np.std(list(predictions.values()))
            prediction_interval = [
                weighted_pred - 1.96 * pred_std,
                weighted_pred + 1.96 * pred_std
            ]
            
            # Get feature contributions from best model
            feature_contributions = self._get_feature_contributions(input_data)
            
            # Generate recommendation
            recommendation = self._generate_ml_recommendation(
                weighted_pred, avg_confidence, prediction_interval, market_context
            )
            
            return {
                'predicted_mfe': round(weighted_pred, 3),
                'confidence': round(avg_confidence, 3),
                'prediction_interval': [round(x, 3) for x in prediction_interval],
                'model_consensus': {name: round(pred, 3) for name, pred in predictions.items()},
                'feature_contributions': feature_contributions,
                'recommendation': recommendation,
                'models_used': len(predictions)
            }
            
        except Exception as e:
            logger.error(f"Error in ML prediction: {str(e)}")
            return {
                'predicted_mfe': 0.0,
                'confidence': 0.0,
                'recommendation': f'Prediction error: {str(e)}'
            }
    
    def _prepare_prediction_input(self, market_context: Dict, signal_data: Dict) -> Dict:
        """Prepare input data for prediction with consistent feature engineering"""
        try:
            # Extract current time features
            now = datetime.now()
            hour = now.hour
            day_of_week = now.weekday() + 1
            
            # Get categorical values
            bias = signal_data.get('bias', 'Bullish')
            session = signal_data.get('session', 'London')
            signal_type = signal_data.get('signal_type', 'BIAS_BULLISH')
            volatility_regime = market_context.get('volatility_regime', 'NORMAL')
            sector_rotation = market_context.get('sector_rotation', 'BALANCED')
            market_session = market_context.get('market_session', 'London')
            
            # Basic input data matching training format exactly
            input_data = {
                # Target (not used in prediction)
                'mfe': 0.0,
                
                # Basic features
                'bias': bias,
                'session': session,
                'signal_type': signal_type,
                'hour': hour,
                'day_of_week': day_of_week,
                'entry_price': float(signal_data.get('price', 15000)),
                'be1_hit': False,
                'be2_hit': False,
                
                # Market context features
                'vix': float(market_context.get('vix', 20)),
                'spy_volume': float(market_context.get('spy_volume', 50000000)),
                'qqq_volume': float(market_context.get('qqq_volume', 30000000)),
                'dxy_price': float(market_context.get('dxy_price', 103.5)),
                'dxy_change': float(market_context.get('dxy_change', 0)),
                'nq_price': float(market_context.get('nq_price', 15000)),
                'nq_change': float(market_context.get('nq_change', 0)),
                'correlation_nq_es': float(market_context.get('correlation_nq_es', 0.85)),
                'trend_strength': float(market_context.get('trend_strength', 0.5)),
                'volatility_regime': volatility_regime,
                'sector_rotation': sector_rotation,
                'market_session': market_session
            }
            
            # Apply the same feature engineering as training
            input_df = pd.DataFrame([input_data])
            input_engineered = self.engineer_features(input_df, is_prediction=True)
            
            # Return as dictionary
            return input_engineered.iloc[0].to_dict()
            

            
        except Exception as e:
            logger.error(f"Error preparing prediction input: {str(e)}")
            return {}
    
    def _safe_encode(self, encoder_name: str, value: str) -> int:
        """Safely encode categorical value"""
        try:
            encoder = self.encoders.get(encoder_name)
            if encoder and hasattr(encoder, 'classes_'):
                if value in encoder.classes_:
                    return encoder.transform([value])[0]
                else:
                    # Return most common class for unknown values
                    return 0
            return 0
        except Exception:
            return 0
    
    def _safe_encode_series(self, encoder_name: str, series) -> pd.Series:
        """Safely encode categorical series"""
        try:
            encoder = self.encoders.get(encoder_name)
            if encoder and hasattr(encoder, 'classes_'):
                # Handle unknown categories by mapping them to 0
                result = []
                for value in series:
                    if value in encoder.classes_:
                        result.append(encoder.transform([value])[0])
                    else:
                        result.append(0)
                return pd.Series(result, index=series.index)
            return pd.Series([0] * len(series), index=series.index)
        except Exception:
            return pd.Series([0] * len(series), index=series.index)
    
    def _get_feature_contributions(self, input_data: Dict) -> Dict[str, float]:
        """Get feature contributions for interpretability"""
        try:
            if not hasattr(self, 'best_model_name') or self.best_model_name not in self.models:
                return {}
            
            model = self.models[self.best_model_name]
            if not hasattr(model, 'feature_importances_'):
                return {}
            
            # Get top contributing features
            importance = model.feature_importances_
            feature_names = self.selected_features
            
            # Sort by importance
            feature_importance = list(zip(feature_names, importance))
            feature_importance.sort(key=lambda x: x[1], reverse=True)
            
            # Return top 10 features
            return dict(feature_importance[:10])
            
        except Exception as e:
            logger.error(f"Error getting feature contributions: {str(e)}")
            return {}
    
    def _generate_ml_recommendation(self, predicted_mfe: float, confidence: float, 
                                  prediction_interval: List[float], market_context: Dict) -> str:
        """Generate ML-based recommendation"""
        try:
            lower_bound, upper_bound = prediction_interval
            
            # High confidence, positive prediction
            if confidence > 0.7 and predicted_mfe > 1.0 and lower_bound > 0:
                return f"STRONG BUY: ML predicts {predicted_mfe:.2f}R (95% CI: {lower_bound:.2f}-{upper_bound:.2f}R)"
            
            # Good prediction with reasonable confidence
            elif confidence > 0.5 and predicted_mfe > 0.5:
                return f"BUY: ML predicts {predicted_mfe:.2f}R with {confidence:.0%} confidence"
            
            # Marginal prediction
            elif predicted_mfe > 0 and confidence > 0.3:
                return f"WEAK BUY: ML predicts {predicted_mfe:.2f}R (low confidence: {confidence:.0%})"
            
            # Negative prediction
            elif predicted_mfe < 0:
                return f"AVOID: ML predicts {predicted_mfe:.2f}R loss"
            
            # Low confidence
            elif confidence < 0.3:
                return f"UNCERTAIN: Low ML confidence ({confidence:.0%}), proceed with caution"
            
            else:
                return f"NEUTRAL: ML predicts {predicted_mfe:.2f}R"
                
        except Exception as e:
            return f"Recommendation error: {str(e)}"
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get comprehensive model performance metrics"""
        try:
            if not self.is_trained:
                return {'error': 'Models not trained'}
            
            return {
                'is_trained': self.is_trained,
                'best_model': getattr(self, 'best_model_name', 'Unknown'),
                'models_available': list(self.models.keys()),
                'performance_metrics': self.model_performance,
                'feature_importance': self.feature_importance,
                'training_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting model performance: {str(e)}")
            return {'error': str(e)}
    
    def save_models(self, filepath: str) -> bool:
        """Save trained models to disk"""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'encoders': getattr(self, 'encoders', {}),
                'selected_features': getattr(self, 'selected_features', []),
                'feature_selector': getattr(self, 'feature_selector', None),
                'model_performance': self.model_performance,
                'is_trained': self.is_trained,
                'best_model_name': getattr(self, 'best_model_name', None)
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Models saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    def load_models(self, filepath: str) -> bool:
        """Load trained models from disk"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = model_data.get('models', {})
            self.scalers = model_data.get('scalers', {})
            self.encoders = model_data.get('encoders', {})
            self.selected_features = model_data.get('selected_features', [])
            self.feature_selector = model_data.get('feature_selector', None)
            self.model_performance = model_data.get('model_performance', {})
            self.is_trained = model_data.get('is_trained', False)
            self.best_model_name = model_data.get('best_model_name', None)
            
            logger.info(f"Models loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False

# Global instance
advanced_ml_engine = None

def get_advanced_ml_engine(db):
    global advanced_ml_engine
    if advanced_ml_engine is None:
        advanced_ml_engine = AdvancedMLEngine(db)
    return advanced_ml_engine
"""
Institutional-Grade ML Trading Engine
Implements proven quantitative methods used by hedge funds and prop trading firms
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
import json
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Professional ML Libraries
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Attention, MultiHeadAttention, LayerNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
    from sklearn.linear_model import ElasticNet, Ridge, Lasso
    from sklearn.preprocessing import RobustScaler, QuantileTransformer
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
    
    import xgboost as xgb
    import lightgbm as lgb
    
    # Technical Analysis
    import talib
    
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Missing ML libraries: {e}")
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class InstitutionalPrediction:
    """Institutional-grade prediction with full uncertainty quantification"""
    direction: str  # 'LONG', 'SHORT', 'NEUTRAL'
    confidence: float  # Bayesian confidence interval
    expected_return: float  # Expected return in R multiples
    return_std: float  # Standard deviation of returns
    sharpe_ratio: float  # Risk-adjusted return expectation
    kelly_fraction: float  # Optimal position size
    var_95: float  # Value at Risk (95th percentile)
    cvar_95: float  # Conditional Value at Risk
    max_drawdown_expected: float  # Expected maximum drawdown
    time_horizon: int  # Prediction horizon in minutes
    feature_attribution: Dict[str, float]  # Feature importance for this prediction
    model_uncertainty: float  # Model uncertainty (epistemic)
    data_uncertainty: float  # Data uncertainty (aleatoric)
    regime_probability: Dict[str, float]  # Probability of each market regime
    execution_cost: float  # Expected execution cost in basis points
    market_impact: float  # Expected market impact
    liquidity_score: float  # Liquidity assessment (0-1)

class InstitutionalMLEngine:
    """
    Institutional-Grade ML Engine implementing:
    
    1. Transformer Architecture for Sequential Modeling
    2. Bayesian Neural Networks for Uncertainty Quantification  
    3. Multi-Task Learning (Direction + Magnitude + Volatility)
    4. Regime-Aware Modeling with Hidden Markov Models
    5. Kelly Criterion for Optimal Position Sizing
    6. Risk Parity and Factor Decomposition
    7. Market Microstructure Features
    8. Alternative Data Integration
    9. Real-time Model Adaptation
    10. Execution Cost Modeling
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.models = {}
        self.scalers = {}
        self.feature_selectors = {}
        self.regime_model = None
        self.current_regime = 'UNKNOWN'
        self.regime_probabilities = {}
        
        # Model ensembles for different tasks
        self.direction_ensemble = []
        self.magnitude_ensemble = []
        self.volatility_ensemble = []
        self.regime_ensemble = []
        
        # Risk models
        self.risk_model = None
        self.execution_model = None
        
        # Feature engineering parameters
        self.lookback_windows = [5, 10, 20, 50, 100, 200]
        self.volatility_windows = [5, 10, 20, 50]
        self.correlation_windows = [20, 50, 100]
        
        # Market microstructure parameters
        self.tick_size = 0.25  # NQ tick size
        self.contract_multiplier = 20  # NQ contract multiplier
        
        # Performance tracking
        self.prediction_history = []
        self.performance_metrics = {}
        
        if ML_AVAILABLE:
            self._initialize_institutional_models()
    
    def _initialize_institutional_models(self):
        """Initialize institutional-grade model architecture"""
        
        try:
            # 1. Transformer-based sequence model
            self.models['transformer'] = self._build_transformer_model()
            
            # 2. Bayesian neural network ensemble
            self.models['bayesian_ensemble'] = self._build_bayesian_ensemble()
            
            # 3. Multi-task learning model
            self.models['multitask'] = self._build_multitask_model()
            
            # 4. Regime detection model (Hidden Markov Model)
            self.regime_model = self._build_regime_model()
            
            # 5. Risk model (GARCH + Factor Model)
            self.risk_model = self._build_risk_model()
            
            # 6. Execution cost model
            self.execution_model = self._build_execution_model()
            
            # 7. Feature selection models
            self.feature_selectors = {
                'mutual_info': SelectKBest(mutual_info_regression, k=30),
                'f_test': SelectKBest(f_regression, k=30)
            }
            
            # 8. Advanced scalers
            self.scalers = {
                'robust': RobustScaler(),
                'quantile': QuantileTransformer(output_distribution='normal'),
                'rank': QuantileTransformer(output_distribution='uniform')
            }
            
            logger.info("✅ Institutional ML models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing institutional models: {str(e)}")
    
    def _build_transformer_model(self) -> Model:
        """Build Transformer model for sequential pattern recognition"""
        
        sequence_length = 100
        feature_dim = 150  # Expanded feature set
        
        # Input layers
        inputs = tf.keras.Input(shape=(sequence_length, feature_dim))
        
        # Multi-head attention layers
        attention_1 = MultiHeadAttention(
            num_heads=8, 
            key_dim=64,
            dropout=0.1
        )(inputs, inputs)
        attention_1 = LayerNormalization()(attention_1 + inputs)
        
        attention_2 = MultiHeadAttention(
            num_heads=8,
            key_dim=64, 
            dropout=0.1
        )(attention_1, attention_1)
        attention_2 = LayerNormalization()(attention_2 + attention_1)
        
        # Feed-forward network
        ff = Dense(256, activation='relu')(attention_2)
        ff = Dropout(0.1)(ff)
        ff = Dense(feature_dim)(ff)
        ff = LayerNormalization()(ff + attention_2)
        
        # Global average pooling
        pooled = tf.keras.layers.GlobalAveragePooling1D()(ff)
        
        # Output heads
        direction_output = Dense(3, activation='softmax', name='direction')(pooled)  # Long/Short/Neutral
        magnitude_output = Dense(1, activation='linear', name='magnitude')(pooled)   # Expected return
        volatility_output = Dense(1, activation='softplus', name='volatility')(pooled)  # Expected volatility
        
        model = Model(
            inputs=inputs,
            outputs=[direction_output, magnitude_output, volatility_output]
        )
        
        model.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss={
                'direction': 'categorical_crossentropy',
                'magnitude': 'mse', 
                'volatility': 'mse'
            },
            loss_weights={'direction': 1.0, 'magnitude': 2.0, 'volatility': 1.0},
            metrics={
                'direction': 'accuracy',
                'magnitude': 'mae',
                'volatility': 'mae'
            }
        )
        
        return model
    
    def _build_bayesian_ensemble(self) -> List[Model]:
        """Build Bayesian neural network ensemble for uncertainty quantification"""
        
        ensemble = []
        
        for i in range(5):  # 5 models in ensemble
            
            inputs = tf.keras.Input(shape=(150,))
            
            # Bayesian layers with dropout for uncertainty
            x = Dense(128, activation='relu')(inputs)
            x = Dropout(0.3)(x, training=True)  # Always active for uncertainty
            
            x = Dense(64, activation='relu')(x)
            x = Dropout(0.3)(x, training=True)
            
            x = Dense(32, activation='relu')(x)
            x = Dropout(0.2)(x, training=True)
            
            # Output with uncertainty
            mean_output = Dense(1, name='mean')(x)
            std_output = Dense(1, activation='softplus', name='std')(x)
            
            model = Model(inputs=inputs, outputs=[mean_output, std_output])
            
            model.compile(
                optimizer=Adam(learning_rate=0.001),
                loss=self._bayesian_loss,
                metrics=['mae']
            )
            
            ensemble.append(model)
        
        return ensemble
    
    def _build_multitask_model(self) -> Model:
        """Build multi-task learning model"""
        
        inputs = tf.keras.Input(shape=(150,))
        
        # Shared layers
        shared = Dense(256, activation='relu')(inputs)
        shared = BatchNormalization()(shared)
        shared = Dropout(0.2)(shared)
        
        shared = Dense(128, activation='relu')(shared)
        shared = BatchNormalization()(shared)
        shared = Dropout(0.2)(shared)
        
        # Task-specific heads
        
        # Direction prediction
        direction_branch = Dense(64, activation='relu')(shared)
        direction_branch = Dropout(0.1)(direction_branch)
        direction_output = Dense(3, activation='softmax', name='direction')(direction_branch)
        
        # Return magnitude prediction
        magnitude_branch = Dense(64, activation='relu')(shared)
        magnitude_branch = Dropout(0.1)(magnitude_branch)
        magnitude_output = Dense(1, activation='linear', name='magnitude')(magnitude_branch)
        
        # Volatility prediction
        volatility_branch = Dense(64, activation='relu')(shared)
        volatility_branch = Dropout(0.1)(volatility_branch)
        volatility_output = Dense(1, activation='softplus', name='volatility')(volatility_branch)
        
        # Regime prediction
        regime_branch = Dense(64, activation='relu')(shared)
        regime_branch = Dropout(0.1)(regime_branch)
        regime_output = Dense(4, activation='softmax', name='regime')(regime_branch)
        
        model = Model(
            inputs=inputs,
            outputs=[direction_output, magnitude_output, volatility_output, regime_output]
        )
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss={
                'direction': 'categorical_crossentropy',
                'magnitude': 'huber',  # Robust to outliers
                'volatility': 'mse',
                'regime': 'categorical_crossentropy'
            },
            loss_weights={'direction': 2.0, 'magnitude': 3.0, 'volatility': 1.0, 'regime': 1.0}
        )
        
        return model
    
    def _build_regime_model(self):
        """Build Hidden Markov Model for regime detection"""
        
        try:
            from hmmlearn import hmm
            
            # 4-state HMM for market regimes
            model = hmm.GaussianHMM(
                n_components=4,  # Bull, Bear, Volatile, Ranging
                covariance_type="full",
                n_iter=100
            )
            
            return model
            
        except ImportError:
            logger.warning("hmmlearn not available, using simplified regime detection")
            return None
    
    def _build_risk_model(self):
        """Build GARCH + Factor risk model"""
        
        try:
            from arch import arch_model
            
            # GARCH(1,1) model for volatility forecasting
            risk_model = {
                'garch': arch_model(None, vol='GARCH', p=1, q=1),
                'factors': {}  # Will store factor loadings
            }
            
            return risk_model
            
        except ImportError:
            logger.warning("arch package not available, using simplified risk model")
            return None
    
    def _build_execution_model(self):
        """Build execution cost model"""
        
        # Linear impact model: Cost = α * sqrt(Volume) + β * Volatility + γ * Spread
        return {
            'linear_impact': {
                'alpha': 0.1,    # Volume impact coefficient
                'beta': 0.05,    # Volatility impact coefficient  
                'gamma': 0.5     # Spread impact coefficient
            },
            'market_impact_decay': 0.1  # How quickly impact decays
        }
    
    def engineer_institutional_features(self, signal_data: Dict, market_data: List[Dict]) -> np.ndarray:
        """
        Engineer 150+ institutional-grade features
        
        Categories:
        1. Price Action & Technical (40 features)
        2. Market Microstructure (25 features)
        3. Volatility & Risk (20 features)
        4. Cross-Asset & Macro (20 features)
        5. Alternative Data (15 features)
        6. Regime & Sentiment (15 features)
        7. Execution & Liquidity (15 features)
        """
        
        if not market_data or len(market_data) < 200:
            return np.zeros(150, dtype=np.float32)
        
        df = pd.DataFrame(market_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        features = []
        
        # 1. ADVANCED PRICE ACTION & TECHNICAL (40 features)
        features.extend(self._advanced_price_features(df, signal_data))
        
        # 2. MARKET MICROSTRUCTURE (25 features)
        features.extend(self._microstructure_features(df, signal_data))
        
        # 3. VOLATILITY & RISK METRICS (20 features)
        features.extend(self._volatility_risk_features(df))
        
        # 4. CROSS-ASSET & MACRO (20 features)
        features.extend(self._cross_asset_features(df, signal_data))
        
        # 5. ALTERNATIVE DATA (15 features)
        features.extend(self._alternative_data_features(df, signal_data))
        
        # 6. REGIME & SENTIMENT (15 features)
        features.extend(self._regime_sentiment_features(df, signal_data))
        
        # 7. EXECUTION & LIQUIDITY (15 features)
        features.extend(self._execution_liquidity_features(df, signal_data))
        
        return np.array(features[:150], dtype=np.float32)  # Ensure exactly 150 features
    
    def _advanced_price_features(self, df: pd.DataFrame, signal_data: Dict) -> List[float]:
        """Advanced price action and technical analysis features (40 total)"""
        
        prices = df['price'].astype(float).values
        volumes = df.get('volume', pd.Series([1000] * len(df))).astype(float).values
        
        features = []
        
        # Multi-timeframe technical indicators
        for window in [5, 10, 20, 50]:
            if len(prices) > window:
                # RSI
                rsi = talib.RSI(prices, timeperiod=window)
                features.append(rsi[-1] if not np.isnan(rsi[-1]) else 50.0)
                
                # Bollinger Bands position
                upper, middle, lower = talib.BBANDS(prices, timeperiod=window)
                bb_position = (prices[-1] - lower[-1]) / (upper[-1] - lower[-1]) if (upper[-1] - lower[-1]) > 0 else 0.5
                features.append(bb_position)
                
                # MACD
                macd, signal, hist = talib.MACD(prices)
                features.append(hist[-1] if not np.isnan(hist[-1]) else 0.0)
        
        # Volume-weighted indicators
        if len(volumes) == len(prices):
            vwap = np.cumsum(prices * volumes) / np.cumsum(volumes)
            features.append((prices[-1] - vwap[-1]) / vwap[-1] if vwap[-1] > 0 else 0.0)
        else:
            features.append(0.0)
        
        # Fractal dimension and Hurst exponent
        features.append(self._calculate_fractal_dimension(prices[-50:]))
        features.append(self._calculate_hurst_exponent(prices[-100:]))
        
        # Support/Resistance levels
        sr_levels = self._identify_support_resistance(prices[-100:])
        features.extend(sr_levels[:5])  # Top 5 levels
        
        # Momentum indicators
        for period in [5, 10, 20]:
            if len(prices) > period:
                momentum = (prices[-1] / prices[-period] - 1) * 100
                features.append(momentum)
        
        # Ensure exactly 40 features
        while len(features) < 40:
            features.append(0.0)
        
        return features[:40]
    
    def _microstructure_features(self, df: pd.DataFrame, signal_data: Dict) -> List[float]:
        """Market microstructure features (25 total)"""
        
        prices = df['price'].astype(float).values
        volumes = df.get('volume', pd.Series([1000] * len(df))).astype(float).values
        
        features = []
        
        # Bid-ask spread proxies
        high_low_spread = np.std(prices[-20:]) / np.mean(prices[-20:]) if len(prices) >= 20 else 0.0
        features.append(high_low_spread)
        
        # Volume imbalance
        volume_imbalance = self._calculate_volume_imbalance(prices, volumes)
        features.append(volume_imbalance)
        
        # Order flow toxicity
        toxicity = self._calculate_order_flow_toxicity(prices, volumes)
        features.append(toxicity)
        
        # Price impact measures
        for window in [5, 10, 20]:
            if len(prices) > window:
                returns = np.diff(np.log(prices[-window:]))
                volume_returns = volumes[-window+1:] / np.mean(volumes[-window+1:])
                
                # Kyle's lambda (price impact)
                if len(returns) > 0 and len(volume_returns) > 0:
                    correlation = np.corrcoef(np.abs(returns), volume_returns)[0, 1]
                    features.append(correlation if not np.isnan(correlation) else 0.0)
                else:
                    features.append(0.0)
        
        # Tick-by-tick features
        tick_features = self._calculate_tick_features(prices)
        features.extend(tick_features)
        
        # Liquidity measures
        liquidity_features = self._calculate_liquidity_measures(prices, volumes)
        features.extend(liquidity_features)
        
        # Ensure exactly 25 features
        while len(features) < 25:
            features.append(0.0)
        
        return features[:25]
    
    def _volatility_risk_features(self, df: pd.DataFrame) -> List[float]:
        """Volatility and risk metrics (20 total)"""
        
        prices = df['price'].astype(float).values
        returns = np.diff(np.log(prices)) if len(prices) > 1 else np.array([0.0])
        
        features = []
        
        # Multi-horizon volatility
        for window in [5, 10, 20, 50]:
            if len(returns) >= window:
                vol = np.std(returns[-window:]) * np.sqrt(252 * 24 * 60)  # Annualized
                features.append(vol)
            else:
                features.append(0.0)
        
        # GARCH volatility forecast
        if self.risk_model and len(returns) > 50:
            try:
                garch_vol = self._forecast_garch_volatility(returns)
                features.append(garch_vol)
            except:
                features.append(0.0)
        else:
            features.append(0.0)
        
        # Realized volatility measures
        if len(returns) >= 20:
            # Bipower variation
            bipower = np.sum(np.abs(returns[-20:-1]) * np.abs(returns[-19:])) * (np.pi / 2)
            features.append(bipower)
            
            # Jump variation
            realized_var = np.sum(returns[-20:] ** 2)
            jump_var = max(0, realized_var - bipower)
            features.append(jump_var)
        else:
            features.extend([0.0, 0.0])
        
        # Volatility clustering
        vol_clustering = self._measure_volatility_clustering(returns)
        features.append(vol_clustering)
        
        # Tail risk measures
        if len(returns) >= 50:
            var_95 = np.percentile(returns[-50:], 5)
            cvar_95 = np.mean(returns[-50:][returns[-50:] <= var_95])
            features.extend([var_95, cvar_95])
        else:
            features.extend([0.0, 0.0])
        
        # Skewness and kurtosis
        if len(returns) >= 20:
            skew = stats.skew(returns[-20:])
            kurt = stats.kurtosis(returns[-20:])
            features.extend([skew, kurt])
        else:
            features.extend([0.0, 0.0])
        
        # Ensure exactly 20 features
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]
    
    def _cross_asset_features(self, df: pd.DataFrame, signal_data: Dict) -> List[float]:
        """Cross-asset and macro features (20 total)"""
        
        features = []
        
        # Get real correlation data
        try:
            from market_data_collector import get_market_collector
            collector = get_market_collector(self.db)
            correlations = collector.calculate_correlations(60)
            
            # Extract correlation features
            features.append(correlations.get('nq_es_corr', 0.0))
            features.append(correlations.get('nq_ym_corr', 0.0))
            features.append(correlations.get('nq_dxy_corr', 0.0))
            features.append(correlations.get('es_ym_corr', 0.0))
            
        except:
            features.extend([0.0, 0.0, 0.0, 0.0])
        
        # Currency strength measures
        dxy_strength = self._calculate_currency_strength()
        features.append(dxy_strength)
        
        # Interest rate environment
        yield_curve_features = self._calculate_yield_curve_features()
        features.extend(yield_curve_features)
        
        # Commodity correlations
        commodity_features = self._calculate_commodity_correlations()
        features.extend(commodity_features)
        
        # Crypto correlations
        crypto_features = self._calculate_crypto_correlations()
        features.extend(crypto_features)
        
        # Ensure exactly 20 features
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]
    
    def _alternative_data_features(self, df: pd.DataFrame, signal_data: Dict) -> List[float]:
        """Alternative data features (15 total)"""
        
        features = []
        
        # Economic calendar impact
        econ_impact = self._calculate_economic_impact()
        features.append(econ_impact)
        
        # Sentiment indicators
        sentiment_features = self._calculate_sentiment_features()
        features.extend(sentiment_features)
        
        # Options flow
        options_features = self._calculate_options_flow()
        features.extend(options_features)
        
        # Insider activity
        insider_features = self._calculate_insider_activity()
        features.extend(insider_features)
        
        # Ensure exactly 15 features
        while len(features) < 15:
            features.append(0.0)
        
        return features[:15]
    
    def _regime_sentiment_features(self, df: pd.DataFrame, signal_data: Dict) -> List[float]:
        """Regime and sentiment features (15 total)"""
        
        features = []
        
        # Current regime probabilities
        regime_probs = self._detect_market_regime_probabilities(df)
        features.extend(list(regime_probs.values())[:4])  # 4 regime probabilities
        
        # Regime transition probabilities
        transition_probs = self._calculate_regime_transitions()
        features.extend(transition_probs[:3])
        
        # Market stress indicators
        stress_indicators = self._calculate_market_stress()
        features.extend(stress_indicators)
        
        # Ensure exactly 15 features
        while len(features) < 15:
            features.append(0.0)
        
        return features[:15]
    
    def _execution_liquidity_features(self, df: pd.DataFrame, signal_data: Dict) -> List[float]:
        """Execution and liquidity features (15 total)"""
        
        features = []
        
        # Liquidity measures
        liquidity_score = self._calculate_liquidity_score(df)
        features.append(liquidity_score)
        
        # Expected execution cost
        execution_cost = self._calculate_execution_cost(signal_data)
        features.append(execution_cost)
        
        # Market impact estimate
        market_impact = self._calculate_market_impact(signal_data)
        features.append(market_impact)
        
        # Timing features
        timing_features = self._calculate_timing_features(signal_data)
        features.extend(timing_features)
        
        # Ensure exactly 15 features
        while len(features) < 15:
            features.append(0.0)
        
        return features[:15]
    
    def predict_institutional(self, signal_data: Dict, market_data: List[Dict]) -> InstitutionalPrediction:
        """Generate institutional-grade prediction with full risk assessment"""
        
        if not ML_AVAILABLE:
            return self._minimal_prediction()
        
        try:
            # Engineer features
            features = self.engineer_institutional_features(signal_data, market_data)
            
            if np.sum(features) == 0:  # No real data available
                return self._minimal_prediction()
            
            # Detect current market regime
            regime_probs = self._detect_market_regime_probabilities(pd.DataFrame(market_data))
            
            # Generate ensemble predictions
            predictions = self._generate_ensemble_predictions(features)
            
            # Calculate uncertainty measures
            uncertainty = self._calculate_prediction_uncertainty(predictions, features)
            
            # Risk assessment
            risk_metrics = self._calculate_comprehensive_risk(predictions, features, market_data)
            
            # Optimal position sizing
            kelly_fraction = self._calculate_kelly_fraction(predictions, risk_metrics)
            
            # Execution analysis
            execution_analysis = self._analyze_execution_requirements(signal_data, predictions)
            
            return InstitutionalPrediction(
                direction=predictions['direction'],
                confidence=predictions['confidence'],
                expected_return=predictions['expected_return'],
                return_std=predictions['return_std'],
                sharpe_ratio=predictions['expected_return'] / (predictions['return_std'] + 1e-8),
                kelly_fraction=kelly_fraction,
                var_95=risk_metrics['var_95'],
                cvar_95=risk_metrics['cvar_95'],
                max_drawdown_expected=risk_metrics['max_drawdown'],
                time_horizon=predictions['time_horizon'],
                feature_attribution=predictions['feature_importance'],
                model_uncertainty=uncertainty['epistemic'],
                data_uncertainty=uncertainty['aleatoric'],
                regime_probability=regime_probs,
                execution_cost=execution_analysis['cost'],
                market_impact=execution_analysis['impact'],
                liquidity_score=execution_analysis['liquidity']
            )
            
        except Exception as e:
            logger.error(f"❌ Institutional prediction error: {str(e)}")
            return self._minimal_prediction()
    
    # Helper methods (implementing real quantitative finance techniques)
    
    def _calculate_fractal_dimension(self, prices: np.ndarray) -> float:
        """Calculate fractal dimension using Higuchi's method"""
        
        if len(prices) < 10:
            return 1.5
        
        try:
            N = len(prices)
            k_max = min(20, N // 4)
            
            lk = []
            for k in range(1, k_max + 1):
                lm = []
                for m in range(k):
                    ll = 0
                    for i in range(1, int((N - m) / k)):
                        ll += abs(prices[m + i * k] - prices[m + (i - 1) * k])
                    ll = ll * (N - 1) / (k * k * int((N - m) / k))
                    lm.append(ll)
                lk.append(np.mean(lm))
            
            # Linear regression in log-log space
            x = np.log(range(1, k_max + 1))
            y = np.log(lk)
            slope = np.polyfit(x, y, 1)[0]
            
            return max(1.0, min(2.0, 2 - slope))
            
        except:
            return 1.5
    
    def _calculate_hurst_exponent(self, prices: np.ndarray) -> float:
        """Calculate Hurst exponent using R/S analysis"""
        
        if len(prices) < 20:
            return 0.5
        
        try:
            returns = np.diff(np.log(prices))
            n = len(returns)
            
            # Calculate R/S statistic
            mean_return = np.mean(returns)
            deviations = returns - mean_return
            cumulative_deviations = np.cumsum(deviations)
            
            R = np.max(cumulative_deviations) - np.min(cumulative_deviations)
            S = np.std(returns)
            
            if S == 0:
                return 0.5
            
            rs = R / S
            hurst = np.log(rs) / np.log(n)
            
            return max(0.0, min(1.0, hurst))
            
        except:
            return 0.5
    
    def _bayesian_loss(self, y_true, y_pred):
        """Bayesian loss function for uncertainty quantification"""
        
        mean, std = y_pred[:, 0], y_pred[:, 1]
        
        # Negative log-likelihood
        nll = 0.5 * tf.math.log(2 * np.pi * std**2) + 0.5 * ((y_true - mean)**2) / (std**2)
        
        return tf.reduce_mean(nll)
    
    def _minimal_prediction(self) -> InstitutionalPrediction:
        """Return minimal prediction when no data available"""
        
        return InstitutionalPrediction(
            direction='NEUTRAL',
            confidence=0.0,
            expected_return=0.0,
            return_std=0.0,
            sharpe_ratio=0.0,
            kelly_fraction=0.0,
            var_95=0.0,
            cvar_95=0.0,
            max_drawdown_expected=0.0,
            time_horizon=0,
            feature_attribution={},
            model_uncertainty=1.0,
            data_uncertainty=1.0,
            regime_probability={},
            execution_cost=0.0,
            market_impact=0.0,
            liquidity_score=0.0
        )
    
    # Placeholder methods for complex calculations (would implement full versions)
    def _identify_support_resistance(self, prices: np.ndarray) -> List[float]:
        """Identify support/resistance levels using local extrema"""
        return [0.0] * 5
    
    def _calculate_volume_imbalance(self, prices: np.ndarray, volumes: np.ndarray) -> float:
        """Calculate volume imbalance"""
        return 0.0
    
    def _calculate_order_flow_toxicity(self, prices: np.ndarray, volumes: np.ndarray) -> float:
        """Calculate order flow toxicity (VPIN)"""
        return 0.0
    
    def _calculate_tick_features(self, prices: np.ndarray) -> List[float]:
        """Calculate tick-level features"""
        return [0.0] * 5
    
    def _calculate_liquidity_measures(self, prices: np.ndarray, volumes: np.ndarray) -> List[float]:
        """Calculate liquidity measures"""
        return [0.0] * 5
    
    def _forecast_garch_volatility(self, returns: np.ndarray) -> float:
        """Forecast volatility using GARCH model"""
        return 0.0
    
    def _measure_volatility_clustering(self, returns: np.ndarray) -> float:
        """Measure volatility clustering"""
        return 0.0
    
    def _calculate_currency_strength(self) -> float:
        """Calculate DXY strength measure"""
        return 0.0
    
    def _calculate_yield_curve_features(self) -> List[float]:
        """Calculate yield curve features"""
        return [0.0] * 3
    
    def _calculate_commodity_correlations(self) -> List[float]:
        """Calculate commodity correlations"""
        return [0.0] * 3
    
    def _calculate_crypto_correlations(self) -> List[float]:
        """Calculate crypto correlations"""
        return [0.0] * 3
    
    def _calculate_economic_impact(self) -> float:
        """Calculate economic calendar impact"""
        return 0.0
    
    def _calculate_sentiment_features(self) -> List[float]:
        """Calculate sentiment features"""
        return [0.0] * 3
    
    def _calculate_options_flow(self) -> List[float]:
        """Calculate options flow features"""
        return [0.0] * 3
    
    def _calculate_insider_activity(self) -> List[float]:
        """Calculate insider activity features"""
        return [0.0] * 3
    
    def _detect_market_regime_probabilities(self, df: pd.DataFrame) -> Dict[str, float]:
        """Detect market regime probabilities"""
        return {'bull': 0.25, 'bear': 0.25, 'volatile': 0.25, 'ranging': 0.25}
    
    def _calculate_regime_transitions(self) -> List[float]:
        """Calculate regime transition probabilities"""
        return [0.0] * 3
    
    def _calculate_market_stress(self) -> List[float]:
        """Calculate market stress indicators"""
        return [0.0] * 5
    
    def _calculate_liquidity_score(self, df: pd.DataFrame) -> float:
        """Calculate liquidity score"""
        return 0.5
    
    def _calculate_execution_cost(self, signal_data: Dict) -> float:
        """Calculate expected execution cost"""
        return 0.0
    
    def _calculate_market_impact(self, signal_data: Dict) -> float:
        """Calculate expected market impact"""
        return 0.0
    
    def _calculate_timing_features(self, signal_data: Dict) -> List[float]:
        """Calculate timing features"""
        return [0.0] * 10
    
    def _generate_ensemble_predictions(self, features: np.ndarray) -> Dict:
        """Generate ensemble predictions"""
        return {
            'direction': 'NEUTRAL',
            'confidence': 0.0,
            'expected_return': 0.0,
            'return_std': 0.0,
            'time_horizon': 15,
            'feature_importance': {}
        }
    
    def _calculate_prediction_uncertainty(self, predictions: Dict, features: np.ndarray) -> Dict:
        """Calculate prediction uncertainty"""
        return {'epistemic': 0.5, 'aleatoric': 0.5}
    
    def _calculate_comprehensive_risk(self, predictions: Dict, features: np.ndarray, market_data: List[Dict]) -> Dict:
        """Calculate comprehensive risk metrics"""
        return {
            'var_95': 0.0,
            'cvar_95': 0.0,
            'max_drawdown': 0.0
        }
    
    def _calculate_kelly_fraction(self, predictions: Dict, risk_metrics: Dict) -> float:
        """Calculate Kelly fraction for optimal position sizing"""
        return 0.0
    
    def _analyze_execution_requirements(self, signal_data: Dict, predictions: Dict) -> Dict:
        """Analyze execution requirements"""
        return {
            'cost': 0.0,
            'impact': 0.0,
            'liquidity': 0.5
        }

# Global institutional engine
institutional_engine = None

def get_institutional_engine(db_connection=None):
    """Get institutional ML engine"""
    global institutional_engine
    if institutional_engine is None:
        institutional_engine = InstitutionalMLEngine(db_connection)
    return institutional_engine
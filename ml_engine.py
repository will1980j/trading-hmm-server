import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta

class TradingMLEngine:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, signals):
        """Convert signals to ML features"""
        df = pd.DataFrame(signals)
        
        # Technical features
        df['price_change'] = df['price'].pct_change()
        df['strength_ma'] = df['strength'].rolling(5).mean()
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(10).mean()
        
        # Time features
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        
        # Signal type encoding
        df['is_fvg'] = df['signal_type'].str.contains('FVG').astype(int)
        df['is_bullish'] = (df['bias'] == 'Bullish').astype(int)
        
        # Pattern features
        df['consecutive_same_bias'] = (df['bias'] == df['bias'].shift()).cumsum()
        
        return df[['price_change', 'strength', 'strength_ma', 'volume_ratio', 
                  'hour', 'day_of_week', 'is_fvg', 'is_bullish', 'consecutive_same_bias']].fillna(0)
    
    def create_labels(self, signals):
        """Create prediction labels (next signal success)"""
        df = pd.DataFrame(signals)
        # Predict if next signal will be profitable (strength > 70)
        return (df['strength'].shift(-1) > 70).astype(int).fillna(0)
    
    def train(self, signals):
        """Train ML model on historical signals"""
        if len(signals) < 50:
            return False
            
        features = self.prepare_features(signals)
        labels = self.create_labels(signals)
        
        # Remove last row (no future label)
        features = features[:-1]
        labels = labels[:-1]
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(features_scaled, labels)
        self.is_trained = True
        
        # Save model
        joblib.dump(self.model, 'trading_model.pkl')
        joblib.dump(self.scaler, 'scaler.pkl')
        
        return True
    
    def predict_signal_quality(self, recent_signals, new_signal):
        """Predict if new signal will be successful"""
        if not self.is_trained:
            return 0.5  # Neutral prediction
            
        # Combine recent signals with new signal
        all_signals = recent_signals + [new_signal]
        features = self.prepare_features(all_signals)
        
        # Get features for new signal (last row)
        new_features = features.iloc[-1:].values
        new_features_scaled = self.scaler.transform(new_features)
        
        # Predict probability
        probability = self.model.predict_proba(new_features_scaled)[0][1]
        return probability
    
    def get_feature_importance(self):
        """Get which features matter most"""
        if not self.is_trained:
            return {}
            
        features = ['price_change', 'strength', 'strength_ma', 'volume_ratio', 
                   'hour', 'day_of_week', 'is_fvg', 'is_bullish', 'consecutive_same_bias']
        
        importance = dict(zip(features, self.model.feature_importances_))
        return sorted(importance.items(), key=lambda x: x[1], reverse=True)

# Global ML engine
ml_engine = TradingMLEngine()
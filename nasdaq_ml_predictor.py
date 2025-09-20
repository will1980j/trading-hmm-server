import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class NasdaqMLPredictor:
    def __init__(self):
        self.models = {
            'rf': RandomForestRegressor(n_estimators=500, min_samples_split=50, random_state=42),
            'gb': GradientBoostingRegressor(n_estimators=500, min_samples_split=50, random_state=42)
        }
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def create_features(self, df):
        """Create advanced technical features from OHLCV data"""
        df = df.copy()
        
        # Price features
        df['price_range'] = df['High'] - df['Low']
        df['body_size'] = abs(df['Close'] - df['Open'])
        df['upper_shadow'] = df['High'] - df[['Open', 'Close']].max(axis=1)
        df['lower_shadow'] = df[['Open', 'Close']].min(axis=1) - df['Low']
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['Close'].rolling(period).mean()
            df[f'price_vs_sma_{period}'] = df['Close'] / df[f'sma_{period}'] - 1
            
        # Volatility
        df['volatility_5'] = df['Close'].rolling(5).std()
        df['volatility_20'] = df['Close'].rolling(20).std()
        
        # Volume features
        df['volume_sma_10'] = df['Volume'].rolling(10).mean()
        df['volume_ratio'] = df['Volume'] / df['volume_sma_10']
        
        # Price momentum
        for period in [1, 3, 5, 10]:
            df[f'return_{period}d'] = df['Close'].pct_change(period)
            
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df.dropna()
    
    def prepare_data(self, symbol='QQQ', period='5y'):
        """Download and prepare NASDAQ data"""
        import requests
        
        # Try Alpha Vantage first (free tier)
        try:
            import os
            api_key = os.environ.get('ALPHA_VANTAGE_KEY', '3GX5OV6NVBXUB01E')
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                import pandas as pd
                ts_data = data['Time Series (Daily)']
                df = pd.DataFrame({
                    'Open': [float(ts_data[date]['1. open']) for date in ts_data],
                    'High': [float(ts_data[date]['2. high']) for date in ts_data], 
                    'Low': [float(ts_data[date]['3. low']) for date in ts_data],
                    'Close': [float(ts_data[date]['4. close']) for date in ts_data],
                    'Volume': [int(ts_data[date]['5. volume']) for date in ts_data]
                }, index=pd.to_datetime(list(ts_data.keys())))
                df = df.sort_index()
                print(f"Downloaded {len(df)} rows from Alpha Vantage for {symbol}")
            else:
                raise Exception(f"Alpha Vantage error: {data.get('Error Message', 'Unknown error')}")
        except Exception as e:
            print(f"Alpha Vantage failed: {e}")
            # Fallback to yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            print(f"Downloaded {len(df)} rows from yfinance for {symbol}")
        
        if len(df) == 0:
            raise ValueError(f"No data downloaded for {symbol}")
        
        df = self.create_features(df)
        
        # Target: next day's return
        df['target'] = df['Close'].shift(-1) / df['Close'] - 1
        df = df.dropna()
        
        feature_cols = [col for col in df.columns if col not in ['target', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        X = df[feature_cols]
        y = df['target']
        
        return X, y, df
    
    def train(self, symbol='QQQ'):
        """Train the ML models"""
        X, y, df = self.prepare_data(symbol)
        
        if len(X) < 50:
            raise ValueError("Insufficient data for training")
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        for name, model in self.models.items():
            model.fit(X_train_scaled, y_train)
            
            train_pred = model.predict(X_train_scaled)
            test_pred = model.predict(X_test_scaled)
            
            results[name] = {
                'train_r2': r2_score(y_train, train_pred),
                'test_r2': r2_score(y_test, test_pred),
                'test_mae': mean_absolute_error(y_test, test_pred)
            }
        
        self.is_trained = True
        self.feature_names = X.columns.tolist()
        
        return results
    
    def predict_with_confidence(self, symbol='QQQ'):
        """Make prediction with confidence threshold"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
            
        # Get latest data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='1y')
        df = self.create_features(df)
        
        # Get latest features
        latest_features = df[self.feature_names].iloc[-1:].values
        latest_scaled = self.scaler.transform(latest_features)
        
        # Get predictions from both models
        predictions = {}
        for name, model in self.models.items():
            pred = model.predict(latest_scaled)[0]
            predictions[name] = pred
            
        # Calculate ensemble prediction and confidence
        pred_values = list(predictions.values())
        ensemble_pred = np.mean(pred_values)
        pred_std = np.std(pred_values)
        
        # Confidence based on model agreement (lower std = higher confidence)
        max_std = 0.02  # 2% max disagreement for 100% confidence
        confidence = max(0, min(100, 100 * (1 - pred_std / max_std)))
        
        return {
            'prediction': ensemble_pred,
            'confidence': confidence,
            'individual_predictions': predictions,
            'should_trade': confidence >= 60.0,
            'direction': 'UP' if ensemble_pred > 0 else 'DOWN',
            'magnitude': abs(ensemble_pred)
        }

# Usage example
if __name__ == "__main__":
    predictor = NasdaqMLPredictor()
    
    print("Training NASDAQ ML Predictor...")
    results = predictor.train('QQQ')
    
    print("\nModel Performance:")
    for model, metrics in results.items():
        print(f"{model.upper()}: R² = {metrics['test_r2']:.3f}, MAE = {metrics['test_mae']:.4f}")
    
    print("\nGetting prediction...")
    prediction = predictor.predict_with_confidence('QQQ')
    
    print(f"Prediction: {prediction['prediction']:.4f} ({prediction['direction']})")
    print(f"Confidence: {prediction['confidence']:.1f}%")
    print(f"Should Trade: {prediction['should_trade']}")
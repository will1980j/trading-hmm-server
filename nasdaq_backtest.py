import yfinance as yf
import pandas as pd
import numpy as np
from nasdaq_ml_predictor import NasdaqMLPredictor
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class NasdaqBacktester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.predictor = NasdaqMLPredictor()
        
    def backtest(self, symbol='QQQ', start_date='2004-01-01', confidence_threshold=60):
        """Backtest the ML model over 20 years"""
        
        # Download full dataset using Alpha Vantage
        import requests
        import os
        
        try:
            api_key = os.environ.get('ALPHA_VANTAGE_KEY', '3GX5OV6NVBXUB01E')
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                ts_data = data['Time Series (Daily)']
                df = pd.DataFrame({
                    'Open': [float(ts_data[date]['1. open']) for date in ts_data],
                    'High': [float(ts_data[date]['2. high']) for date in ts_data], 
                    'Low': [float(ts_data[date]['3. low']) for date in ts_data],
                    'Close': [float(ts_data[date]['4. close']) for date in ts_data],
                    'Volume': [int(ts_data[date]['5. volume']) for date in ts_data]
                }, index=pd.to_datetime(list(ts_data.keys())))
                df = df.sort_index()
                print(f"Downloaded {len(df)} rows from Alpha Vantage for backtest")
            else:
                raise Exception(f"Alpha Vantage error: {data.get('Error Message', 'Unknown error')}")
        except Exception as e:
            print(f"Alpha Vantage failed: {e}, falling back to yfinance")
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=datetime.now().strftime('%Y-%m-%d'))
            print(f"Downloaded {len(df)} rows from yfinance for backtest")
        
        if len(df) < 200:
            raise ValueError("Insufficient historical data")
            
        # Split into training and testing periods
        train_size = int(len(df) * 0.3)  # Use first 30% for initial training
        
        results = []
        capital = self.initial_capital
        position = 0
        trades = 0
        winning_trades = 0
        
        print(f"Backtesting {symbol} from {start_date} with {len(df)} days of data...")
        
        # Walk-forward analysis
        for i in range(train_size, len(df) - 1):
            try:
                # Use expanding window for training
                train_data = df.iloc[:i]
                
                # Retrain model every 30 days
                if i % 30 == 0 or i == train_size:
                    print(f"Retraining model at day {i}...")
                    self.predictor = NasdaqMLPredictor()
                    
                    # Prepare training data
                    train_features = self.predictor.create_features(train_data)
                    train_features['target'] = train_features['Close'].shift(-1) / train_features['Close'] - 1
                    train_features = train_features.dropna()
                    
                    if len(train_features) < 50:
                        continue
                        
                    feature_cols = [col for col in train_features.columns if col not in ['target', 'Open', 'High', 'Low', 'Close', 'Volume']]
                    X_train = train_features[feature_cols]
                    y_train = train_features['target']
                    
                    # Train models
                    X_train_scaled = self.predictor.scaler.fit_transform(X_train)
                    for name, model in self.predictor.models.items():
                        model.fit(X_train_scaled, y_train)
                    
                    self.predictor.is_trained = True
                    self.predictor.feature_names = X_train.columns.tolist()
                
                if not self.predictor.is_trained:
                    continue
                    
                # Make prediction for next day
                current_data = df.iloc[:i+1]
                features_df = self.predictor.create_features(current_data)
                
                if len(features_df) == 0:
                    continue
                    
                latest_features = features_df[self.predictor.feature_names].iloc[-1:].values
                latest_scaled = self.predictor.scaler.transform(latest_features)
                
                # Get predictions
                predictions = {}
                for name, model in self.predictor.models.items():
                    pred = model.predict(latest_scaled)[0]
                    predictions[name] = pred
                
                ensemble_pred = np.mean(list(predictions.values()))
                pred_std = np.std(list(predictions.values()))
                confidence = max(0, min(100, 100 * (1 - pred_std / 0.02)))
                
                # Trading logic
                current_price = df.iloc[i]['Close']
                next_price = df.iloc[i+1]['Close']
                actual_return = (next_price - current_price) / current_price
                
                trade_made = False
                if confidence >= confidence_threshold:
                    trades += 1
                    trade_made = True
                    
                    if ensemble_pred > 0:  # Buy signal
                        position = capital / current_price
                        capital = 0
                    else:  # Sell signal (short)
                        if position > 0:
                            capital = position * current_price
                            position = 0
                    
                    # Calculate P&L
                    if ensemble_pred > 0 and actual_return > 0:
                        winning_trades += 1
                    elif ensemble_pred < 0 and actual_return < 0:
                        winning_trades += 1
                
                # Update portfolio value
                portfolio_value = capital + (position * current_price if position > 0 else 0)
                
                results.append({
                    'date': df.index[i],
                    'price': current_price,
                    'prediction': ensemble_pred,
                    'confidence': confidence,
                    'actual_return': actual_return,
                    'trade_made': trade_made,
                    'portfolio_value': portfolio_value,
                    'position': position,
                    'capital': capital
                })
                
            except Exception as e:
                print(f"Error at day {i}: {e}")
                continue
        
        # Final portfolio value
        final_price = df.iloc[-1]['Close']
        final_value = capital + (position * final_price if position > 0 else 0)
        
        # Calculate metrics
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        buy_hold_return = (final_price - df.iloc[train_size]['Close']) / df.iloc[train_size]['Close'] * 100
        win_rate = (winning_trades / trades * 100) if trades > 0 else 0
        
        results_df = pd.DataFrame(results)
        
        return {
            'results': results_df,
            'metrics': {
                'total_return': total_return,
                'buy_hold_return': buy_hold_return,
                'final_value': final_value,
                'total_trades': trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'confidence_threshold': confidence_threshold,
                'backtest_period': f"{start_date} to {datetime.now().strftime('%Y-%m-%d')}"
            }
        }
    
    def plot_results(self, backtest_results):
        """Plot backtest results"""
        results_df = backtest_results['results']
        metrics = backtest_results['metrics']
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
        
        # Portfolio value vs Buy & Hold
        ax1.plot(results_df['date'], results_df['portfolio_value'], label='ML Strategy', linewidth=2)
        initial_price = results_df['price'].iloc[0]
        buy_hold_values = (results_df['price'] / initial_price) * self.initial_capital
        ax1.plot(results_df['date'], buy_hold_values, label='Buy & Hold', linewidth=2)
        ax1.set_title(f"Portfolio Performance - ML: {metrics['total_return']:.1f}% vs B&H: {metrics['buy_hold_return']:.1f}%")
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True)
        
        # Predictions vs Actual
        trade_dates = results_df[results_df['trade_made']]['date']
        trade_predictions = results_df[results_df['trade_made']]['prediction']
        trade_actuals = results_df[results_df['trade_made']]['actual_return']
        
        ax2.scatter(trade_predictions, trade_actuals, alpha=0.6)
        ax2.plot([-0.05, 0.05], [-0.05, 0.05], 'r--', label='Perfect Prediction')
        ax2.set_xlabel('Predicted Return')
        ax2.set_ylabel('Actual Return')
        ax2.set_title(f'Prediction Accuracy - {metrics["total_trades"]} trades, {metrics["win_rate"]:.1f}% win rate')
        ax2.legend()
        ax2.grid(True)
        
        # Confidence distribution
        ax3.hist(results_df['confidence'], bins=50, alpha=0.7)
        ax3.axvline(x=metrics['confidence_threshold'], color='r', linestyle='--', label=f'Threshold: {metrics["confidence_threshold"]}%')
        ax3.set_xlabel('Prediction Confidence (%)')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Confidence Distribution')
        ax3.legend()
        ax3.grid(True)
        
        plt.tight_layout()
        plt.show()
        
        return fig

# Run backtest
if __name__ == "__main__":
    backtester = NasdaqBacktester(initial_capital=10000)
    
    print("Starting 20-year backtest...")
    results = backtester.backtest('QQQ', start_date='2004-01-01', confidence_threshold=60)
    
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    for key, value in results['metrics'].items():
        print(f"{key}: {value}")
    
    # Plot results
    backtester.plot_results(results)
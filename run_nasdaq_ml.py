from nasdaq_ml_predictor import NasdaqMLPredictor
from nasdaq_backtest import NasdaqBacktester

# 1. BACKTEST THE MODEL (20 years)
print("=== RUNNING 20-YEAR BACKTEST ===")
backtester = NasdaqBacktester(initial_capital=10000)
backtest_results = backtester.backtest('QQQ', start_date='2004-01-01', confidence_threshold=60)

print("\nBacktest Results:")
for key, value in backtest_results['metrics'].items():
    print(f"{key}: {value}")

# Plot results
backtester.plot_results(backtest_results)

# 2. TRAIN LIVE MODEL
print("\n=== TRAINING LIVE MODEL ===")
predictor = NasdaqMLPredictor()
training_results = predictor.train('QQQ')

print("\nModel Performance:")
for model, metrics in training_results.items():
    print(f"{model.upper()}: R² = {metrics['test_r2']:.3f}, MAE = {metrics['test_mae']:.4f}")

# 3. GET TODAY'S PREDICTION
print("\n=== TODAY'S PREDICTION ===")
prediction = predictor.predict_with_confidence('QQQ')

print(f"Direction: {prediction['direction']}")
print(f"Magnitude: {prediction['magnitude']:.4f}")
print(f"Confidence: {prediction['confidence']:.1f}%")
print(f"Should Trade: {prediction['should_trade']}")

if prediction['should_trade']:
    print(f"🚀 HIGH CONFIDENCE SIGNAL: {prediction['direction']} with {prediction['confidence']:.1f}% confidence")
else:
    print(f"⚠️ Low confidence ({prediction['confidence']:.1f}%) - No trade recommended")
# ML Hyperparameter Optimization Guide

## Overview
Automated hyperparameter tuning for Random Forest + Gradient Boosting ensemble models used in NASDAQ day trading signal prediction.

## Features

### 1. GridSearchCV with Time Series Cross-Validation
- **5-fold time series splits** - Respects temporal order of trading data
- **Prevents data leakage** - Future data never used to predict past

### 2. Hyperparameter Search Space

**Random Forest:**
- `n_estimators`: [100, 150, 200]
- `max_depth`: [5, 7, 10]
- `min_samples_split`: [2, 5]
- `min_samples_leaf`: [1, 2]
- `max_features`: ['sqrt', 'log2']

**Gradient Boosting:**
- `n_estimators`: [100, 150, 200]
- `max_depth`: [3, 5, 7]
- `learning_rate`: [0.01, 0.05, 0.1]
- `subsample`: [0.8, 1.0]
- `min_samples_split`: [2, 5]
- **Early stopping**: Stops if no improvement for 10 iterations

### 3. Multi-Metric Evaluation
- **Accuracy** - Overall correctness
- **Precision** - Avoid false signals
- **Recall** - Catch all opportunities
- **F1-Score** - Balance precision/recall
- **Profit Score** - Custom metric: +2R on correct, -1R on wrong

### 4. Baseline Comparison
Compares optimized models against current baseline:
- Baseline: n_estimators=100, max_depth=5
- Reports improvement in accuracy and profit

### 5. Model Persistence
- Saves best models with `joblib`
- Timestamped filenames for version control
- Ready for production deployment

## Usage

### Via ML Dashboard UI
1. Navigate to ML Intelligence Hub
2. Click "🔧 Optimize Hyperparameters" button
3. Wait 2-5 minutes for optimization
4. View improvement results

### Via API
```bash
curl -X POST https://web-production-cd33.up.railway.app/api/ml-optimize
```

### Programmatically
```python
from ml_hyperparameter_optimizer import optimize_trading_models

results = optimize_trading_models(db)

print(f"RF Improvement: {results['comparison']['rf_improvement']['accuracy']:.2f}%")
print(f"GB Improvement: {results['comparison']['gb_improvement']['accuracy']:.2f}%")
print(f"Best RF params: {results['rf_optimization']['best_params']}")
print(f"Best GB params: {results['gb_optimization']['best_params']}")
```

## Expected Results

### Current Performance
- Accuracy: 89.1%
- n_estimators: 100
- max_depth: 5

### Expected After Optimization
- Accuracy: 91-93% (+2-4%)
- Optimized n_estimators: ~150-200
- Optimized max_depth: ~7
- Improved profit score

## Optimization Process

1. **Data Preparation** (30s)
   - Load 1,898+ historical trades
   - Extract features (session, bias, VIX, etc.)
   - Split 80/20 train/test (time-based)

2. **Random Forest Optimization** (1-2 min)
   - Test 48 parameter combinations
   - 5-fold time series CV per combination
   - Select best based on profit score

3. **Gradient Boosting Optimization** (2-3 min)
   - Test 90 parameter combinations
   - Early stopping prevents overfitting
   - 5-fold time series CV per combination

4. **Baseline Comparison** (10s)
   - Train baseline models
   - Compare all metrics
   - Calculate improvements

5. **Model Saving** (5s)
   - Save optimized models
   - Generate timestamped filenames

## When to Run Optimization

- **After 100+ new trades** - More data = better optimization
- **Monthly** - Market conditions change
- **After accuracy drops** - Model may need retuning
- **Before major trading events** - Ensure peak performance

## Monitoring

Check optimization results:
```python
# View detailed CV results
rf_cv = results['rf_optimization']['cv_results']
print(rf_cv[['params', 'mean_test_profit', 'mean_test_accuracy']])

# View best parameters
print(results['rf_optimization']['best_params'])
print(results['gb_optimization']['best_params'])
```

## Production Deployment

After optimization, deploy best models:
```python
from ml_hyperparameter_optimizer import MLHyperparameterOptimizer

optimizer = MLHyperparameterOptimizer(db)
# ... run optimization ...

# Save for production
paths = optimizer.save_models('models/production')
print(f"Deploy these models: {paths}")
```

## Notes

- **Time Complexity**: O(n_params × n_folds × n_samples)
- **Memory**: ~500MB for 1,898 samples
- **CPU**: Uses all cores (`n_jobs=-1`)
- **Reproducible**: `random_state=42` for consistency

## Troubleshooting

**"Insufficient training data"**
- Need at least 100 trades with MFE data
- Current: 1,898+ trades ✅

**"Optimization taking too long"**
- Reduce parameter grid size
- Decrease n_splits from 5 to 3
- Use fewer n_estimators options

**"No improvement over baseline"**
- Baseline may already be optimal
- Try different parameter ranges
- Check for overfitting in CV results

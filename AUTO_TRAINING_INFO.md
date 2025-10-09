# ML Auto-Training - Fully Automated

## How It Works

The ML system **trains itself automatically**. You don't need to do anything!

### Auto-Training Triggers

ML retrains when:

1. **First Signal** - Trains on first prediction if not trained
2. **Every 24 Hours** - Retrains daily to stay current
3. **Every 50 New Trades** - Retrains when you add significant data
4. **Background Check** - Checks every hour if retraining needed

### What Happens

```
Hour 1:  ML checks → No retrain needed
Hour 2:  ML checks → No retrain needed
...
Hour 24: ML checks → 24 hours passed → Auto-retrains
Hour 25: ML checks → No retrain needed
...
```

Or:

```
Trade 1-50:   ML trained
Trade 51-100: ML checks → 50 new trades → Auto-retrains
Trade 101-150: ML checks → 50 new trades → Auto-retrains
```

### You See This in Logs

```
🔄 Auto-training ML models...
✅ Auto-trainer: Training complete - 326 samples, 73.2% accuracy
```

Or:

```
⏰ Auto-retrain: 24.3 hours since last training
🔄 Auto-training ML models...
✅ Training complete
```

Or:

```
📊 Auto-retrain: 52 new trades since last training
🔄 Auto-training ML models...
✅ Training complete
```

## Manual Training (Optional)

You can still manually train via:
- Dashboard: Click "Train ML Models"
- API: `POST /api/ml-train`

But you don't need to! ML manages itself.

## Benefits

✅ **Always Current** - ML learns from latest data
✅ **Zero Maintenance** - No manual retraining needed
✅ **Continuous Improvement** - Gets better as you trade
✅ **Smart Scheduling** - Only retrains when beneficial

## Configuration (Optional)

Default settings (in `unified_ml_intelligence.py`):
```python
self.auto_retrain_threshold = 50  # Retrain every 50 new trades
```

Change to retrain more/less often:
```python
self.auto_retrain_threshold = 25   # More frequent
self.auto_retrain_threshold = 100  # Less frequent
```

## Performance Impact

- Training time: 10-30 seconds
- Happens in background
- Doesn't affect live predictions
- Railway handles it easily

## That's It!

ML trains itself. You just trade and it learns! 🤖

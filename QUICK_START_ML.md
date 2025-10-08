# Quick Start: ML Confidence in Trades

## ✅ You Already Have It!

ML confidence is **already integrated** and working in your system.

## 🎯 Where to See ML Confidence

### 1. Execution Dashboard (Updated Today)
**URL**: `http://your-server/1m-execution`

Shows for each signal:
```
🤖 ML: 2.35R (85% confidence)
```

Color coding:
- 🟢 Green: >70% confidence (take trade)
- 🟠 Orange: 50-70% confidence (caution)
- 🔴 Red: <50% confidence (skip)

### 2. API Endpoint
```bash
POST /api/ml-predict
{
  "bias": "Bullish",
  "session": "NY AM",
  "price": 15000,
  "market_context": {...}
}
```

### 3. Signal Lab Dashboard
**URL**: `http://your-server/signal-lab-dashboard`

Scroll to "ML Intelligence Dashboard" section.

## 🚀 First Time Setup

### Step 1: Add Training Data
1. Go to Signal Lab (`/signal-analysis-lab`)
2. Add at least 30 trades with MFE data
3. Make sure MFE values are filled in

### Step 2: Train Models
1. Go to Signal Lab Dashboard
2. Find "ML Intelligence Dashboard"
3. Click "Train Models" button
4. Wait 30 seconds for training

### Step 3: View Predictions
1. Go to 1M Execution Dashboard
2. Wait for new signals
3. ML confidence displays automatically

## 📊 What ML Predicts

- **Predicted MFE**: Expected profit in R
- **Confidence**: Model certainty (0-100%)
- **Recommendation**: AI trading advice

## 💡 How to Use

**Position Sizing by Confidence**:
- 80%+ confidence → Full position
- 60-80% → 75% position
- <60% → Skip or 50% position

**Signal Filtering**:
- Only take trades with >70% ML confidence
- Combine with HTF alignment for best results

## 🔧 Quick Troubleshooting

**"Models not trained"**
→ Add 30+ trades with MFE data, then train

**Confidence shows 0%**
→ Need more diverse training data

**Predictions seem off**
→ Retrain models with recent data

## ✅ That's It!

Your ML confidence system is ready to use.

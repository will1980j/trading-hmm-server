# API Quick Reference Guide

## 🚀 Base URL
```
https://web-production-cd33.up.railway.app
```

---

## 📡 WEBHOOK ENDPOINTS (POST)

### Signal Webhooks
```bash
# Enhanced FVG Signals (V2)
POST /api/live-signals-v2
Content-Type: application/json
{
  "signal_type": "Bullish",
  "price": 25900.50,
  "timestamp": 1234567890000,
  "session": "NY AM"
}

# Real-Time Price Updates
POST /api/realtime-price
Content-Type: application/json
{
  "type": "realtime_price",
  "symbol": "NQ",
  "price": 25900.50,
  "timestamp": 1234567890000,
  "session": "NY AM",
  "volume": 1000,
  "bid": 25900.25,
  "ask": 25900.75,
  "change": -4.75
}

# Legacy Signals (V1)
POST /api/live-signals
```

---

## 📊 V2 SIGNAL LAB APIs (GET)

```bash
# System Statistics
GET /api/v2/stats
Response: {
  "total_signals": 150,
  "pending_trades": 5,
  "active_trades": 3,
  "today_signals": 12
}

# Active Trades
GET /api/v2/active-trades
Response: {
  "trades": [
    {
      "trade_uuid": "abc-123",
      "signal_type": "Bullish",
      "signal_price": 25900.50,
      "trade_status": "active",
      "current_mfe": 1.5,
      ...
    }
  ]
}

# Current Price
GET /api/v2/price/current
Response: {
  "price": 25900.50,
  "session": "NY AM",
  "timestamp": 1234567890000,
  "change": -4.75
}

# Price Stream
GET /api/v2/price/stream?limit=10
Response: {
  "prices": [...]
}
```

---

## 🤖 MACHINE LEARNING APIs

```bash
# Train Models
POST /api/nasdaq-train
Content-Type: application/json
{
  "model_type": "random_forest",
  "features": [...]
}

# Get Predictions
POST /api/nasdaq-predict
Content-Type: application/json
{
  "signal_data": {...}
}
Response: {
  "prediction": "Bullish",
  "confidence": 0.85,
  "features": {...}
}

# Prediction Accuracy
GET /api/prediction-accuracy
Response: {
  "accuracy": 0.78,
  "total_predictions": 500,
  "correct_predictions": 390
}

# AI Insights
POST /api/ai-insights
```

---

## 🔍 MONITORING APIs

```bash
# Webhook Health
GET /api/webhook-health
Response: {
  "status": "healthy",
  "last_signal": "2024-01-01T10:30:00Z",
  "uptime": "99.9%"
}

# Webhook Statistics
GET /api/webhook-stats
Response: {
  "total_webhooks": 1500,
  "today_webhooks": 45,
  "success_rate": 99.5
}
```

---

## 🔐 AUTHENTICATION

```bash
# Login
POST /login
Content-Type: application/x-www-form-urlencoded
username=user&password=pass

# Homepage (Protected)
GET /homepage
Requires: Valid session cookie
```

---

## 🌐 DASHBOARD URLS

```bash
# V2 Signal Lab
/signal-lab-v2

# Main Signal Lab
/signal-lab-dashboard

# ML Dashboard
/ml-dashboard

# Time Analysis
/time-analysis

# Strategy Optimizer
/strategy-optimizer

# Strategy Comparison
/strategy-comparison

# AI Business Advisor
/ai-business-advisor

# Prop Portfolio
/prop-portfolio

# Trade Manager
/trade-manager

# Financial Summary
/financial-summary

# Reporting Hub
/reporting-hub

# Webhook Monitor
/webhook-monitor
```

---

## 🕐 TRADING SESSIONS

```
ASIA:      20:00 - 23:59 EST
LONDON:    00:00 - 05:59 EST
NY PRE:    06:00 - 08:29 EST
NY AM:     08:30 - 11:59 EST (Priority)
NY LUNCH:  12:00 - 12:59 EST
NY PM:     13:00 - 15:59 EST (Priority)
INVALID:   16:00 - 19:59 EST (Market Closed)
```

---

## ⚡ WEBSOCKET

```javascript
// Connect to WebSocket
const ws = new WebSocket('wss://web-production-cd33.up.railway.app/ws');

// Receive real-time updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

---

## 🔧 CURL EXAMPLES

```bash
# Test V2 Webhook
curl -X POST https://web-production-cd33.up.railway.app/api/live-signals-v2 \
  -H "Content-Type: application/json" \
  -d '{"signal_type":"Bullish","price":25900.50,"timestamp":1234567890000,"session":"NY AM"}'

# Get V2 Stats
curl https://web-production-cd33.up.railway.app/api/v2/stats

# Get Current Price
curl https://web-production-cd33.up.railway.app/api/v2/price/current

# Check Webhook Health
curl https://web-production-cd33.up.railway.app/api/webhook-health
```

---

## 📝 RESPONSE CODES

```
200 - Success
201 - Created
400 - Bad Request (invalid payload)
401 - Unauthorized (login required)
404 - Not Found
500 - Internal Server Error
```

---

## 🚨 ERROR HANDLING

```json
// Error Response Format
{
  "status": "error",
  "message": "Description of error",
  "code": "ERROR_CODE"
}
```

---

**Quick Tip:** All dashboards require authentication except webhook endpoints (public for TradingView access).

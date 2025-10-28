# NASDAQ Trading Platform - Complete Architecture Documentation

## 📊 Architecture Diagram
**File:** `platform_architecture_diagram.drawio`  
**Open with:** [Draw.io](https://app.diagrams.net/) or [diagrams.net](https://www.diagrams.net/)

---

## ☁️ CLOUD INFRASTRUCTURE

### Railway Cloud Platform
**Production URL:** `https://web-production-cd33.up.railway.app`  
**Features:**
- Auto-deploy from GitHub (main branch)
- Environment variable management
- Health monitoring and auto-restart
- HTTPS/SSL enabled
- Custom domain support
- 2-3 minute deployment time

### PostgreSQL Database (Railway Managed)
**Connection:** `DATABASE_URL` environment variable  
**Features:**
- Automatic backups
- Connection pooling
- High availability
- Encrypted connections
- Auto-scaling storage

### GitHub Integration
**Repository:** Connected to Railway  
**Workflow:**
1. Local development
2. Commit via GitHub Desktop
3. Push to main branch
4. Railway auto-detects and deploys
5. Database migrations run automatically
6. Health checks validate deployment
7. Production goes live

### TradingView Cloud
**Integration:** Webhook-based  
**Features:**
- Pine Script indicator hosting
- Alert system (15 alerts per 3 minutes)
- Webhook delivery to Railway
- Real-time data feed
- Chart hosting

---

## 🏗️ SYSTEM LAYERS

### 1. TRADINGVIEW INDICATORS (Data Source)
**Location:** TradingView Cloud  
**Purpose:** Generate trading signals and stream real-time prices

#### Enhanced FVG Indicator V2
- **File:** `enhanced_fvg_indicator_v2.pine`
- **Webhook:** `POST /api/live-signals-v2`
- **Payload Format:**
```json
{
  "signal_type": "Bullish|Bearish",
  "price": 25900.50,
  "timestamp": 1234567890000,
  "session": "NY AM|NY PM|LONDON|etc"
}
```
- **Features:**
  - FVG/IFVG detection
  - HTF bias filtering (1H, 15M, 5M)
  - Engulfing pattern detection
  - Session filtering (ASIA, LONDON, NY PRE, NY AM, NY LUNCH, NY PM)

#### Real-Time Price Streamer
- **File:** `tradingview_simple_price_streamer.pine`
- **Webhook:** `POST /api/realtime-price`
- **Update Frequency:** 1-second intervals (15 alerts per 3 minutes limit)
- **Payload Format:**
```json
{
  "type": "realtime_price",
  "symbol": "NQ",
  "price": 25900.50,
  "timestamp": 1234567890000,
  "session": "NY AM",
  "volume": 1000,
  "bid": 25900.25,
  "ask": 25900.75,
  "change": -4.75,
  "priority": "high|low"
}
```

---

### 2. WEBHOOK ENDPOINTS (Railway Cloud)
**Base URL:** `https://web-production-cd33.up.railway.app`  
**Technology:** Flask/Python  
**Purpose:** Receive and process TradingView webhooks

#### Signal Webhooks


| Endpoint | Method | Purpose | Database Table |
|----------|--------|---------|----------------|
| `/api/live-signals-v2` | POST | Enhanced FVG signals | `signal_lab_v2_trades` |
| `/api/realtime-price` | POST | 1-second price updates | `realtime_prices` |
| `/api/live-signals` | POST | Legacy V1 signals | `live_signals` |

#### Monitoring Webhooks
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/webhook-health` | GET | Health status |
| `/api/webhook-stats` | GET | Statistics |

---

### 3. DATABASE LAYER (PostgreSQL on Railway)
**Connection:** Environment variable `DATABASE_URL`  
**Features:** Auto-recovery, health monitoring, connection pooling

#### Core Tables

**signal_lab_v2_trades** (V2 Automation System)
```sql
- trade_uuid (PK, UUID)
- signal_type (Bullish/Bearish)
- signal_price (DECIMAL)
- signal_timestamp (BIGINT)
- session (VARCHAR)
- trade_status (pending_confirmation|active|completed)
- confirmation_price (DECIMAL, nullable)
- confirmation_timestamp (BIGINT, nullable)
- entry_price (DECIMAL, nullable)
- stop_loss (DECIMAL, nullable)
- current_mfe (DECIMAL)
- max_mfe (DECIMAL)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

**realtime_prices** (Price Streaming)
```sql
- id (PK, SERIAL)
- symbol (VARCHAR) - "NQ"
- price (DECIMAL)
- timestamp (BIGINT)
- session (VARCHAR)
- volume (INTEGER)
- bid (DECIMAL)
- ask (DECIMAL)
- change (DECIMAL)
- created_at (TIMESTAMP)
```

**signal_lab_trades** (Manual Entry - ML Training Source)
```sql
- Complete validated trade data
- Manual entry by trader
- Source for ML model training
- High-quality curated signals
```

**live_signals** (Legacy V1 System)
```sql
- Original signal capture system
- Maintained for backward compatibility
```

---

### 4. BACKEND API LAYER (Flask/Python)
**Location:** Railway Cloud  
**File:** `web_server.py`

#### V2 Signal Lab APIs


| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/v2/stats` | GET | System statistics | `{total_signals, pending_trades, active_trades, today_signals}` |
| `/api/v2/active-trades` | GET | All V2 trades | `{trades: [...]}` with filtering |
| `/api/v2/price/current` | GET | Latest price | `{price, session, timestamp, change}` |
| `/api/v2/price/stream` | GET | Recent prices | `{prices: [...]}` with limit param |

#### Machine Learning APIs
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/nasdaq-train` | POST | Train ML models (Random Forest, Gradient Boosting) |
| `/api/nasdaq-predict` | POST | Get predictions with confidence scores |
| `/api/prediction-accuracy` | GET | Track model accuracy and performance |
| `/api/ai-insights` | POST | AI-powered trading insights |

#### Authentication
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/login` | GET/POST | User authentication |
| `/homepage` | GET | Main homepage (requires login) |
| All dashboards | GET | Protected with `@login_required` |

#### Real-Time Features
- **WebSocket Connection:** Live updates to all connected clients
- **Signal Broadcasting:** Real-time signal distribution
- **Price Streaming:** Continuous price updates
- **Health Monitoring:** Auto-recovery and error handling

---

### 5. FRONTEND DASHBOARDS (HTML/JavaScript)
**Technology:** HTML5, CSS3, JavaScript, Chart.js  
**Features:** Responsive design, real-time updates, WebSocket integration

#### 12 Core Trading Tools

**1. Signal Lab V2 Dashboard** (`/signal-lab-v2`)
- Enhanced FVG signal display
- Real-time price widget with stale data detection
- Trade status tracking (pending → active → completed)
- Session filtering
- **Key Feature:** Rejects stale data (>5 min) and INVALID sessions

**2. Signal Lab Dashboard** (`/signal-lab-dashboard`)
- Manual signal entry and validation
- Primary ML training data source
- Performance analytics
- Trade journaling

**3. ML Intelligence Hub** (`/ml-dashboard`)
- Model training interface
- Real-time predictions
- Accuracy tracking
- Feature importance visualization

**4. Time Analysis** (`/time-analysis`)
- Session performance analysis
- Optimal entry time identification
- Temporal pattern recognition

**5. Strategy Optimizer** (`/strategy-optimizer`)
- Backtesting engine
- Parameter optimization
- Risk analysis


**6. Strategy Comparison** (`/strategy-comparison`)
- Compare multiple strategies
- Risk metrics visualization
- Performance benchmarking

**7. AI Business Advisor** (`/ai-business-advisor`)
- AI-powered insights
- Trading recommendations
- Business intelligence

**8. Prop Portfolio** (`/prop-portfolio`)
- Portfolio management
- Risk allocation
- Performance tracking

**9. Trade Manager** (`/trade-manager`)
- Trade execution
- Position management
- Order tracking

**10. Financial Summary** (`/financial-summary`)
- P&L tracking
- Performance metrics
- Financial reporting

**11. Reporting Hub** (`/reporting-hub`)
- Comprehensive reports
- Analytics export
- Custom report generation

**12. Webhook Monitor** (`/webhook-monitor`)
- Webhook health monitoring
- Statistics dashboard
- Error tracking

---

## 🔄 DATA FLOW

### Complete Cloud Workflow
```
1. TradingView Cloud: Indicator fires → Webhook POST
   ↓
2. Railway Cloud: Receives webhook → Processes request
   ↓
3. PostgreSQL Cloud: Stores data → Indexes for queries
   ↓
4. Backend APIs: Query database → Process data
   ↓
5. Frontend Dashboards: Fetch via API → Display data
   ↓
6. WebSocket Cloud: Broadcast → Real-time updates
   ↓
7. Health Monitoring: Auto-recovery → Error logging
   ↓
8. Complete Cycle: All cloud-based → No local dependencies
```

### Signal Processing Flow
```
1. TradingView Indicator detects signal
   ↓
2. Sends webhook POST to Railway endpoint
   ↓
3. Webhook handler validates and stores in PostgreSQL
   ↓
4. Backend APIs query database
   ↓
5. Frontend dashboards fetch via API
   ↓
6. WebSocket broadcasts real-time updates
   ↓
7. All connected clients receive instant updates
```

### Price Streaming Flow
```
1. TradingView streams price every 1 second
   ↓
2. Session filter validates (reject INVALID)
   ↓
3. Webhook stores in realtime_prices table
   ↓
4. Dashboard fetches via /api/v2/price/current
   ↓
5. JavaScript validates freshness (<5 min)
   ↓
6. Display live price OR show "Market Closed"
```

---

## 🎯 TRADING SESSIONS (Eastern Time)

| Session | Time Range (EST/EDT) | Priority | Status |
|---------|---------------------|----------|--------|
| ASIA | 20:00 - 23:59 | Low | Active |
| LONDON | 00:00 - 05:59 | Low | Active |
| NY PRE | 06:00 - 08:29 | Low | Active |
| NY AM | 08:30 - 11:59 | **HIGH** | Active |
| NY LUNCH | 12:00 - 12:59 | Low | Active |
| NY PM | 13:00 - 15:59 | **HIGH** | Active |
| INVALID | 16:00 - 19:59 | N/A | **CLOSED** |

**Note:** Times are constant in Eastern Time regardless of DST

---

## 🚨 CRITICAL RULES

### NO FAKE DATA RULE


**Never display:**
- Fallback/placeholder data
- Simulation data
- Sample data
- Stale data (>5 minutes old)
- Data from INVALID sessions

**Always show:**
- Real data only
- Clear error messages when data unavailable
- "Market Closed" during invalid sessions
- Honest empty states

### CLOUD-FIRST RULE
**Never use:**
- Local database connections (localhost:5432)
- Local file storage
- Local-only dependencies
- Local testing as validation

**Always use:**
- Railway DATABASE_URL
- Cloud storage solutions
- Railway-compatible libraries
- Production Railway as source of truth

### EXACT METHODOLOGY RULE
**Never:**
- Simplify signal logic
- Use placeholder calculations
- Skip confirmation requirements
- Approximate stop loss placement

**Always:**
- Implement exact confirmation logic
- Use exact pivot detection (3-candle rules)
- Follow exact stop loss methodology
- Validate all conditions

---

## 🔧 DEPLOYMENT PROCESS

### Complete Cloud Deployment Workflow
```
1. LOCAL DEV
   • Code changes
   • Test locally (development only)
   ↓
2. GITHUB
   • Commit via GitHub Desktop
   • Push to main branch
   ↓
3. AUTO-DEPLOY
   • Railway detects push
   • Builds application
   • Deploys to cloud
   ↓
4. DATABASE
   • Migrations run automatically
   • Schema updates applied
   ↓
5. HEALTH CHECK
   • Auto-restart if needed
   • Monitoring activated
   ↓
6. PRODUCTION
   • Live at Railway URL
   • Ready for traffic
   ↓
7. TRADINGVIEW
   • Webhooks active
   • Sending signals
   ↓
8. VALIDATION
   • Test endpoints
   • Verify data flow
   • Confirm cloud operation
```

### Environment Variables (Railway Cloud)
```bash
# Database Connection (Railway Managed)
DATABASE_URL=postgresql://user:pass@host:port/db

# Flask Configuration
FLASK_SECRET_KEY=[secure random key]
FLASK_ENV=production

# All variables managed in Railway dashboard
# No local environment files needed
```

### Deployment Timeline
- **Code Push:** Instant (GitHub)
- **Build Time:** 1-2 minutes (Railway)
- **Deploy Time:** 30-60 seconds (Railway)
- **Total:** 2-3 minutes (commit to live)

### Rollback Process
```bash
# Railway supports instant rollback
1. Go to Railway dashboard
2. Select previous deployment
3. Click "Redeploy"
4. Live in 30 seconds
```

---

## 📊 PERFORMANCE METRICS

### Webhook Performance
- **Target:** <100ms response time
- **Limit:** 15 alerts per 3 minutes (TradingView)
- **Strategy:** 20-second minimum intervals
- **Daily Limit:** 200 alerts (safety net)

### Database Performance
- **Connection Pooling:** Enabled
- **Auto-Recovery:** Yes
- **Health Checks:** Every 10 seconds
- **Query Optimization:** Indexed columns

### Real-Time Updates
- **WebSocket Latency:** <50ms
- **Price Update Frequency:** 1 second
- **Dashboard Refresh:** Real-time via WebSocket
- **Stale Data Threshold:** 5 minutes

---

## 🛡️ SECURITY

### Authentication
- Session-based authentication
- `@login_required` decorator on all dashboards
- Secure password hashing
- CSRF protection

### Webhooks
- Public endpoints (TradingView access)
- Payload validation
- Rate limiting
- Error handling

### Database
- Parameterized queries (SQL injection prevention)
- Connection encryption
- Environment variable credentials
- Regular backups

---

## 📈 FUTURE ENHANCEMENTS

### Automation Goals
1. **Automated Signal Validation**
   - AI learns from manual Signal Lab entries
   - 95%+ accuracy matching manual decisions
   - Real-time processing (<5 seconds)

2. **MFE Tracking**
   - Real-time Maximum Favorable Excursion
   - Break-even trigger detection
   - Stop loss hit monitoring

3. **Confirmation Monitoring**
   - Automated confirmation detection
   - Entry price calculation
   - Stop loss placement

4. **Data Flywheel**
   - More signals → Better ML → Higher confidence
   - Compound intelligence over time
   - Self-improving system

---

## 📞 SUPPORT & DOCUMENTATION

### Key Files
- **Architecture Diagram:** `platform_architecture_diagram.drawio`
- **This Documentation:** `ARCHITECTURE_DOCUMENTATION.md`
- **Project Context:** `.kiro/steering/project-context.md`
- **Webapp Spec:** `WEBAPP_STRUCTURE_SPECIFICATION.md`

### Production URL
**https://web-production-cd33.up.railway.app**

### Technology Stack
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **Deployment:** Railway Cloud
- **Version Control:** GitHub
- **Indicators:** Pine Script (TradingView)

---

**Last Updated:** 2024-01-01  
**Platform Version:** V2 (Dual Indicator System)  
**Status:** Production Ready ✅

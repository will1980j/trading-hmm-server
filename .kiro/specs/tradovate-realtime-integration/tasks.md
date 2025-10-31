# Tradovate Real-Time API Integration - Implementation Tasks

## Overview

This implementation plan breaks down the Tradovate integration into discrete, manageable coding tasks. Each task builds incrementally on previous work, with clear objectives and requirements references. The plan follows a 7-phase approach over approximately 28 weeks, with each phase delivering working, testable functionality.

**Key Principles:**
- Each task is independently testable
- Tasks build on each other incrementally
- All code must work on Railway cloud infrastructure
- Paper trading before live trading
- Parallel operation with existing systems during transition

---

## Phase 1: Foundation - Real-Time Data Infrastructure (Weeks 1-4)

### 1. Set Up Tradovate API Integration

- [ ] 1.1 Create Tradovate API client module with authentication
  - Implement OAuth2 authentication flow for Tradovate API
  - Store API credentials in Railway environment variables
  - Create connection manager with demo/live environment support
  - Add credential validation and error handling
  - _Requirements: 1.1, 1.3_

- [ ] 1.2 Implement WebSocket connection with auto-reconnect
  - Create WebSocket client using `websockets` library
  - Implement exponential backoff reconnection strategy (1s, 2s, 4s, 8s, max 30s)
  - Add connection health monitoring with heartbeat (30s interval)
  - Implement graceful shutdown handlers
  - Log all connection events (connect, disconnect, reconnect)
  - _Requirements: 1.1, 1.3, 19.1_

- [ ] 1.3 Subscribe to NQ futures market data stream
  - Implement market data subscription protocol
  - Parse incoming tick data messages
  - Validate data format and handle malformed messages
  - Emit tick events to event bus
  - _Requirements: 1.1, 1.2_

- [ ]* 1.4 Write unit tests for WebSocket client
  - Test connection establishment and authentication
  - Test reconnection logic with simulated failures
  - Test message parsing and validation
  - Test graceful shutdown
  - _Requirements: 1.1, 1.3_



### 2. Build Real-Time Price Service

- [ ] 2.1 Create tick data storage system
  - Create `tradovate_tick_data` database table
  - Implement batch insert for tick data (1-second batches)
  - Add database indexes for efficient querying
  - Implement data retention policy (archive old ticks)
  - _Requirements: 1.2, 11.1_

- [ ] 2.2 Implement in-memory price cache
  - Create Redis-like cache structure in PostgreSQL
  - Store current price, bid, ask, spread for each symbol
  - Implement sub-millisecond cache access
  - Add cache invalidation on new tick data
  - _Requirements: 1.1, 1.2_

- [ ] 2.3 Build 1-minute candle aggregation
  - Create `realtime_candles` database table
  - Implement rolling window candle builder from tick data
  - Update candles in real-time as ticks arrive
  - Mark candles as closed when minute completes
  - Store OHLCV data with timestamps
  - _Requirements: 12.1, 12.2_

- [ ] 2.4 Create price service API endpoints
  - `GET /api/realtime/current-price?symbol=NQ`
  - `GET /api/realtime/current-candle?symbol=NQ&timeframe=1m`
  - `GET /api/realtime/recent-ticks?symbol=NQ&count=100`
  - Add error handling and validation
  - _Requirements: 1.1, 1.2_

- [ ]* 2.5 Write integration tests for price service
  - Test tick storage and retrieval
  - Test candle building accuracy
  - Test cache performance
  - Test API endpoints
  - _Requirements: 1.1, 1.2_

### 3. Implement Central Event Bus

- [ ] 3.1 Create event bus architecture
  - Implement pub/sub pattern for event distribution
  - Define event types (TickEvent, SignalEvent, MFEUpdateEvent, RiskEvent, OrderEvent)
  - Create event emitter and subscriber interfaces
  - Add event logging for debugging
  - _Requirements: 1.1, 1.2_

- [ ] 3.2 Integrate event bus with WebSocket client
  - Emit TickEvent for each incoming tick
  - Emit ConnectionStatusEvent for connection changes
  - Add event rate limiting if needed
  - _Requirements: 1.1, 1.3_

- [ ] 3.3 Create event bus monitoring dashboard
  - Display event rates (ticks/second, events/minute)
  - Show subscriber counts for each event type
  - Display event processing latency
  - Add health status indicators
  - _Requirements: 19.1, 19.2_

### 4. Deploy Database Schema

- [ ] 4.1 Create database migration script
  - Write SQL migration for all new tables
  - Add indexes for performance
  - Create database views for cross-dashboard queries
  - Test migration on Railway PostgreSQL
  - _Requirements: 1.2, 11.1_

- [ ] 4.2 Deploy schema to Railway production
  - Run migration via Railway CLI
  - Verify all tables created successfully
  - Test database connections from application
  - Validate indexes are working
  - _Requirements: 1.2_

### 5. Build Health Monitoring System

- [ ] 5.1 Create health monitoring endpoints
  - `GET /api/health/tradovate` - WebSocket connection status
  - `GET /api/health/price-service` - Price service status
  - `GET /api/health/event-bus` - Event bus status
  - `GET /api/health/system` - Overall system health
  - _Requirements: 19.1, 19.2_

- [ ] 5.2 Implement system metrics collection
  - Track WebSocket connection uptime
  - Track tick processing rate
  - Track database query performance
  - Track memory and CPU usage
  - Store metrics in `system_health_metrics` table
  - _Requirements: 19.1, 19.4_

- [ ] 5.3 Create health monitoring dashboard
  - Display connection status with visual indicators
  - Show real-time metrics (ticks/sec, latency, uptime)
  - Display historical metrics charts
  - Add alert thresholds and notifications
  - _Requirements: 19.1, 19.2_

### 6. Add Live Price Ticker to All Dashboards

- [ ] 6.1 Create shared LivePriceTicker component
  - Display current NQ price with bid/ask
  - Show price change and percentage
  - Update in real-time via WebSocket
  - Add visual indicators for price direction
  - _Requirements: 1.1, 12.1_

- [ ] 6.2 Integrate WebSocket connection manager
  - Create shared WebSocket connection for all dashboards
  - Implement automatic reconnection
  - Handle connection state across page navigation
  - Add connection status indicator
  - _Requirements: 1.3_

- [ ] 6.3 Add live price ticker to all 12 dashboards
  - Main Dashboard header
  - Signal Lab V2 header
  - ML Dashboard header
  - Time Analysis header
  - Strategy Optimizer header
  - Strategy Comparison header
  - AI Business Advisor header
  - Prop Portfolio header
  - Trade Manager header
  - Financial Summary header
  - Reports header
  - Consistent placement and styling across all pages
  - _Requirements: 12.1, 12.2_



---

## Phase 2: Signal Automation - Automated Validation & Confirmation (Weeks 5-8)

### 7. Build Signal Validation Engine

- [ ] 7.1 Create signal validation service
  - Implement staleness check (signal price vs current price < 5 points)
  - Implement session validation using exact methodology
  - Create validation result data structure
  - Add validation logging for analysis
  - _Requirements: 2.1, 2.2_

- [ ] 7.2 Integrate with existing TradingView webhook
  - Modify `/api/live-signals-v2` endpoint to use validation engine
  - Maintain backward compatibility with existing webhook
  - Add validation status to webhook response
  - Log all validation decisions
  - _Requirements: 2.1, 2.5_

- [ ] 7.3 Implement confirmation monitoring service
  - Monitor real-time candles for confirmation patterns
  - Detect bullish candle closing above signal candle high
  - Detect bearish candle closing below signal candle low
  - Emit SignalEvent when confirmation detected
  - Handle signal cancellation (opposing signal)
  - _Requirements: 2.3, 2.4_

- [ ]* 7.4 Write unit tests for validation logic
  - Test staleness check with various price deviations
  - Test session validation for all sessions
  - Test confirmation detection logic
  - Test signal cancellation logic
  - _Requirements: 2.1, 2.2, 2.3_

### 8. Implement Pivot Detection Algorithm

- [ ] 8.1 Create pivot detection service
  - Implement 3-candle pivot logic (bullish: low < both adjacent lows)
  - Implement 3-candle pivot logic (bearish: high > both adjacent highs)
  - Detect pivots in confirmation range
  - Store pivot data for analysis
  - _Requirements: 4.1, 4.2_

- [ ] 8.2 Integrate pivot detection with stop loss calculation
  - Find lowest/highest point in confirmation range
  - Check if point is a 3-candle pivot
  - If pivot: use pivot ± 25 points for stop
  - If not pivot: search left 5 candles for pivot
  - If no pivot found: use first opposing candle ± 25 points
  - _Requirements: 4.1, 4.2_

- [ ]* 8.3 Write unit tests for pivot detection
  - Test 3-candle pivot identification
  - Test pivot search in confirmation range
  - Test fallback logic when no pivot found
  - Test stop loss calculation accuracy
  - _Requirements: 4.1, 4.2_

### 9. Build Entry and Stop Loss Calculator

- [ ] 9.1 Create trade setup calculator service
  - Calculate entry price (next candle open after confirmation)
  - Calculate stop loss using pivot detection
  - Calculate risk amount (entry - stop in points)
  - Create TradeSetup data structure
  - _Requirements: 2.4, 2.5, 4.1_

- [ ] 9.2 Integrate with real-time price service
  - Get next candle open price from live data
  - Use real-time candle data for pivot detection
  - Validate calculations against live market conditions
  - _Requirements: 2.4, 4.1_

- [ ]* 9.3 Write integration tests for trade setup
  - Test entry price calculation with live data
  - Test stop loss calculation with various scenarios
  - Test risk amount calculation
  - Compare automated vs manual calculations
  - _Requirements: 2.4, 2.5, 4.1_

### 10. Implement Auto Signal Lab Entry Creation

- [ ] 10.1 Create automated Signal Lab entry service
  - Auto-create entry in `signal_lab_v2_trades` when signal confirmed
  - Populate all fields: direction, entry_price, stop_loss, risk_amount, session, etc.
  - Mark entries as automated (add flag to distinguish from manual)
  - Store validation metadata (staleness_check, session_check, pivot_price)
  - _Requirements: 2.3, 2.4, 2.5_

- [ ] 10.2 Add automated entry tracking
  - Track confirmation_detected_at timestamp
  - Store actual_entry_price and actual_stop_loss
  - Link to original TradingView signal
  - Add validation_status field
  - _Requirements: 2.3, 2.4_

- [ ] 10.3 Create automated entries API endpoint
  - `GET /api/signal-lab/automated-entries?date=today`
  - Return list of automated entries with metadata
  - Include validation details and confirmation timeline
  - _Requirements: 2.3, 2.4_

### 11. Build Pending Signals Dashboard Components

- [ ] 11.1 Create PendingSignals component
  - Display signals awaiting confirmation
  - Show signal price, current price, deviation
  - Show time since signal received
  - Update in real-time via WebSocket
  - _Requirements: 2.1, 2.3_

- [ ] 11.2 Create ConfirmationTimeline component
  - Visual timeline: Signal → Monitoring → Confirmation → Entry
  - Show candles in confirmation range
  - Highlight confirmation candle
  - Display pivot points detected
  - _Requirements: 2.3, 2.4_

- [ ] 11.3 Add pending signals to Main Dashboard
  - New section showing pending signals
  - Real-time updates as confirmations occur
  - Visual alerts when confirmation detected
  - _Requirements: 2.1, 2.3_

- [ ] 11.4 Add confirmation timeline to Signal Lab V2
  - Show detailed confirmation process for each trade
  - Display candles used in confirmation
  - Highlight pivot points
  - Show entry and stop loss calculations
  - _Requirements: 2.3, 2.4_

### 12. Implement Parallel Validation Testing

- [ ] 12.1 Create validation comparison tool
  - Compare automated validation vs manual decisions
  - Track accuracy metrics (precision, recall, F1 score)
  - Identify false positives and false negatives
  - Generate validation reports
  - _Requirements: 2.1, 2.2_

- [ ] 12.2 Run parallel validation for 2 weeks
  - Automated system validates all signals
  - Manual validation continues as normal
  - Log all discrepancies for analysis
  - Refine validation logic based on results
  - _Requirements: 2.1, 2.2_

- [ ] 12.3 Analyze validation accuracy
  - Calculate accuracy metrics
  - Identify patterns in errors
  - Adjust validation thresholds if needed
  - Document validation performance
  - _Requirements: 2.1, 2.2_



---

## Phase 3: MFE Tracking - Real-Time Trade Monitoring (Weeks 9-12)

### 13. Build MFE Tracking Service

- [ ] 13.1 Create MFE tracking service core
  - Create `active_trades` table for tracking
  - Implement MFE calculation for bullish trades: (highest_price - entry) / risk_distance
  - Implement MFE calculation for bearish trades: (entry - lowest_price) / risk_distance
  - Update MFE on every tick for active trades
  - Store MFE updates in `mfe_history` table
  - _Requirements: 3.1, 3.2_

- [ ] 13.2 Implement trade activation system
  - Activate MFE tracking when automated entry created
  - Initialize active_trades record with entry, stop, risk
  - Start monitoring price updates for the trade
  - Emit MFEUpdateEvent on new extremes
  - _Requirements: 3.1, 3.2_

- [ ] 13.3 Build stop loss monitoring
  - Check if current price touches stop loss level
  - For bullish: check if price <= stop_loss
  - For bearish: check if price >= stop_loss
  - Mark trade as stopped_out when hit
  - Record final MFE and stop_hit_at timestamp
  - Update Signal Lab entry with final MFE
  - _Requirements: 3.3, 4.2_

- [ ] 13.4 Implement break-even trigger detection
  - Check if MFE reaches +1R
  - Move current_stop to entry_price when triggered
  - Mark break_even_triggered = true
  - Record break_even_triggered_at timestamp
  - Continue tracking MFE until stop hit
  - _Requirements: 3.4, 4.4_

- [ ]* 13.5 Write unit tests for MFE tracking
  - Test MFE calculation accuracy for bullish/bearish
  - Test stop loss detection
  - Test break-even trigger detection
  - Test MFE history recording
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

### 14. Create Active Trades Monitoring Components

- [ ] 14.1 Create ActiveTradesWidget component
  - Display all active trades with live MFE
  - Show entry price, current price, stop loss
  - Show current MFE in R-multiples
  - Show stop loss proximity (distance to stop)
  - Update in real-time via WebSocket
  - _Requirements: 3.1, 3.2, 6.1_

- [ ] 14.2 Create MFEHistoryChart component
  - Line chart showing MFE progression over time
  - Mark break-even trigger point
  - Mark stop loss hit point
  - Show highest MFE achieved
  - _Requirements: 3.2, 3.4_

- [ ] 14.3 Create StopLossProximity indicator
  - Visual indicator of distance to stop
  - Color-coded: green (safe), yellow (close), red (very close)
  - Show exact points to stop loss
  - Alert when within 10 points of stop
  - _Requirements: 4.1, 4.2_

### 15. Integrate MFE Tracking with Dashboards

- [ ] 15.1 Add active trades monitor to Main Dashboard
  - New section showing all active trades
  - Live MFE updates for each trade
  - Visual alerts when stops hit
  - Visual alerts when break-even triggered
  - _Requirements: 3.1, 3.2, 6.1_

- [ ] 15.2 Add MFE history charts to Signal Lab V2
  - Show MFE progression for each completed trade
  - Display highest MFE achieved
  - Show break-even trigger point if applicable
  - Compare MFE across trades
  - _Requirements: 3.2, 3.4_

- [ ] 15.3 Update Financial Summary with live P&L
  - Calculate unrealized P&L from active trades
  - Show live P&L updates as prices move
  - Display today's realized P&L from closed trades
  - Show total P&L (realized + unrealized)
  - _Requirements: 6.2, 6.3_

- [ ] 15.4 Add MFE tracking to Strategy Optimizer
  - Compare actual MFE vs backtested expectations
  - Track MFE distribution in live trading
  - Identify trades that exceeded backtest MFE
  - Analyze MFE patterns by session, direction, etc.
  - _Requirements: 3.1, 3.2_

### 16. Build MFE Analytics and Reporting

- [ ] 16.1 Create MFE analytics API endpoints
  - `GET /api/realtime/active-trades` - All active trades with live MFE
  - `GET /api/realtime/trade-mfe/{trade_id}` - Current MFE for specific trade
  - `GET /api/realtime/mfe-history/{trade_id}` - MFE progression history
  - `GET /api/analytics/mfe-distribution` - MFE distribution analysis
  - _Requirements: 3.1, 3.2_

- [ ] 16.2 Create MFE analysis reports
  - Average MFE by session
  - Average MFE by direction (bullish/bearish)
  - MFE distribution histogram
  - Trades stopped out vs break-even triggered
  - Highest MFE achieved per trade
  - _Requirements: 3.1, 3.2, 17.2_

- [ ] 16.3 Add MFE reports to Reports dashboard
  - New MFE analysis section
  - Interactive charts and visualizations
  - Export MFE data to CSV
  - Compare MFE across time periods
  - _Requirements: 3.1, 3.2_

### 17. Implement Trade Lifecycle Management

- [ ] 17.1 Create trade lifecycle state machine
  - States: pending → confirmed → active → stopped_out/break_even_hit
  - Track state transitions with timestamps
  - Emit events on state changes
  - Log all lifecycle events
  - _Requirements: 3.1, 3.3, 3.4_

- [ ] 17.2 Build trade closure system
  - Close trade when stop loss hit
  - Close trade when break-even triggered (if BE enabled)
  - Update Signal Lab entry with final data
  - Archive active_trades record
  - Emit trade closure event
  - _Requirements: 3.3, 4.3_

- [ ] 17.3 Create trade history tracking
  - Store complete trade lifecycle in database
  - Track all MFE updates
  - Record all state transitions
  - Enable trade replay for analysis
  - _Requirements: 11.4, 17.2_



---

## Phase 4: Paper Trading - Risk-Free Execution Testing (Weeks 13-16)

### 18. Build Paper Trading Simulator

- [ ] 18.1 Create paper trading core engine
  - Create `paper_trading_orders` and `paper_trading_positions` tables
  - Implement order placement logic (market and limit orders)
  - Simulate realistic fills based on current bid/ask
  - Track simulated positions and P&L
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 18.2 Implement fill simulation logic
  - Market orders: fill at current bid (sell) or ask (buy)
  - Limit orders: fill when price reaches limit
  - Add realistic slippage (0-2 ticks randomly)
  - Add latency simulation (50-200ms delay)
  - _Requirements: 5.2, 8.1_

- [ ] 18.3 Build position management system
  - Track open positions with entry price
  - Calculate unrealized P&L in real-time
  - Update position P&L on every tick
  - Handle position closure (manual or stop/target hit)
  - Calculate realized P&L on closure
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 18.4 Implement commission and fee simulation
  - Apply $2.50 per contract per side (configurable)
  - Track total commissions paid
  - Include commissions in P&L calculations
  - Generate commission reports
  - _Requirements: 6.3, 8.2_

- [ ]* 18.5 Write integration tests for paper trading
  - Test order placement and fills
  - Test position tracking
  - Test P&L calculations
  - Test commission calculations
  - _Requirements: 5.1, 5.2, 5.3_

### 19. Create Trade Manager Interface

- [ ] 19.1 Build signal execution queue component
  - Display validated signals ready for execution
  - Show signal details (direction, entry, stop, risk)
  - One-click execution button
  - Pre-trade risk check before execution
  - _Requirements: 5.1, 10.1_

- [ ] 19.2 Create order placement interface
  - Order entry form (symbol, direction, quantity, type)
  - Market order vs limit order selection
  - Stop loss and take profit inputs
  - Paper trading toggle (paper vs live)
  - Order confirmation dialog
  - _Requirements: 5.1, 5.2_

- [ ] 19.3 Build active position monitor
  - Display all open positions
  - Show entry price, current price, unrealized P&L
  - Show stop loss and take profit levels
  - Quick close position button
  - Position management controls (adjust stops/targets)
  - _Requirements: 6.1, 6.2_

- [ ] 19.4 Create order history display
  - Show all executed orders (filled, rejected, cancelled)
  - Display fill prices and timestamps
  - Show commissions paid
  - Filter by date, status, direction
  - _Requirements: 5.3, 5.4_

### 20. Implement Paper Trading API Endpoints

- [ ] 20.1 Create order execution endpoints
  - `POST /api/paper-trading/place-order` - Place new order
  - `GET /api/paper-trading/orders` - Get order history
  - `DELETE /api/paper-trading/cancel-order/{order_id}` - Cancel pending order
  - Add validation and error handling
  - _Requirements: 5.1, 5.2_

- [ ] 20.2 Create position management endpoints
  - `GET /api/paper-trading/positions` - Get all open positions
  - `GET /api/paper-trading/position/{position_id}` - Get specific position
  - `DELETE /api/paper-trading/close-position/{position_id}` - Close position
  - `PUT /api/paper-trading/update-stops/{position_id}` - Update stop/target
  - _Requirements: 6.1, 6.2_

- [ ] 20.3 Create account status endpoints
  - `GET /api/paper-trading/account-status` - Get account balance, equity, P&L
  - `GET /api/paper-trading/daily-pnl` - Get today's P&L
  - `POST /api/paper-trading/reset-account` - Reset paper trading account
  - _Requirements: 6.1, 6.3, 6.4_

### 21. Integrate Paper Trading with Dashboards

- [ ] 21.1 Add paper trading to Trade Manager
  - Integrate signal execution queue
  - Add order placement interface
  - Add active position monitor
  - Add order history display
  - Add paper/live toggle
  - _Requirements: 5.1, 6.1_

- [ ] 21.2 Add paper trading positions to Prop Portfolio
  - Display paper trading positions
  - Show paper trading P&L
  - Track paper trading against prop firm rules
  - Simulate rule violations
  - _Requirements: 6.1, 6.4, 10.1_

- [ ] 21.3 Add paper trading P&L to Financial Summary
  - Show paper trading balance and equity
  - Display unrealized and realized P&L
  - Track commissions paid
  - Compare paper vs live performance (when live enabled)
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 21.4 Add paper trading to Strategy Comparison
  - Run multiple strategies in paper trading simultaneously
  - Compare performance across strategies
  - Track execution quality per strategy
  - Identify best-performing strategy
  - _Requirements: 5.1, 6.1_

### 22. Build Paper Trading Validation System

- [ ] 22.1 Run paper trading for 2 weeks
  - Execute all validated signals in paper trading
  - Track all fills, positions, and P&L
  - Compare paper results vs manual Signal Lab entries
  - Identify discrepancies and issues
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 22.2 Validate execution quality
  - Compare paper fills vs expected prices
  - Analyze slippage distribution
  - Validate commission calculations
  - Check P&L accuracy
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 22.3 Generate paper trading reports
  - Daily performance summary
  - Execution quality metrics
  - Slippage analysis
  - Commission costs
  - Win rate and expectancy
  - _Requirements: 8.1, 8.2, 8.3_



---

## Phase 5: Risk Management - Automated Rule Enforcement (Weeks 17-20)

### 23. Build Risk Management Engine

- [ ] 23.1 Create risk management core service
  - Implement daily P&L tracking
  - Track position sizes and exposure
  - Monitor consecutive losses
  - Calculate risk metrics in real-time
  - _Requirements: 10.1, 10.2, 10.4_

- [ ] 23.2 Implement prop firm rule configuration
  - Create PropFirmRules data structure
  - Support multiple prop firm rule sets (FTMO, TopStep, etc.)
  - Allow custom rule configuration
  - Store rules in database
  - _Requirements: 10.1, 10.5_

- [ ] 23.3 Build pre-trade risk checks
  - Check daily loss limit before allowing trade
  - Check position size limits
  - Check max contracts limit
  - Check trading hours restrictions
  - Return RiskCheckResult with allow/block decision
  - _Requirements: 10.1, 10.2, 10.3_

- [ ] 23.4 Implement risk threshold alerts
  - 50-70% of limit: Warning level (require confirmation)
  - 70-90% of limit: Danger level (prominent warnings)
  - 90%+ of limit: Locked level (block new trades)
  - Emit RiskEvent on threshold crossings
  - _Requirements: 10.1, 10.2_

- [ ]* 23.5 Write unit tests for risk management
  - Test daily loss limit calculations
  - Test position size checks
  - Test consecutive loss tracking
  - Test risk threshold alerts
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

### 24. Create Risk Monitoring Components

- [ ] 24.1 Create RiskStatusPanel component
  - Display current daily P&L
  - Show daily loss limit and remaining buffer
  - Show risk status (safe/warning/danger/locked)
  - Display consecutive losses count
  - Show current exposure vs max
  - Update in real-time via WebSocket
  - _Requirements: 10.1, 10.2, 10.4_

- [ ] 24.2 Create RiskAlertModal component
  - Modal dialog for risk warnings
  - Show specific rule being approached
  - Require confirmation to proceed with trade
  - Block trade if locked status
  - _Requirements: 10.1, 10.2_

- [ ] 24.3 Create PropFirmRuleDisplay component
  - Display all active prop firm rules
  - Show compliance status for each rule
  - Visual indicators (✓ OK, ⚠ WARNING, ✗ VIOLATED)
  - Show exact values vs limits
  - _Requirements: 10.1, 10.5_

### 25. Integrate Risk Management with Dashboards

- [ ] 25.1 Add risk status to all dashboard headers
  - Small risk indicator in header (color-coded)
  - Click to expand full risk details
  - Real-time updates via WebSocket
  - Consistent across all 12 dashboards
  - _Requirements: 10.1, 10.2_

- [ ] 25.2 Add risk status panel to Main Dashboard
  - Prominent risk status display
  - Daily P&L progress bar
  - Risk threshold indicators
  - Quick access to risk details
  - _Requirements: 10.1, 10.2, 10.4_

- [ ] 25.3 Add rule compliance monitor to Prop Portfolio
  - Detailed prop firm rule display
  - Compliance status for each rule
  - Historical rule compliance tracking
  - Rule violation alerts
  - _Requirements: 10.1, 10.5_

- [ ] 25.4 Add daily limit tracker to Prop Portfolio
  - Visual progress toward daily loss limit
  - Show remaining buffer in dollars and percentage
  - Projected end-of-day P&L
  - Historical daily P&L chart
  - _Requirements: 10.1, 10.2_

- [ ] 25.5 Add pre-trade risk checks to Trade Manager
  - Run risk check before allowing order placement
  - Display risk check results
  - Block order if risk check fails
  - Show reason for block
  - _Requirements: 10.1, 10.2, 10.3_

### 26. Build Risk Analytics and Reporting

- [ ] 26.1 Create risk analytics API endpoints
  - `GET /api/realtime/risk-status` - Current risk status
  - `GET /api/realtime/daily-pnl` - Today's P&L
  - `GET /api/realtime/exposure` - Current exposure
  - `GET /api/risk/rule-compliance` - Prop firm rule compliance
  - _Requirements: 10.1, 10.2_

- [ ] 26.2 Create risk compliance reports
  - Daily risk compliance summary
  - Rule violation history
  - Near-miss incidents (approached limits)
  - Risk-adjusted performance metrics
  - _Requirements: 10.1, 10.5_

- [ ] 26.3 Add risk reports to Reports dashboard
  - New risk compliance section
  - Interactive risk charts
  - Export risk data to CSV
  - Compare risk metrics across time periods
  - _Requirements: 10.1, 10.2_

### 27. Implement AI-Powered Risk Warnings

- [ ] 27.1 Add risk warnings to AI Business Advisor
  - Analyze current risk exposure
  - Provide risk management suggestions
  - Warn about approaching limits
  - Suggest stopping for the day if needed
  - _Requirements: 10.1, 10.2, 10.4_

- [ ] 27.2 Create adaptive risk recommendations
  - Adjust position sizing based on current P&L
  - Suggest more conservative trading near limits
  - Recommend break when consecutive losses occur
  - Provide risk-adjusted strategy suggestions
  - _Requirements: 10.1, 10.4_

### 28. Test Risk Management System

- [ ] 28.1 Test with various prop firm rule sets
  - Test FTMO rules
  - Test TopStep rules
  - Test custom rule configurations
  - Verify all rules enforced correctly
  - _Requirements: 10.1, 10.5_

- [ ] 28.2 Simulate approaching daily loss limits
  - Test warning thresholds (50%, 70%, 90%)
  - Test trade blocking at 90%+
  - Test consecutive loss detection
  - Verify alerts trigger correctly
  - _Requirements: 10.1, 10.2, 10.4_

- [ ] 28.3 Validate risk calculations
  - Test daily P&L accuracy
  - Test exposure calculations
  - Test position size checks
  - Compare automated vs manual risk tracking
  - _Requirements: 10.1, 10.2, 10.3_



---

## Phase 6: ML Enhancement - Live Data Intelligence (Weeks 21-24)

### 29. Build Live Feature Engineering

- [ ] 29.1 Create live feature extraction service
  - Extract features from real-time tick data
  - Calculate bid/ask spread
  - Calculate tick volume (1min, 5min)
  - Calculate price momentum
  - Calculate volatility measures
  - _Requirements: 16.1, 16.2_

- [ ] 29.2 Implement market microstructure features
  - Order flow imbalance (buy vs sell pressure)
  - Volume-weighted average price (VWAP)
  - Time since last signal
  - Session volatility vs average
  - Price distance from session high/low
  - _Requirements: 7.1, 7.2, 16.1_

- [ ] 29.3 Create feature storage and retrieval
  - Store features with signal data
  - Create feature history for analysis
  - Build feature API endpoints
  - Enable feature visualization
  - _Requirements: 16.1, 16.2_

### 30. Enhance ML Models with Live Data

- [ ] 30.1 Retrain models with live features
  - Add live features to training dataset
  - Retrain Random Forest and Gradient Boosting models
  - Validate model performance with live features
  - Compare accuracy with/without live features
  - _Requirements: 16.1, 16.2_

- [ ] 30.2 Implement real-time prediction updates
  - Generate predictions when signal received
  - Update predictions as market conditions change
  - Track prediction confidence over time
  - Emit prediction events
  - _Requirements: 16.2, 16.5_

- [ ] 30.3 Build signal quality predictor
  - Predict if signal will confirm (before confirmation)
  - Predict likely MFE based on market conditions
  - Provide confidence scores
  - Track predictor accuracy
  - _Requirements: 16.2, 16.3_

- [ ] 30.4 Create regime detection system
  - Identify market regime changes (trending, ranging, volatile)
  - Detect unusual patterns in live data
  - Alert when regime changes
  - Adapt strategy recommendations based on regime
  - _Requirements: 16.3_

### 31. Create ML Dashboard Enhancements

- [ ] 31.1 Add live feature display to ML Dashboard
  - Show current market features in real-time
  - Display feature values for recent signals
  - Visualize feature distributions
  - Compare current vs historical features
  - _Requirements: 16.1, 16.2_

- [ ] 31.2 Add real-time predictions widget
  - Display live predictions for pending signals
  - Show prediction confidence scores
  - Update predictions as conditions change
  - Track prediction accuracy
  - _Requirements: 16.2, 16.5_

- [ ] 31.3 Add regime detector display
  - Show current market regime
  - Display regime change history
  - Alert when regime changes
  - Show regime-specific performance
  - _Requirements: 16.3_

- [ ] 31.4 Add signal quality predictor
  - Predict signal confirmation probability
  - Predict likely MFE range
  - Show prediction confidence
  - Track predictor performance
  - _Requirements: 16.2_

### 32. Implement ML-Powered Insights

- [ ] 32.1 Add ML insights to AI Business Advisor
  - ML-powered market analysis
  - Regime-based strategy recommendations
  - Signal quality assessments
  - Predictive performance insights
  - _Requirements: 16.2, 16.3_

- [ ] 32.2 Create adaptive strategy suggestions
  - Suggest strategies based on current regime
  - Recommend position sizing based on predictions
  - Adjust stop loss placement based on volatility
  - Provide entry timing recommendations
  - _Requirements: 16.2, 16.3_

### 33. Build ML Performance Tracking

- [ ] 33.1 Create prediction accuracy tracker
  - Track predictions vs actual outcomes
  - Calculate accuracy metrics (precision, recall, F1)
  - Identify prediction errors and patterns
  - Generate accuracy reports
  - _Requirements: 16.5_

- [ ] 33.2 Implement model drift detection
  - Monitor model performance over time
  - Detect when accuracy degrades
  - Alert when retraining needed
  - Track feature importance changes
  - _Requirements: 16.3, 16.5_

- [ ] 33.3 Create ML performance API endpoints
  - `GET /api/ml/live-features` - Current market features
  - `GET /api/ml/predictions` - Recent predictions
  - `GET /api/ml/accuracy` - Prediction accuracy metrics
  - `GET /api/ml/regime` - Current market regime
  - _Requirements: 16.2, 16.5_

### 34. Test ML Enhancements

- [ ]* 34.1 Validate feature extraction accuracy
  - Test feature calculations with known data
  - Compare automated vs manual feature extraction
  - Verify feature storage and retrieval
  - _Requirements: 16.1_

- [ ]* 34.2 Test prediction accuracy
  - Run predictions on historical data
  - Compare predictions vs actual outcomes
  - Calculate accuracy metrics
  - Identify areas for improvement
  - _Requirements: 16.2, 16.5_

- [ ]* 34.3 Test regime detection
  - Validate regime identification
  - Test regime change detection
  - Verify regime-specific performance tracking
  - _Requirements: 16.3_



---

## Phase 7: Advanced Analytics - Execution Quality & Insights (Weeks 25-28)

### 35. Build Execution Quality Tracking

- [ ] 35.1 Create slippage analysis service
  - Calculate slippage for each fill (expected vs actual price)
  - Track slippage distribution
  - Identify patterns in slippage
  - Alert when slippage exceeds thresholds
  - _Requirements: 8.1, 8.2, 8.3_

- [ ] 35.2 Implement fill quality metrics
  - Track fill speed (time from order to fill)
  - Measure price improvement (better than expected)
  - Track rejection rates
  - Calculate fill rate for limit orders
  - _Requirements: 8.4, 8.5_

- [ ] 35.3 Build execution quality API endpoints
  - `GET /api/execution/slippage-analysis` - Slippage metrics
  - `GET /api/execution/fill-quality` - Fill quality metrics
  - `GET /api/execution/order-stats` - Order statistics
  - _Requirements: 8.1, 8.2, 8.4_

### 36. Enhance Strategy Optimizer

- [ ] 36.1 Add live vs backtest comparison
  - Compare live execution vs backtest assumptions
  - Show slippage impact on strategy performance
  - Display commission costs vs backtest
  - Identify strategy degradation in live trading
  - _Requirements: 8.2, 8.3_

- [ ] 36.2 Add execution quality metrics
  - Display average slippage per strategy
  - Show fill quality statistics
  - Track execution costs (commissions + slippage)
  - Compare execution quality across strategies
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 36.3 Implement realistic backtesting
  - Use actual tick data for fill simulation
  - Apply realistic slippage based on historical data
  - Include actual commission costs
  - Simulate order book depth
  - _Requirements: 11.3, 16.4_

### 37. Build Time Analysis Enhancements

- [ ] 37.1 Add live session performance tracking
  - Track real-time P&L by session
  - Compare today's session performance vs historical
  - Show session momentum (improving/declining)
  - Alert when session underperforming
  - _Requirements: 9.1, 9.2_

- [ ] 37.2 Create intraday heatmap
  - Heatmap of performance by hour
  - Compare current hour vs historical average
  - Identify best/worst trading hours
  - Show volatility by time of day
  - _Requirements: 9.1, 9.3_

- [ ] 37.3 Add volatility tracking
  - Track live volatility throughout the day
  - Compare current volatility vs historical
  - Alert when volatility spikes
  - Show volatility impact on performance
  - _Requirements: 7.2, 9.3_

- [ ] 37.4 Create volume profile display
  - Show real-time volume distribution
  - Identify high-volume price levels
  - Display volume-weighted average price
  - Track volume patterns by session
  - _Requirements: 7.5, 9.4_

### 38. Enhance Strategy Comparison

- [ ] 38.1 Add live strategy comparison
  - Compare multiple strategies running in real-time
  - Show live performance metrics for each
  - Track execution quality per strategy
  - Identify best-performing strategy today
  - _Requirements: 9.5_

- [ ] 38.2 Add execution quality comparison
  - Compare slippage across strategies
  - Compare fill quality across strategies
  - Show execution costs per strategy
  - Identify most efficient strategy
  - _Requirements: 8.1, 8.4_

- [ ] 38.3 Add market condition performance
  - Track which strategy works best in current conditions
  - Show regime-specific performance
  - Recommend strategy based on market state
  - _Requirements: 9.5, 16.3_

### 39. Build Comprehensive Reporting

- [ ] 39.1 Create live trading reports
  - Real-time performance report (today's trading)
  - Intraday performance breakdown
  - Session-by-session analysis
  - Live vs historical comparison
  - _Requirements: 9.1, 9.2_

- [ ] 39.2 Create execution quality reports
  - Slippage analysis report
  - Fill quality report
  - Execution costs breakdown
  - Order statistics report
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 39.3 Create MFE analysis reports
  - MFE distribution report
  - Average MFE by session/direction
  - Highest MFE trades
  - Stop loss efficiency report
  - _Requirements: 3.1, 3.2, 17.2_

- [ ] 39.4 Create risk compliance reports
  - Daily risk compliance summary
  - Rule violation history
  - Near-miss incidents
  - Risk-adjusted performance
  - _Requirements: 10.1, 10.5_

- [ ] 39.5 Implement automated daily reports
  - Generate end-of-day summary automatically
  - Email daily performance report
  - Include all key metrics
  - Highlight notable events
  - _Requirements: 17.1, 17.2_

### 40. Add Advanced Visualizations

- [ ] 40.1 Create execution quality dashboard
  - Slippage charts and distributions
  - Fill quality metrics display
  - Order flow visualization
  - Execution timeline
  - _Requirements: 8.1, 8.2, 8.4_

- [ ] 40.2 Create market microstructure display
  - Order book depth visualization
  - Bid/ask spread charts
  - Volume profile display
  - Liquidity heatmap
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 40.3 Create correlation monitoring
  - Display correlated assets (ES, YM, RTY)
  - Show correlation breakdown alerts
  - Track VIX and market sentiment
  - Identify divergence opportunities
  - _Requirements: 15.1, 15.2, 15.3_

### 41. Final Integration and Testing

- [ ] 41.1 Perform end-to-end system testing
  - Test complete signal lifecycle (signal → confirmation → entry → MFE → stop)
  - Test all dashboard integrations
  - Verify data consistency across all dashboards
  - Test WebSocket stability under load
  - _Requirements: All_

- [ ] 41.2 Conduct performance optimization
  - Profile and optimize database queries
  - Optimize WebSocket message handling
  - Reduce memory usage
  - Improve response times
  - _Requirements: 19.1, 19.4_

- [ ] 41.3 Perform user acceptance testing
  - Run system for 2 weeks with full monitoring
  - Compare automated vs manual processes
  - Gather user feedback
  - Identify and fix issues
  - _Requirements: All_

- [ ] 41.4 Create comprehensive documentation
  - System architecture documentation
  - API documentation
  - User guides for each dashboard
  - Troubleshooting guide
  - _Requirements: All_

- [ ] 41.5 Deploy to production
  - Final deployment to Railway
  - Monitor system health
  - Verify all features working
  - Enable for live trading (when ready)
  - _Requirements: All_

---

## Optional Enhancements (Future Phases)

### 42. News and Economic Events Integration

- [ ]* 42.1 Integrate economic calendar API
  - Subscribe to economic event data
  - Display upcoming high-impact events
  - Alert before major releases
  - _Requirements: 14.1, 14.4_

- [ ]* 42.2 Implement news impact detection
  - Detect unusual volatility spikes
  - Correlate with news events
  - Adjust risk parameters during news
  - _Requirements: 14.2, 14.3_

### 43. Mobile Alerts and Monitoring

- [ ]* 43.1 Implement push notification system
  - Send alerts for validated signals
  - Alert when stops hit
  - Alert when approaching daily limits
  - Alert when targets hit
  - _Requirements: 20.1, 20.2, 20.3, 20.4_

- [ ]* 43.2 Create mobile-optimized dashboards
  - Responsive design for all dashboards
  - Mobile-friendly trade monitoring
  - Quick trade approval from mobile
  - Emergency controls on mobile
  - _Requirements: 20.1, 20.2, 20.3_

### 44. Live Order Execution (Post Paper Trading Validation)

- [ ]* 44.1 Integrate Tradovate REST API for orders
  - Implement order placement via Tradovate API
  - Handle order fills and rejections
  - Track live positions
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ]* 44.2 Build live execution safety controls
  - Require explicit confirmation for live orders
  - Implement kill switch (stop all trading)
  - Add order size limits
  - Require two-factor authentication
  - _Requirements: 5.1, 10.1_

---

## Summary

**Total Tasks**: 44 major tasks with 200+ sub-tasks
**Timeline**: 28 weeks (7 phases × 4 weeks)
**Approach**: Incremental, testable, cloud-native
**Priority**: Foundation → Automation → Tracking → Trading → Risk → ML → Analytics

**Key Milestones**:
- Week 4: Real-time data flowing, live prices on all dashboards
- Week 8: Automated signal validation and confirmation
- Week 12: Real-time MFE tracking for all trades
- Week 16: Paper trading fully functional
- Week 20: Risk management enforcing all rules
- Week 24: ML models using live data
- Week 28: Complete platform transformation

**Success Criteria**:
- 95%+ signal validation accuracy
- 100% MFE tracking accuracy
- Zero rule violations
- Sub-second latency for all updates
- 99.9% uptime during market hours
- 80%+ signals processed automatically
- 3x increase in dataset growth rate


# 📘 UNIFIED ROADMAP — SECOND SKIES TRADING

### _Enterprise Architecture v1.1 — Single Source of Truth_

### _Updated December 13, 2025 — Priorities Adjusted for Data-Driven Manual Trading_

## 🏛 INTRODUCTION

This unified roadmap consolidates:
- ROADMAP_MASTER.md
- AI_Trading_System_Master_Plan.md
- PRODUCT_BACKLOG.md
- All MODULE completion files
- All STAGE completion files
- All PATCH completion files
- Architecture documentation
- ML + execution + automation requirements
- Strict Kiro protocols and development rules
- Enterprise-level Level/Phase architecture

This is now the **single authoritative roadmap** for the entire Second Skies platform.

---

## 🎯 STRATEGIC OVERVIEW

**Goal:** Leave AWS and trade prop firms full-time for massive profits

**Strategy:**
1. **Data Collection (DONE ✅):** Automated Signals Dashboard collects every signal automatically
2. **Strategy Discovery (6-18 months):** Let data reveal optimal trading approach
3. **Manual Trading (Months 12-24):** Trade prop firms manually using data-discovered strategy
4. **Prove Profitability:** Build track record and consistent income
5. **Automation (Months 24+):** Automate proven profitable strategy

**Key Insight:** Don't automate before knowing what works. Discover optimal strategy through data, prove it manually, THEN automate.

---

## 📊 TWO-TRACK DEVELOPMENT APPROACH

### TRACK 1: Data Collection (PASSIVE - Runs Automatically)
- **Status:** ✅ OPERATIONAL
- **Effort:** 0 hours/week (automated)
- **Timeline:** Months 1-24 (continuous)
- **Goal:** Accumulate 300-900 signals to reveal optimal strategy

### TRACK 2: Platform Development (ACTIVE - Build Business Tools)
- **Status:** ⏳ IN PROGRESS
- **Effort:** 20-30 hours/week
- **Timeline:** Months 7-18
- **Goal:** Build professional prop firm business infrastructure

**These tracks run in PARALLEL, not sequentially.**

---

# 🧩 LEVEL-BASED ENTERPRISE ARCHITECTURE (0–10)

Each LEVEL contains PHASES.
Each PHASE contains MODULES.
Each MODULE contains SUBMODULES or STAGES.

**Priority Levels:**
- 🔴 **CRITICAL:** Needed for manual trading business (Months 7-18)
- 🟡 **HIGH:** Needed for profitability and scaling (Months 12-24)
- 🟢 **MEDIUM:** Needed for automation (Months 24+)
- ⚪ **LOW:** Nice-to-have or future expansion

---

# 🟩 LEVEL 0 — FOUNDATIONS (100% Complete)

## PHASE 0 — Foundations

- Trading methodology definition
- Cloud architecture setup (Railway + Postgres + Flask)
- Strict Kiro Protocol
- Repo synchronization & guardrails
- Baseline ML research structure
- Webhook + signal schema foundation

**Completion Criteria:**
✔ Stable architecture
✔ Signal ingestion working
✔ Repo stable
✔ Development lifecycle defined

---

# 🟩 LEVEL 1 — CORE PLATFORM & DATA COLLECTION (33% Complete)

**Priority:** 🔴 CRITICAL  
**Timeline:** Months 1-12  
**Goal:** Automated data collection + professional platform foundation

## PHASE 1 — Core Platform & UI/UX Modernization

### H1.1 — Core Platform Foundation ✅

**Status:** COMPLETE  
**Completed:** Months 1-6

**Modules:**
- Homepage Command Center (Module 15) ✅
- Automated Signals Engine (Always-On Ingestion) ✅
- Automated Signals Dashboard (Lifecycle Viewer) ✅
- Real-Time Event Processor (ENTRY / MFE_UPDATE / BE_TRIGGERED / EXIT_SL) ✅
- Automated Signals Storage (`automated_signals` table) ✅
- Webhook Processing Pipeline ✅
- Live Data Integrity Checker ✅
- **Hybrid Signal Synchronization System** ✅ (Added Month 6)

**Functional Notes:**
- **DATA COLLECTION AUTOMATION:** Automated Signals Engine runs 24/7 collecting every signal automatically
- This is TRACK 1 (Passive) - runs in background with zero effort
- Dashboard collects complete lifecycle data for strategy discovery
- All signal lifecycle events (SIGNAL_CREATED, ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT_SL, CANCELLED) captured
- Hybrid Sync ensures 100% data completeness (90+ health score)
- Foundation for ML training and strategy discovery
- **Expected Data:** 300-900 signals over 6-18 months will reveal optimal trading strategy

---

### H1.2 — Main Dashboard ⭐ H1 (Module 16) ✅

**Status:** COMPLETE  
**Priority:** 🔴 CRITICAL  
**Completed:** Month 5

**Description:** Primary command center with two-column layout, real-time KPIs, and session-aware analytics.

**Panels:**
- Active Signals (lifecycle-driven)
- Live Trades (H1 essentials)
- Prop-Firm Status (H1-limited)
- Automation Engine (locked)
- P&L Today (expanded)
- Session Performance (full upgrade)
- Signal Quality (real metrics)
- Risk Snapshot (with warnings)

---

### H1.3 — Time Analysis ⭐ H1 (Module 17) ✅

**Status:** COMPLETE

**Description:** Fully integrated with Automated Signals ingestion. Real-time, session-aware temporal analysis.

**Features:**
- Session performance tracking
- Intraday heatmaps
- Hot hours analysis
- Feeds ML features in later phases

**Notes:**
- Integrated with Automated Signals Engine
- Real-time data processing
- Session-aware analytics
- Foundation for ML temporal features

---

### H1.4 — Automated Signals Dashboard Redesign (H1.2 Mirror Aesthetic)

**Status:** PLANNED  
**Priority:** ⚪ LOW (Cosmetic)  
**Timeline:** Month 12+ (if desired)

**Description:** Complete redesign of Automated Signals Dashboard to mirror H1.2 Main Dashboard aesthetic and structure.

**Note:** Current dashboard is functional. Redesign is cosmetic only. Consider deferring to focus on business-critical features.

#### H1.4A — Layout Overhaul (Mirror H1.2)
- Two-column responsive grid
- Deep-blue fintech theme
- Card structure identical to main-dashboard
- Neon-accent typography
- Professional spacing and hierarchy

#### H1.4B — Real-Time Panels
- **Active Signals Panel:** Currently running signals with live MFE tracking
- **Live Trades Panel:** Active positions with entry/SL/MFE/BE status
- **Completed Trades Panel:** Historical signals with final outcomes
- **Signal Lifecycle Summary:** Event timeline and state transitions

#### H1.4C — Stats Summary
- Total signals today / week
- Win/loss distribution
- Avg MFE / BE impact
- Session breakdown
- R-multiple distribution
- Lifecycle event counts

#### H1.4D — Roadmap-Locked Future Analytics
🔒 **Execution Quality Engine** (H2.26)
🔒 **Trade Outcome Predictor** (H2.27)
🔒 **Market Regime Classifier** (H2.28)
🔒 **Entry Confirmation Confidence** (H2.29)
🔒 **MFE Distribution Engine** (H2.30)
🔒 **BE Efficiency Analysis** (H2.31)

---

### H1.5 — ML Intelligence Hub ⭐ H1 (Module 20)

**Status:** PLANNED  
**Priority:** 🟡 HIGH  
**Timeline:** Months 10-12

**Description:** ML analysis tools for strategy discovery (NOT trading automation yet)

**Purpose:**
- Analyze accumulated signal data (300+ signals)
- Identify patterns (session performance, HTF impact, BE vs No-BE)
- Train ML models to reveal optimal strategy
- Provide data-driven insights for manual trading decisions

**Note:** This is for ANALYSIS and DISCOVERY, not automated trading. Trading automation comes much later (Level 5 full implementation, Month 24+).

---

### H1.6 — Financial Summary ⭐ H1 (Module 21)

**Status:** PLANNED  
**Priority:** 🔴 CRITICAL  
**Timeline:** Months 13-15

**Description:** Complete financial tracking for prop firm business

**Features:**
- P&L tracking (all accounts)
- Income/expense tracking
- Tax planning and reporting
- Cash flow management
- Performance metrics

**Why Critical:** Essential for managing multi-prop-firm business and tax compliance.

---

### H1.7 — Reporting Center ⭐ H1 (Module 22)

**Status:** PLANNED  
**Priority:** 🟡 HIGH  
**Timeline:** Months 15-17

**Description:** Professional reporting for prop firms and business management

**Features:**
- Weekly performance reports
- Monthly business reviews
- Prop firm submission materials
- Tax documentation
- Performance history export

**Why High:** Needed for prop firm applications and professional operations.

---

### Authentication & Navigation Modules

**Priority:** ⚪ LOW (Single-user platform)  
**Status:** DEFERRED

- H2.1 Secure Authentication System ⭐ H2 (Basic auth sufficient)
- H2.2 Navigation Framework ⭐ H2 (Current nav works)
- H2.3 User/Session Manager ⭐ H2 (Single user)
- H2.4 User Roles & Permissions ⭐ H2 (Not needed)
- H2.5 Multi-Factor Authentication (MFA) ⭐ H2 (Overkill)
- H3.1 Unified Navigation System (role-aware) ⭐ H3 (Not needed)
- H3.2 Audit Trail & Activity Logging (expanded) ⭐ H3 (Basic logging sufficient)

**Note:** These modules are designed for multi-user platforms. Since this is a single-user trading platform, basic authentication is sufficient. Consider skipping or deferring indefinitely.

---

# 🟦 LEVEL 2 — AUTOMATED SIGNALS ENGINE (80% Complete)

**Priority:** 🟢 MEDIUM (Most already built)  
**Timeline:** Months 1-6 (mostly complete)  
**Status:** Core functionality operational, advanced features deferred

## PHASE 2A — Raw Ingestion & Normalization ✅

**Status:** COMPLETE (Built in H1.1)

Modules:
- H1.7 Signal Noise Filter ✅ (Lifecycle enforcement)
- H1.8 Webhook Ingestion ✅ (Webhook pipeline operational)
- H1.9 Timestamp Normalization ✅ (NY timezone handling)
- H2.6 Duplicate Filtering ✅ (Lifecycle enforcement)
- H2.7 Session Tagging ✅ (Session detection working)

**Note:** These modules were built as part of H1.1 Core Platform Foundation.

## PHASE 2B — Signal Validation Engine ✅

**Status:** COMPLETE (Built in H1.1 + Hybrid Sync)

Modules:
- H1.10 Validation Rules ✅ (Lifecycle enforcement)
- H1.11 Outlier Detection ✅ (Data validation)
- H2.8 Guardrails ✅ (Strict mode enforcement)
- H2.9 Missing-Field Repair ✅ (Hybrid Sync reconciliation)

**Note:** These modules were built as part of H1.1 and Hybrid Sync System.

## PHASE 2C — Signal Lifecycle Engine ✅

**Status:** COMPLETE (Built in H1.1)

Modules:
- H1.12 Signal Lifecycle Model ✅ (SIGNAL_CREATED → ENTRY → MFE → EXIT)
- H1.13 MFE Engine (Dual) ✅ (be_mfe, no_be_mfe tracking)
- H1.14 BE Logic ✅ (BE_TRIGGERED events)
- H1.15 Exit Consolidation ✅ (EXIT_SL, EXIT_BE)
- H2.10 Multi-Event Reconciliation ✅ (Hybrid Sync)
- H2.11 Data Accumulation Window ✅ (Continuous collection)
- H2.12 Signal Schema Governance ✅ (Database schema)
- H3.3 Data Integrity Watchdog ✅ (Hybrid Sync gap detection)
- H3.4 Signal Replay Engine ⏳ (Deferred - not needed yet)

**Note:** Core lifecycle engine is complete. Advanced features deferred.

## PHASE 2.5 — Prop Guardrails & Evaluation

**Status:** PLANNED  
**Priority:** 🔴 CRITICAL  
**Timeline:** Months 10-12

Modules:
- H1.16 Drawdown Limits ⏳ (Needed for prop firm trading)
- H1.17 Daily Loss Limits ⏳ (Needed for prop firm trading)
- H2.13 Consistency Metrics ⏳ (Needed for evaluations)
- H2.14 Evaluation Reporting ⏳ (Needed for evaluations)

**Note:** These are CRITICAL for manual prop firm trading. Move to high priority.

---

# 🟧 LEVEL 3 — REAL-TIME DATA LAYER (0%)

**Priority:** 🟢 MEDIUM (Deferred to automation phase)  
**Timeline:** Months 24+ (AFTER manual profitability proven)  
**Cost:** $100-300/month (Polygon/Massive API)

**Strategic Note:** Real-time data is NOT needed for strategy discovery or manual trading. Current TradingView 1-minute bars are sufficient. Only needed when scaling to 24/7 automated trading.

## PHASE 3 — Real-Time Data Infrastructure

**Status:** DEFERRED until Month 24+

Modules:
- H1.18 Real-Time Price Stream ⭐ H1
- H1.19 ATR/Volatility Model ⭐ H1
- H1.20 Tick-to-Bar Converter ⭐ H1
- H2.15 Session Heatmaps ⭐ H2
- H2.16 Regime Classifier ⭐ H2
- H2.17 Bar Aggregation ⭐ H2
- H2.18 Session Metrics ⭐ H2
- H3.5 Tick Data Warehouse ⭐ H3
- H3.6 Market Replay Engine ⭐ H3
- H3.7 DOM / Orderbook Capture Layer ⭐ H3
- H3.8 Latency Monitoring ⭐ H3

**When to Build:**
- After proving manual profitability (Month 18+)
- When ready to automate trading (Month 24+)
- When hitting TradingView rate limits
- When scaling to 24/7 operation

**Why Deferred:** Current data quality is sufficient for strategy discovery and manual trading. Real-time data is expensive (time + money) and only needed for automation.

---

# 🟨 LEVEL 4 — EXECUTION & AUTOMATION ENGINE (0%)

**Priority:** 🟢 MEDIUM (Deferred to automation phase)  
**Timeline:** Months 24-30 (AFTER manual profitability proven)

**Strategic Note:** Automated execution comes AFTER proving manual profitability. Don't automate an unproven strategy. Trade manually first, prove it works, THEN automate.

## PHASE 4A — Execution Router

**Status:** DEFERRED until Month 24+

Modules:
- H1.21 Multi-Account Router ⭐ H1
- H1.22 Order Queue ⭐ H1
- H1.23 Dry-Run Mode ⭐ H1 (Paper trading - Month 22-24)
- H1.24 State Reconciliation ⭐ H1
- H2.19 Program Sizing ⭐ H2
- H2.20 Risk Engine Integration ⭐ H2
- H2.21 Account State Manager ⭐ H2
- H2.22 Position State Manager ⭐ H2
- H3.9 Execution Safety Sandbox ⭐ H3
- H3.10 Circuit Breakers ⭐ H3
- H3.11 Execution Decision Engine (ML → action logic) ⭐ H3
- H3.12 Pre-Trade Checks ⭐ H3

## PHASE 4B — Automated Execution Engine

**Status:** DEFERRED until Month 26+

Modules:
- H1.25 Automated Entry Logic ⭐ H1
- H1.26 Automated Exit Logic ⭐ H1
- H1.27 Position Sizing Automation ⭐ H1
- H2.23 Strategy–Signal Compatibility Engine ⭐ H2

**Dependencies:**
- Manual profitability proven (12+ months)
- Strategy validated through data
- Level 3 (Real-Time Data) operational
- Level 5 (ML) providing high-confidence signals

**When to Build:**
- After 12+ months of profitable manual trading
- After strategy is proven and validated
- When ready to scale beyond manual capacity

---

# 🟪 LEVEL 5 — ML INTELLIGENCE LAYER (0%)

**Priority:** Split into two phases  
**Phase A (Analysis):** 🟡 HIGH - Months 10-12  
**Phase B (Automation):** 🟢 MEDIUM - Months 24+

**Strategic Note:** ML serves TWO purposes:
1. **Strategy Discovery (Phase A):** Analyze data to reveal optimal strategy (Months 10-12)
2. **Trading Automation (Phase B):** Automate proven strategy (Months 24+)

## PHASE 5A — ML Strategy Discovery (Months 10-12)

**Status:** PLANNED  
**Priority:** 🟡 HIGH  
**Goal:** Use ML to analyze data and reveal optimal trading strategy

Modules:
- H1.28 Early-Stage Strategy Discovery Engine ⭐ H1 (Month 10)
- H1.29 ML Dataset Builder ⭐ H1 (Month 10)
- H1.30 Feature Engineering ⭐ H1 (Month 11)
- H1.31 Expectancy Model ⭐ H1 (Month 11)
- H1.32 R-Multiple Distribution Predictor ⭐ H1 (Month 12)
- H2.25 ML Dashboard (Module 20 baseline) ⭐ H2 (Month 12)

**Purpose:** Analyze 300+ signals to identify:
- Best sessions (ASIA, LONDON, NY AM, NY PM)
- Best HTF alignments (which combinations work?)
- BE=1 vs No-BE (which strategy is better?)
- Optimal risk management (position sizing, targets)

**Output:** Data-driven strategy recommendations for manual trading

## PHASE 5B — ML Trading Automation (Months 24+)

**Status:** DEFERRED  
**Priority:** 🟢 MEDIUM  
**Goal:** Automate proven profitable strategy

Modules:
- H2.24 Regime Classifier ⭐ H2
- H3.13 Feature Store ⭐ H3
- H3.14 Model Registry ⭐ H3
- H3.15 Model Drift Detection ⭐ H3

**Purpose:** Automate the strategy discovered in Phase A and proven through manual trading

**Dependencies:**
- 12+ months of profitable manual trading
- Strategy validated and proven
- Ready to scale beyond manual capacity

---

# 🟥 LEVEL 6 — STRATEGY RESEARCH & ANALYTICS (0%)

**Priority:** 🟡 HIGH (MOVED UP - Start Month 10)  
**Timeline:** Months 10-15  
**Goal:** Analyze data to discover optimal trading strategy

**Strategic Note:** This level is CRITICAL for strategy discovery. Originally scheduled for Month 22-26, but moved to Month 10-15 to align with data accumulation timeline (300+ signals by Month 10).

## PHASE 6 — Strategy Research & Optimization

### Core Analysis Modules (Months 10-12) - CRITICAL
- H1.36 Expectancy Analysis ⭐ H1 (Month 10)
- H2.26 Session Analytics ⭐ H2 (Month 11)
- H1.33 Signal–Strategy Attribution Engine ⭐ H1 (Month 12)

**Purpose:** Analyze accumulated data to answer:
- Which sessions have best expectancy?
- Which HTF alignments are most profitable?
- BE=1 vs No-BE: which is better?
- What's the optimal trading approach?

### Strategy Tools (Months 13-15) - HIGH PRIORITY
- H1.34 Strategy Optimizer (Module 18) ⭐ H1 (Month 13)
- H1.35 Strategy Compare (Module 19) ⭐ H1 (Month 14)
- H2.31 R-Multiple Expectation Designer ⭐ H2 (Month 15)

**Purpose:** Refine and validate discovered strategy

### Advanced Features (Months 16+) - DEFERRED
- H2.27 Multi-Strategy Portfolio Analysis ⭐ H2 (Not needed - single strategy)
- H2.28 What-If Scenarios ⭐ H2 (Nice-to-have)
- H2.29 Backtesting Engine ⭐ H2 (Deferred to Month 20+)
- H2.30 Strategy Library ⭐ H2 (Not needed - single strategy)
- H3.16 Automated Reporting Engine ⭐ H3 (Covered in H1.7)
- H3.17 Slide/Document Generation ⭐ H3 (Not needed)
- H3.18 Report Scheduler ⭐ H3 (Covered in H1.7)
- H3.19 Narrative AI Summarization ⭐ H3 (Nice-to-have)

**Completion Target:** Month 15 (optimal strategy identified and validated)

---

# 🟩 LEVEL 7 — SIGNAL QUALITY & INTEGRITY (0%)

## PHASE 7 — Signal Quality & Telemetry

Modules:
- H1.37 Signal Integrity API ⭐ H1
- H1.38 Telemetry Pipeline (PATCH 7A–7M) ⭐ H1
- H1.39 Validation Checks ⭐ H1
- H2.32 Signal Validator ⭐ H2
- H2.33 Anomaly Detection ⭐ H2
- H2.34 Repair Engine ⭐ H2
- H3.20 Integrity Dashboard ⭐ H3
- H3.21 Statistical Integrity Engine ⭐ H3
- H3.22 Quality Scoring Engine ⭐ H3
- H3.23 Alerting Engine ⭐ H3

---

# 🟫 LEVEL 8 — PROP PORTFOLIO & COMPLIANCE (0%)

**Priority:** 🔴 CRITICAL (MOVED UP - Start Month 10)  
**Timeline:** Months 10-18  
**Goal:** Professional prop firm business management

**Strategic Note:** This level is CRITICAL for your goal of leaving AWS and trading prop firms full-time. Originally scheduled for Month 28-32, but moved to Month 10-18 to align with manual trading timeline.

## PHASE 8 — Prop Firm Management & Compliance

### Core Modules (Months 10-12) - CRITICAL
- H1.43 Prop Account Registry ⭐ H1 (Month 10)
- H2.35 Risk Rule Logic ⭐ H2 (Month 11)
- H2.37 Violation Detection ⭐ H2 (Month 11)
- H2.38 Account Breach Detection ⭐ H2 (Month 11)
- H3.25 Compliance Dashboard ⭐ H3 (Month 12)

### Multi-Account Modules (Months 13-15) - HIGH PRIORITY
- H1.42 Prop Portfolio Management ⭐ H1 (Month 13)
- H2.36 Rule Library ⭐ H2 (Month 14)
- H3.27 Exposure Monitoring ⭐ H3 (Month 15)

### Advanced Modules (Months 16-18) - MEDIUM PRIORITY
- H1.40 Prop Firm Challenge Simulator ⭐ H1 (Month 16)
- H1.41 Drawdown Stress Tester ⭐ H1 (Month 17)
- H2.39 Payout Schedule ⭐ H2 (Month 17)
- H2.40 Programme Sizing ⭐ H2 (Month 18)
- H3.24 Payout Engine ⭐ H3 (Month 18)
- H3.26 Scaling Ladder ⭐ H3 (Month 18)

**Completion Target:** Month 18 (ready for 10+ prop firm accounts)

---

# 🟪 LEVEL 9 — SCALING & INFRASTRUCTURE (0%)

**Priority:** ⚪ LOW (Not needed for single-user platform)  
**Timeline:** Indefinite (only if building multi-user SaaS)  
**Status:** DEFERRED or SKIP

**Strategic Note:** These modules are for scaling to 100+ users, multi-region deployment, and enterprise infrastructure. Not needed for single-user prop firm trading platform.

## PHASE 9 — Infrastructure & Scaling

**Status:** DEFERRED indefinitely (may never be needed)

Modules:
- H2.41 Worker Scaling ⭐ H2 (Not needed - single user)
- H2.42 DB Scaling ⭐ H2 (Current DB sufficient)
- H2.43 Multi-Region Support ⭐ H2 (Not needed)
- H2.44 Load Balancing ⭐ H2 (Not needed - low traffic)
- H2.45 Caching Layer ⭐ H2 (Not needed - fast enough)
- H2.46 Performance Tuning ⭐ H2 (Only if issues arise)
- H3.28 Observability Stack ⭐ H3 (Basic monitoring sufficient)
- H3.29 Observability Layer ⭐ H3 (Not needed)
- H3.30 Distributed Worker Queue ⭐ H3 (Not needed)
- H3.31 Disaster Recovery ⭐ H3 (Railway handles backups)

**When to Build:**
- If building multi-user SaaS product (not current goal)
- If experiencing performance issues (not happening)
- If scaling to 100+ concurrent users (not applicable)

**Recommendation:** Skip this level entirely unless goals change.

---

# 🟦 LEVEL 10 — AUTONOMOUS TRADER ENGINE (0%)

**Priority:** 🟢 MEDIUM (Deferred to automation phase)  
**Timeline:** Months 30+ (AFTER manual profitability + initial automation proven)

**Strategic Note:** Autonomous trading is the ultimate goal, but comes LAST. Must prove manual profitability first, then basic automation, then full autonomy.

## PHASE 10 — Autonomous AI Trading

**Status:** DEFERRED until Month 30+

Modules:
- H2.47 Automated Challenge Execution Planner ⭐ H2
- H2.48 Strategy Selector ⭐ H2
- H2.49 Autonomous Executor ⭐ H2
- H2.50 Auto Risk Manager ⭐ H2
- H2.51 AI Business Advisor ⭐ H2 (Basic version in H1.5)
- H2.52 Auto Tilt Detection ⭐ H2
- H2.53 Regime-Aware Execution ⭐ H2
- H2.54 Auto Scale Up/Down ⭐ H2
- H3.32 Safety-Aware Strategy Selector ⭐ H3
- H3.33 Autonomous Execution Simulator (shadow mode) ⭐ H3
- H3.34 Fund Automation Bridge ⭐ H3

**Dependencies:**
- 12+ months of profitable manual trading
- Level 3 (Real-Time Data) operational
- Level 4 (Execution) proven in paper trading
- Level 5 (ML) providing reliable signals
- Level 8 (Prop Firms) managing 10+ accounts successfully

**When to Build:**
- After proving manual profitability ($15K-25K/month)
- After basic automation working (Level 4)
- When ready to scale beyond manual capacity
- When comfortable with autonomous decision-making

---

# 📅 REVISED TIMELINE SUMMARY

## Months 1-6: Foundation (COMPLETE ✅)
- ✅ Level 0: Foundations
- ✅ Level 1 (H1.1-H1.3): Data collection operational
- ✅ Level 2: Core signal engine (80% built in H1.1)
- **Data Status:** 36-150 signals collected

## Months 7-12: Platform Completion + Strategy Discovery
**TRACK 1 (Passive):** Data accumulates to 150-300 signals  
**TRACK 2 (Active):** Build business infrastructure

**Development Focus:**
- Complete Level 1 (H1.4-H1.7): Platform polish
- Start Level 5A: ML Strategy Discovery (Months 10-12)
- Start Level 6: Strategy Analysis (Months 10-12)
- Start Level 8: Prop Firm Tools (Months 10-12)
- Start Level 2.5: Prop Guardrails (Months 10-12)

**Trading:** Begin with 1-2 prop accounts (evaluation phase)

## Months 13-18: Multi-Account Scaling + Strategy Validation
**TRACK 1 (Passive):** Data accumulates to 300-600 signals (strategy clear)  
**TRACK 2 (Active):** Scale prop firm business

**Development Focus:**
- Complete Level 8: Prop Firm Management
- Complete Level 6: Strategy Research
- Complete Level 2.5: Prop Guardrails
- Complete Level 7: Signal Quality (if needed)

**Trading:** Scale to 5-10 prop accounts, prove profitability

**Milestone:** Ready to leave AWS full-time ✅

## Months 19-24: Profitability + Automation Planning
**TRACK 1 (Passive):** Data accumulates to 600-900 signals  
**TRACK 2 (Active):** Optimize operations

**Development Focus:**
- Optimize existing tools
- Plan automation approach
- Build paper trading system (Month 22-24)

**Trading:** 10-15 prop accounts, consistent $15K-25K/month

**Milestone:** Proven profitable business ✅

## Months 24+: Automation Phase (FUTURE)
**Development Focus:**
- Level 3: Real-Time Data Integration
- Level 4: Execution Automation
- Level 5B: ML Trading Automation
- Level 10: Autonomous Trading

**Trading:** Transition from manual to automated execution

---

# 🎯 PRIORITY SUMMARY

## CRITICAL (Months 7-18) 🔴
**Goal:** Build prop firm business infrastructure

- Complete Level 1 (H1.4-H1.7)
- Level 2.5: Prop Guardrails
- Level 5A: ML Strategy Discovery
- Level 6: Strategy Analysis (core modules)
- Level 8: Prop Firm Management

**Why:** These enable manual prop firm trading business

## HIGH (Months 12-24) 🟡
**Goal:** Prove profitability and scale

- Manual trading with discovered strategy
- Scale to 10+ prop accounts
- Build track record
- Consistent $15K-25K/month income

**Why:** Prove the business model works before automating

## MEDIUM (Months 24+) 🟢
**Goal:** Automate proven strategy

- Level 3: Real-Time Data
- Level 4: Execution Automation
- Level 5B: ML Trading Automation
- Level 10: Autonomous Trading

**Why:** Only automate after proving manual profitability

## LOW (Indefinite) ⚪
**Goal:** Nice-to-have or not needed

- Level 9: Infrastructure Scaling (single-user platform)
- Authentication modules (single user)
- Advanced features without clear ROI

**Why:** Not needed for your goals

---

# 🗂 CLEANUP NOTES

All legacy files should be moved to:

/archive/roadmap/legacy/

This includes:
- ROADMAP_MASTER.md
- AI_Trading_System_Master_Plan.md
- PRODUCT_BACKLOG.md
- All MODULE_* MDs
- All STAGE_* MDs
- All PATCH_* MDs
- All legacy V2 documents

---

# 📝 ROADMAP CHANGE LOG

**v1.1 - December 13, 2025:**
- Clarified "automation" terminology (data collection vs trading automation)
- Moved Level 8 (Prop Firms) from Month 28 to Month 10 (CRITICAL priority)
- Moved Level 6 (Strategy Analysis) from Month 22 to Month 10 (HIGH priority)
- Split Level 5 into Phase A (Discovery - Month 10) and Phase B (Automation - Month 24+)
- Marked Level 2 as 80% complete (built in H1.1)
- Deferred Level 3 (Real-Time Data) to Month 24+ (after profitability)
- Deferred Level 4 (Execution) to Month 24+ (after profitability)
- Marked Level 9 (Infrastructure) as LOW priority (single-user platform)
- Added two-track approach (passive data collection + active development)
- Aligned timeline with goal: leave AWS full-time by Month 18-24

**v1.0 - November 2025:**
- Initial unified roadmap consolidating all legacy documents

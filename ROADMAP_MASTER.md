# 🔒 Strict Kiro Protocol (SKP)

All Kiro operations must follow these rules:

- Zero assumptions  
- Zero autofix  
- Zero creative interpretation  
- Only modify files explicitly specified  
- No refactors unless explicitly authorized  
- No architecture changes unless explicitly authorized  
- Ask for clarification if ANYTHING is unclear  
- Validate syntax, imports, integration, and roadmap alignment  
- Never add imports unless explicitly instructed  
- Always output structured patch details

# 📘 Roadmap Synchronization Protocol

After each validated patch:

1. ChatGPT updates the roadmap text.
2. ChatGPT generates a Strict Kiro Update Prompt.
3. User pastes the prompt into Kiro.
4. Kiro updates ROADMAP_MASTER.md accordingly.
5. ChatGPT + Kiro remain perfectly synchronized.

# 🧩 Core Platform Modules (System Pillars)

This section defines all major functional modules that make up the Second Skies trading platform.  Each module is a long-term pillar of the system, with its own purpose, roadmap phases, UI/UX rebuild needs,  and backend requirements. These modules form the structural backbone of the platform.

---

## 1. ML Intelligence Hub

Purpose: Central hub for AI/ML models, predictions, feature engineering, regime detection, and model monitoring.

Roadmap Phases: 1, 6, 9

UI/UX: Requires complete redesign.

## 2. Main Dashboard

Purpose: High-level operational and trading overview: performance, signals, risk alerts, automation health.

Roadmap Phases: 1, 2, 5

UI/UX: Requires full rebuild.

## 3. Signal Lab (Legacy Dataset V1)

Purpose: Manual dataset creation during Phase 1; now archived.

Roadmap Position: Phase 1 only; read-only legacy.

UI/UX: Minimal updates.

## 4. Automated Signals (Legacy)

Purpose: Original automated signal page; deprecated.

Roadmap Position: Replaced by Automated Signals ULTRA.

## 5. Automated Signals ULTRA (Primary)

Purpose: Real-time automated signal lifecycle engine: confirmations, MFE tracking, BE, SL events.

Roadmap Phases: 2, 4, 5, 6, 9

UI/UX: Needs expansion.

## 6. Time Analysis

Purpose: Session-based performance analysis, time-of-day analytics, volatility regimes.

Roadmap Phases: 1, 2, 6

UI/UX: Requires full rebuild.

## 7. Strategy Optimizer

Purpose: Identify high-performance strategies and parameter sets using historical and automated datasets.

Roadmap Phases: 1, 2, 6, 9

UI/UX: Full rebuild required.

## 8. Compare (Strategy Comparison Engine)

Purpose: Compare strategies, parameter sets, and variations across datasets and sessions.

Roadmap Phases: 1, 6, 9

UI/UX: Full rebuild.

## 9. AI Business Advisor

Purpose: AI agent that understands your business, data, and trading to advise across commercial/trading decisions.

Roadmap Phases: 1 (prototype), 6–10 (full AI integration)

UI/UX: Needs dedicated interface.

## 10. Prop Portfolio

Purpose: Prop-firm account management: scaling, rule validation, breaches, program progression.

Roadmap Phases: 3, 4, 5, 6, 10

UI/UX: Full rebuild.

## 11. Trade Manager

Purpose: Execution engine UI: trade routing, order copying, BE and SL automation, multi-account execution.

Roadmap Phases: 5, 3, 10

UI/UX: Full rebuild.

## 12. Financial Summary

Purpose: Cross-account P&L, firm-level financial analytics, drawdowns, performance reporting.

Roadmap Phases: 1, 2, 10

UI/UX: Full rebuild.

## 13. Reports

Purpose: Operational reporting, accounting integration, audit logs, data exports.

Roadmap Phases: 1, 10

UI/UX: Full rebuild.

## 14. Execution Quality Dashboard (NEW — CRITICAL)

Purpose: Slippage, fill quality, latency, spread conditions, execution drift and reliability.

Roadmap Phases: 5, 6, 8, 10

UI/UX: New module; must be built from scratch.

## 15. Homepage Command Center (NEW — CRITICAL)

**Purpose:**  The Homepage Command Center is the central visual and operational hub of the entire Second Skies trading platform.  It serves as the top-level navigation, the visual roadmap interface, the branding anchor (video background),  and the executive overview for all phases, modules, and system health indicators.

This module integrates roadmap progression, system intelligence, live status, and category-based navigation into a single cohesive UI.

---

### 🌟 Conceptual Role

The Homepage Command Center is not a menu.  It is the *command surface* of the trading ecosystem.

It must:

- Preserve the high-end video background aesthetic  
- Present the Visual Roadmap at the top of the page  
- Display phase and stage progress  
- Provide category-based access to modules  
- Display live system health indicators  
- Reflect automation activity  
- Keep the user oriented within the platform's evolution  
- Scale as new modules and capabilities come online  

---

### 🧩 Core Features

#### 1. Visual Roadmap Integration

- Phase cards (0–10)  
- Status indicators (Complete, Active, Upcoming)  
- Progress bars per phase  
- Expandable stage breakdown  
- Greyed-out locked phases  
- Tooltips explaining each phase  

---

#### 2. Module Category Cards  

Reduce homepage clutter by grouping modules:

**Category 1 — Intelligence**  
- ML Intelligence Hub  
- AI Business Advisor  
- Strategy Optimizer  
- Compare  

**Category 2 — Signals & Execution**  
- Automated Signals ULTRA  
- Trade Manager  

**Category 3 — Analytics**  
- Time Analysis  
- Financial Summary  
- Reports  

**Category 4 — Accounts & Prop Firm**  
- Prop Portfolio  
- Account/Risk engine health  
- Execution queue status  

Each category is a single card that expands to show its modules.

---

#### 3. Live System Health Ribbon

Includes:  
- Webhook health  
- Execution queue depth  
- Risk engine status  
- Last signal timestamp  
- Database latency  
- Account breach status  

---

#### 4. Real-Time Market Context

- Current session  
- Time until next session  
- Basic market condition snapshot  

---

### 🧱 Technical Requirements

Backend:

- Roadmap metadata API  
- System status API  
- Module availability API  
- Live session/time endpoint  
- WebSocket "system health" stream  

Frontend:

- Responsive card layout  
- Video background with gradient overlay  
- Expandable roadmap section  
- Collapsible module category grid  

---

### 🎨 UI/UX Requirements

- Retain video background  
- Apply soft gradient overlay for readability  
- Use clean modern fintech styling  
- Zero clutter, strict hierarchy  
- Animated expand/collapse  
- Unify homepage aesthetic with future modules  

---

### 🔮 Future Expansions

- AI-generated daily summaries  
- Personalized alerts  
- Automatic roadmap state updates  
- Market regime visual overlays  
- Multi-market dashboards  

---

### 📊 Completion Status  

0% — foundational module for Phase 1 rebuild.

---

## Module 16 — Main System Dashboard  

**Status: Implemented**

The Main System Dashboard has been fully rebuilt using the Hybrid Fintech UI System.  It includes:

- Operational Top Bar (automation, risk engine, queue depth, webhook health, latency, session context)  
- Hybrid 55/45 two-column grid (Operational + Analytics)  
- Active Signals, Automation Engine Overview, Prop-Firm Status  
- P&L today, session performance, signal quality, expectancy  
- Distribution analytics (win rate, R-distribution)  
- Lower analytics grid: equity curve, R-heatmap, hour-of-day, session compare  

Responsive layout across desktop/tablet/mobile.  Phase 1 uses mock data; backend integration begins in Phase 2.

---

## Module 17 — Time Analysis  

**Status: Implemented**

The Time Analysis dashboard has been fully rebuilt using the Hybrid Fintech UI System.  It includes:

- Header & metric summary (win rate, expectancy, avg R, total trades, best session)  
- Dataset selector (V1 active, V2 placeholder) and date range selector (placeholder)  
- Session performance grid: heatmap, R-multiple distribution, session win rate and expectancy cards  
- Hour-of-day analytics: win rate histogram, expectancy curve, R-distribution by hour, heatmap overlay  
- Temporal performance curves: equity curve (placeholder), MFE/MAE time decay, trend vs chop, volatility-time curve (placeholders)  
- Insights panel placeholder for future AI-generated commentary (Phase 6–9)

Mock data is used for Phase 1; no backend dependencies yet.  The layout is fully responsive across desktop/tablet/mobile.

---

## Module 18 — Strategy Optimizer  

**Status: Implemented**

The Strategy Optimizer dashboard has been rebuilt using the Hybrid Fintech UI System with a hybrid dual-mode design:

- Configuration Optimizer:
  - Parameter control panel (confirmation type, stop-loss logic, sessions, volatility, time-of-day, R-target ranges)
  - Result panel showing win rate, expectancy, avg R, session performance, R-distribution, equity curve and heatmap placeholders
- Variant Optimizer:
  - Variant cards (Baseline, Conservative, Aggressive, Volatility, Session-focused, NY-only)
  - Comparison panel showing win rate, expectancy, trades, stability, best/worst sessions, and chart placeholders

Phase 1 implementation uses mock data only (no backend calls), with full responsiveness and Hybrid Fintech styling.  Future phases (4, 6, 9) will connect this module to real datasets, ML outputs, and AI insights.

---

## Module 19 — Compare  

**Status: Implemented**

The Compare dashboard has been rebuilt using the Hybrid Fintech UI System with unlimited strategy comparison:

- Add Strategy card UI with modal-based selection from a mock strategy list  
- Horizontally scrollable strategy card deck (unlimited strategies)  
- Each strategy card shows name, winrate, expectancy, avg R, trades, stability, session performance, R-distribution and equity placeholders  
- Multi-strategy comparison charts: expectancy curves, R-distribution, winrate by session, expectancy by session, hour-of-day, stability  
- Delta metrics row comparing strategies (e.g., first vs last selected)  
- Insights panel placeholder for future AI-generated commentary (Phase 6–9)

Phase 1 implementation uses mock data only (no backend calls) with full responsiveness across desktop/tablet/mobile.

---

## Module 20 — ML Intelligence Hub  

**Status: Implemented**

The ML Intelligence Hub has been fully built in Hybrid Fintech UI as a five-region intelligence shell:

- **Region A: High-Level Overview**  
  Market regime, signal quality forecast, volatility outlook, model confidence, strategy recommendation (placeholders)

- **Region B: Model Intelligence**  
  Model accuracy, expected vs delivered performance, feature importance, drift indicator, dataset distribution, model health

- **Region C: Market Intelligence**  
  Regime classifier, regime timeline, expected MFE, expected drawdown, volatility regime, session forecasts

- **Region D: Signal Intelligence**  
  Signal validity forecast, predicted R-distribution, predicted win rate, 24h heatmap, opportunity zones, strategy projections

- **Region E: AI Insights (Phase 6–9 placeholder)**  
  Placeholder card for future AI-generated explanations and risk/strategy narratives

Phase 1 uses mock data only (no backend calls).  
Full responsive implementation with Hybrid Fintech styling.  
Backend integration begins in Phase 4–6 when ML engine comes online.

---

## Module 21 — Financial Summary  

**Status: Implemented**

The Financial Summary dashboard has been rebuilt using the Hybrid Fintech UI System with a hybrid personal + prop portfolio architecture:

**Region A — Global Overview**

- Total P&L  
- Combined R Today  
- Portfolio Drawdown  
- Active Accounts (Eval/Funded)  
- Scaling Opportunity Index  

**Region B — Personal Trading Performance**

- P&L Today (R + $)  
- Equity curve (placeholder)  
- Drawdown curve (placeholder)  
- Session profitability blocks  
- R-distribution  
- Day-type heatmap (placeholder)  

**Region C — Prop Firm Portfolio Performance**

- Prop Account Cards (mock firms, programs, balances, DD, daily loss, status, P&L today, risk indicator)  
- Portfolio aggregation metrics  
- Multi-account equity curve (placeholder)  
- Portfolio R-distribution (placeholder)  
- Correlation matrix (placeholder)  

**Region D — Portfolio Risk & Forecast**

- Risk exposure card  
- Breach probability gauge (placeholder)  
- Forecast panel (placeholder curve)  

Phase 1 uses mock data only (no backend calls) with full responsive Hybrid Fintech styling.  
Backend integration begins across Phases 4–6.

---

## Module 22 — Reporting Center  

**Status: Implemented**

The Reporting Center has been fully built using the Hybrid Fintech UI System with four major category groups:

**Trading Reports**

- Daily, Weekly, Monthly, Year-to-Date, Strategy-Based, Session Reports  
- Summary metrics, equity curve placeholder, drawdown placeholder, R-distribution, HOD histogram  

**Prop Firm Reports**

- Daily loss reports, Max DD reports, Program compliance summaries  
- Scaling history, Funded vs Evaluation overview, Prop P&L summary  
- Multi-account equity and compliance indicators  

**Business & Accounting Reports**

- Tax summary (placeholder), quarterly financials, annual performance, cash flow forecast  
- Income curves, quarterly P&L bars, expense breakdown charts  

**Export Center**

- Mock export buttons (PDF, CSV, Excel) for all report groups  
- Placeholder JS handlers (no backend calls)

Phase 1 uses mock data only (no backend calls) and is fully responsive across all breakpoints.

---

## Module 23 — Automated Signals ULTRA (Full Redesign)  

**Status: Implemented**

Automated Signals ULTRA has been fully redesigned using the Hybrid Terminal + Fintech UI system.  This redesign introduces a five-region architecture suitable for the future automation engine (Phases 2–5),  ML overlays (Phase 6), and AI narrative explanations (Phase 9).

**Region A — Signal Feed Header**  
- Live status, dataset selector, session/date switcher, timestamp  
- Metrics: signals today, confirmed, active trades, Avg R, MFE high

**Region B — Live Signal Feed (Terminal Panel)**  
- Terminal-style animated signal cards  
- Direction badges, session badges, entry/stop  
- Full lifecycle strip: PENDING → CONFIRMED → BE → MFE → EXIT  
- Gradient progress bar (#4C66FF→#8E54FF)

**Region C — Signal Details Panel (Right Slide-Out)**  
- Entry details, full lifecycle timeline  
- Price map (chart placeholder)  
- Signal stats (R, MFE, AE, duration)  
- ML/AI placeholders for future phases

**Region D — Performance Strip (Bottom)**  
- Today's R, Today's P&L, Session P&L  
- MFE high/low, BE triggers, SL events  
- Sparkline placeholder

**Region E — Filters & History Sidebar**  
- Collapsible left panel  
- Filters: session, direction, status, time window, R-range, MFE-range  
- Recent signal history with "load older" (mock)

Phase 1 uses mock data only (no backend calls or websockets).  Fully responsive implementation with zero console errors.  Legacy ULTRA archived under /archive/.

---

# End of Modules 1–14

# 🤖 OpenAI Integration & Safety Protocol

This section defines how OpenAI and other LLM-based AI systems will be integrated into the Second Skies trading platform.  The objective is to clearly separate:

1. AI that can safely be used in trading systems  
2. AI that must never directly control execution  
3. AI roles during different phases of platform evolution  
4. Safety boundaries to prevent model drift or catastrophic error  

This protocol ensures that OpenAI enhances the platform,  but never endangers trading capital or violates deterministic rules.

---

# 🟦 1. AI Categories in the Platform

We distinguish between three types of AI:

## A) Deterministic ML Models (ALLOWED FOR TRADING DECISIONS)

Examples:

- Random Forest  
- Gradient Boosted Trees  
- Neural networks  
- Time-series models  
- Regime classifiers  
- Predictive MFE/MAE models  

Characteristics:

- Deterministic  
- Backtestable  
- Version-controlled  
- Safe for trade decision logic  

Used for:

- Strategy filtering  
- Signal validation  
- Regime classification  
- Probabilistic forecasting  
- Volatility prediction  

---

## B) LLMs (OpenAI/Claude/Gemini) — ALLOWED WITH LIMITS

These are:

- Reasoning engines  
- Language understanding models  
- Pattern interpreters  

They are NOT deterministic and must not drive trades.

LLMs are used for:

- Insight generation  
- Pattern commentary  
- Strategy research  
- Data summarization  
- Market structure description  
- Predictive explanations  
- Business intelligence  
- Risk commentary  
- AI Business Advisor logic  

LLMs supplement analysis,  but do not influence execution.

---

## C) Hybrid AI (Deterministic ML + LLM Reasoning)

Allowed only in future phases.

LLMs may:

- Explain ML predictions  
- Provide reasoning overlays  
- Generate daily briefings  
- Suggest potential improvements  
- Detect unusual conditions (advisory only)

This is safe because:

- ML models make the decisions  
- LLMs merely contextualize them  

Execution remains deterministic.

---

# 🟥 2. AI Safety Rules (Hard Requirements)

These rules prevent catastrophic failures.

## ❌ OpenAI is NOT ALLOWED to:

- Decide trade entries  
- Decide trade exits  
- Modify stop-loss placement  
- Determine pivot points  
- Override ExecutionRouter  
- Compute contract size  
- Trigger or cancel orders  
- Generate numeric trading instructions  
- Modify methodology rules  
- Influence prop-firm rule checks  
- Interact with risk engine  

## ✔ OpenAI IS ALLOWED to:

- Provide narrative explanation  
- Describe structure and patterns  
- Identify contextual market features  
- Summarize data  
- Explain ML signals  
- Offer strategy research insights  
- Generate business intelligence  
- Assist in feature engineering  
- Assist in anomaly detection (advisory only)  

---

# 🟧 3. Integration by Roadmap Phase

## Phase 1 (Manual Era)

- LLM assists interpretation  
- No execution influence  

## Phase 2 (Semi-Automation)

- LLM summarizes automated signals  
- LLM insight-only  

## Phase 3 (Execution & Risk Engine)

- LLM may comment on risk conditions  
- Cannot touch risk logic  

## Phase 4 (Automated Validation)

- LLM may comment on why a signal appears valid  
- Cannot influence confirmation, SL, or pivot logic  

## Phase 5 (Full Automation)

- LLM provides narrative overlays  
- Execution logic remains deterministic  

## Phase 6 (ML Intelligence)

- LLM explains ML outputs  
- Suggests features  
- Helps refine strategies  

## Phase 7–8 (Scaling & Institutional Infra)

- LLM produces operational summaries  
- Assists reporting  

## Phase 9 (Autonomous AI Engine)

- Hybrid model emerges: ML decides, LLM explains  
- LLM still cannot influence execution  

## Phase 10 (Prop Firm Business Layer)

- LLM becomes full business advisor  
- Supports planning, scaling, capital allocation  
- No execution control  

---

# 🟩 4. API & Infrastructure Requirements

- All LLM calls must be sandboxed  
- All calls must be logged  
- All versions must be pinned  
- Execution must NOT depend on LLM availability  
- No time-sensitive logic may use OpenAI  
- LLM failure must never break trading  

---

# 🟨 5. Data Privacy & Confidentiality

OpenAI may receive:

- Summaries  
- Aggregates  
- Contextual descriptions  
- Statistical outputs  

OpenAI may NOT receive:

- Account credentials  
- API keys  
- Live execution signals  
- Position details  
- Edge-revealing proprietary logic  

Where necessary, on-device or private models may replace OpenAI.

---

# 🟫 6. Future Extensions

Possible future LLM components:

- Fine-tuned internal LLM  
- AI journaling agent  
- Regime explainer  
- Automated report generator  
- Strategy research assistant  

Never for execution.

---

# 🟥 7. Summary of Safety Protocol

**OpenAI = reasoning, narrative, insight**  
**ML models = prediction, classification**  
**Deterministic engines = execution, risk, methodology**

This layered separation ensures capital safety, regulatory compliance, and long-term stability of the automation engine.

---

# End of Section

# 🟪 PHASE 0 — FOUNDATIONS (100% COMPLETE)

**Purpose:**  Phase 0 establishes the conceptual and methodological foundation that the entire Second Skies trading platform is built upon.  This is the "philosophy and architecture definition" phase — before any code, dashboards, or automation exists.

## 🎯 Objectives of Phase 0

- Define the exact trading methodology used in the platform  
- Ensure the methodology is written in mechanical, code-ready form  
- Establish the asset class (NASDAQ futures)  
- Establish the timeframe (1-minute primary)  
- Define exact confirmations (bullish and bearish)  
- Define pivot identification (3-candle + 4-candle)  
- Define stop-loss methodology (pivot-based, ±25 points)  
- Define session classification (Asia, London, NY Pre, AM, Lunch, PM)  
- Define R-multiple framework (+1R, +2R… +20R)  
- Establish the rule: "No shortcuts, no simplifications, exact methodology only"  
- Choose cloud-first architecture (TradingView → webhook → Python/Flask → Railway)  
- Identify long-term vision:  
- Automated signals → automated trading → multi-account prop engine → ML intelligence → full autonomy  

## 🧠 Methodology Definition

Phase 0 locked in all trading logic used across all automated systems:

### **1. Signal confirmation logic**  
- Bullish = candle closes above high of signal candle  
- Bearish = candle closes below low of signal candle  
- Entry = open of next candle after confirmation  

### **2. Stop-loss logic**  
- Determine pivot low/high between signal and confirmation  
- If pivot exists within ruleset → SL = pivot ± 25 points  
- If signal candle is pivot → same rule  
- If no pivot → dynamic pivot search logic  

### **3. Break-even logic (BE=1)**  
- Move SL to entry when price reaches +1R  

### **4. Trade classification**  
- Sessions  
- Bias  
- R-multiples  
- MFE  
- MAE  

### **5. No-simplification rule**  
The methodology is sacred.  No assumptions.  No buffer fiction.  No pseudo-signals.  Everything must be implemented EXACTLY as defined.

## 🏗 Architectural Foundation

Phase 0 defined the core platform structure:

- TradingView → webhook ingestion  
- Flask backend  
- PostgreSQL database  
- Cloud deployment (Railway)  
- WebSocket real-time updates  
- Frontend dashboards  
- Execution queue architecture  
- Event-driven signal lifecycle  

## 🌍 Vision Definition

The long-term vision was set explicitly:

1. Manual → semi-automated → fully automated signals  
2. Automated validation engine  
3. Automated trade execution  
4. Predictive ML-based selection engine  
5. Multi-account prop-firm execution  
6. Multi-strategy orchestration  
7. Real-time regime awareness  
8. Full autonomous AI-driven trading engine  
9. Prop-firm style account scaling  
10. Institutional-grade business backend  

## 📌 Completion Status

**Completion:**  ██████████ 100%

Phase 0 is permanently complete.  No further development required in this phase.


# 🟦 PHASE 1 — EXPANSION & UI/UX MODERNIZATION  

**Status: In Progress**  

**Purpose:**  
Transform all early-stage platform modules into a unified, professional-grade Hybrid Fintech interface consistent with the Automated Signals Dashboard ULTRA.  This phase replaces all prototype dashboards with a consistent, scalable design system.

Phase 1 creates the visual and structural foundation for every future phase.

---

# 🎯 Objectives of Phase 1

1. Establish a unified UI design system across all modules  
2. Rebuild every Phase 1 dashboard in the Hybrid Fintech style  
3. Freeze and archive the Legacy Signal Lab (Dataset V1)  
4. Integrate Dataset V2 placeholders for future automated dataset  
5. Prepare each module for future ML + automation integration  
6. Build the Homepage Command Center (Module 15)  
7. Clean navigation and module grouping  
8. Ensure accessibility, responsiveness, and clarity  
9. Eliminate legacy layouts and placeholder blocks  
10. Ensure every future patch has a stable UI system to build on  

---

# 🎨 Unified Hybrid Fintech UI System (Phase 1 Core Deliverable)

## Colors  

- Background: #0D0E12  
- Cards: #14161C / #1A1C22  
- Accent: Electric blue → Indigo (#4C66FF → #8E54FF)  
- Secondary: Cyan (#00D1FF)  
- Text: #F2F3F5  
- Muted: #9CA3AF  
- Borders: 0.1–0.2 opacity lines  

## Typography  

Primary font: Satoshi (fallback Inter with tighter letter spacing)  
Style: clean, modern, institutional.

## Components  

- Cards  
- Metric Blocks  
- Status Ribbons  
- Section Headers  
- Pill Tabs  
- Dark Tables  
- Progress Bars  
- Roadmap Cards  
- Category Cards  
- Minimal monochrome icons  
- Light glass overlays  
- Notification toasts  

## Grid & Layout  

- 12-column grid  
- 24px spacing  
- 48px section spacing  
- 80px hero padding  
- Collapsible sidebar nav  
- Optional sticky status ribbon  

## Motion  

- 150–250ms transitions  
- Micro-animations  
- Hover elevation  
- Expand/collapse animation  

---

# 🧱 Phase 1 Module Rebuilds

## 1. ML Intelligence Hub — Rebuild  

## 2. Main Dashboard — Rebuild  

## 3. Time Analysis — Rebuild  

## 4. Strategy Optimizer — Rebuild  

## 5. Compare — Rebuild  

## 6. Financial Summary — Rebuild  

## 7. Reports — Rebuild  

## 8. Homepage Command Center — Build  

## 9. Automated Signals ULTRA — Polish  

## 10. Legacy Signal Lab — Freeze (Dataset V1)

---

# ⛓ Backend/API Adjustments

- Dashboard endpoint consolidation  
- UI-ready formatting  
- System status API  
- Module availability metadata  
- Dataset V2 placeholder schema  
- ML Hub cleanup  

---

# 📊 Phase 1 Completion Criteria

Phase 1 is complete when:

1. All dashboards rebuilt  
2. Homepage Command Center operational  
3. Navigation unified  
4. Legacy SignalLab archived (V1)  
5. Automated Signals ULTRA polished  
6. UI system unified globally  
7. Roadmap + homepage synced  
8. Platform stable for Phase 2  

# Phase Status  

Current: **In Progress**

---

# 🟦 PHASE 2C.1 — DATA ACCUMULATION & SYSTEM CALIBRATION WINDOW  

**Status: Planned**  

**Purpose:** Allow the platform to ingest enough real-time Dataset V2 signals to build statistical reliability, confirm ingestion stability, validate lifecycle accuracy, and ensure dashboards reflect true performance before Phase 2.5 evaluations begin.

This window ensures confidence, stability, and psychological readiness.

---

## 🎯 Objectives of Phase 2C.1

1. Build a fresh Dataset V2 from normalized live signals  
2. Validate lifecycle flow (ENTRY → CONFIRMED → BE → MFE → EXIT)  
3. Confirm ULTRA terminal accuracy under real live conditions  
4. Populate Time Analysis with meaningful session & time-of-day data  
5. Populate Financial Summary with realistic daily/weekly P&L  
6. Produce reliable R-distribution, MFE/AE metrics, and expectancy baselines  
7. Detect ingestion anomalies early (missing fields, malformed events)  
8. Strengthen trader confidence before evaluations (Phase 2.5)

---

## ⏳ Recommended Duration

**2–4 weeks of live data ingestion**, or  
**a statistically meaningful number of live signals**, whichever comes first.

During this window:

- No automation is active  
- Manual execution environment is being prepared  
- All components must be stable and accurate  

---

## 🔧 Platform Tasks During Phase 2C.1

- Fix minor UI/UX polish across rebuilt dashboards  
- Validate signal timestamps and session classification  
- Refine lifecycle mapping and ordering  
- Validate polling stability and error handling  
- Confirm backend ingestion behaves predictably under load  
- Verify P&L and stats calculations  
- Improve dashboard clarity based on real data  
- Add log visibility where needed  
- Prepare evaluation workflow for Phase 2.5  

---

## 🧘 Psychological & Operational Readiness

Phase 2C.1 supports trader discipline:

- Daily review routine  
- Signal quality review  
- Session pattern observation  
- Performance calibration  
- Mental preparation for evaluation trading  
- Trust-building between trader and system  

---

## 🧩 Completion Criteria for Phase 2C.1

Phase 2C.1 is complete when:

1. Dataset V2 contains meaningful, recent real-world signals  
2. ULTRA displays accurate, real-time lifecycle events  
3. Dashboards show statistically reliable metrics  
4. No ingestion errors appear in logs  
5. No lifecycle ordering anomalies occur  
6. Performance strip aligns with true session results  
7. Session/Time-of-Day patterns stabilize  
8. You have subjective confidence in the system  
9. Platform is proven stable under daily live usage  
10. Trader is psychologically ready to begin Phase 2.5

---

# 🟩 PHASE 2.5 — PROP EVALUATION & CONSISTENCY BASE  

**Status: Planned**  

**Purpose:** Establish consistent profitability as a manual trader, pass prop firm evaluations, generate initial business income, and create the capital foundation necessary for future scaling and automation.

This phase represents the FIRST REAL MONEY PHASE of the business.

---

## 🎯 Objectives of Phase 2.5

1. Achieve consistent manual trading performance  
2. Pass initial prop firm evaluations (1–3 evaluations)  
3. Build psychological confidence in live trading  
4. Generate first payouts for the business  
5. Activate evaluation pipeline with wave stacking  
6. Establish real account growth & capital base  
7. Automation remains OFF during this phase  
8. Platform supports evaluation tracking & discipline routines  

---

## 🧱 Structure of Phase 2.5

### 1. Manual Strategy Lock-In

- Finalize the strategy used for live evaluations  
- Use ULTRA + dashboards to reinforce consistency  
- Define: entry → confirmation → SL → BE → MFE rules  

### 2. Evaluation Pipeline (Wave System)

**Wave 1 (Foundation):**
- 1–3 evaluations  
- Pass sequentially or in parallel  

**Wave 2 (Growth):**
- Scale early funded accounts  
- Add more evaluations  

**Wave 3 (Portfolio Build):**
- 5–10 funded accounts  
- Semi-automated assistance later  

---

## 📊 Platform Integration

- Evaluation progress tracking  
- Daily performance view  
- Prop-firm rule compliance status  
- DD / daily loss tracking  
- Session performance  
- Journaling / consistency notes  

---

## 💰 Business Transition

Phase 2.5 is the FIRST phase where:
- The business earns real income  
- Manual trading proves the business model  
- Consistency becomes measurable  
- Capital for scaling is created  
- Future automation has a financial base  

---

## 🧩 Phase 2.5 Completion Criteria

1. First evaluation passed  
2. Minimum 2–3 evaluations attempted  
3. At least 1 active funded account  
4. First payout achieved  
5. Manual strategy validated under real conditions  
6. Evaluation pipeline operational  
7. Confidence in live trading  
8. Capital allocation strategy activated  
9. Automation remains OFF until Phase 3+


---

# 💎 WEALTH ARCHITECTURE & STRATEGIC CAPITAL ALLOCATION  

**Purpose:** Convert trading performance into long-term wealth, stable income, SMSF growth, and property/investment accumulation through an AI-assisted financial framework.

This section is a PERMANENT part of the long-term roadmap.

---

# 🎯 Goals

1. Build a sustainable, growing prop-firm portfolio  
2. Create stable income streams  
3. Optimize for tax + SMSF + wealth preservation  
4. Allocate profits across income, reinvestment, and wealth  
5. Build property and investment asset base  
6. Maintain business runway and operational buffers  

---

# 💰 Capital Flow Framework (per payout)

### 1. Personal Income Stream  

- Monthly salary drawn from trading profits  

### 2. Business Retained Earnings  

- Evaluation fees  
- Scaling funded accounts  
- Infrastructure & automation  
- Buffer capital  

### 3. Wealth Building (SMSF + Property)  

- SMSF contributions  
- Property investment  
- Long-term asset growth  
- Trust or corporate structure (future)  

### 4. Tax Allocation Reserve  

- Income tax buffer  
- SMSF tax  
- Accounting provisions  

---

# 🧠 Role of AI Business Advisor (Phase 7–10)

AI Advisor will eventually:
- Model payout cycles vs scaling opportunities  
- Suggest optimal tax-efficient strategies  
- Forecast SMSF + property growth  
- Optimize income distribution  
- Recommend prop-firm allocation  
- Track long-term wealth progression  
- Provide business-level decision intelligence  

---

# 🔄 Capital Scaling Waves

**Wave 1:** 1–3 funded accounts, initial income  
**Wave 2:** 5–10 accounts, stability  
**Wave 3:** automation + property/SMSF growth  
**Wave 4:** institutional-grade trading business  

---

# 📊 Wealth Architecture Activation Criteria

1. First funded withdrawal completed  
2. Capital allocation model defined and active  
3. Income rules established  
4. SMSF contribution logic active  
5. Property investment timeline started  
6. AI Advisor integrated in Phase 7+  
7. Prop-firm portfolio scaling routine operational  
8. Monthly cashflow stability achieved  


---

# 💞 PARTNER COMMUNICATION & REVIEW CADENCE  

**Purpose:** Ensure clear communication, visibility, alignment, and shared ownership of the Second Skies project between both business partners.  This cadence strengthens trust, transparency, accountability, and shared strategic vision.

---

# 📆 Monthly Review Rhythm

**1. Monthly Strategic Review (MSR)**  

A structured review at the end of each month covering:  

- Phase progress completed  
- What has been built  
- Demonstrations of new modules  
- Any improvements or fixes  
- What's next on the roadmap  
- Financial status & capital plan  
- Business outlook and goals  

**Outcome:** Shared alignment + confidence in direction.

---

# 🎉 Milestone Showcases

**Showcases happen at the completion of each major module, including:**  

- ULTRA updates  
- Time Analysis enhancements  
- Dashboard rebuilds  
- New risk logic  
- New ML or AI systems  
- Integration with real signals  
- Prop evaluation wave completions  
- Automation breakthroughs  

Each showcase includes a walk-through of:  

- What was built  
- Why it matters  
- How it contributes to the long-term business vision

**Outcome:** Celebrating wins + maintaining excitement.

---

# 🔔 Partner Alert Checkpoints

Trigger a partner update when:  

- A Phase completes (Phase 1, 2A, 2.5, etc.)  
- A new evaluation is started  
- An evaluation is passed  
- A funded account becomes active  
- A payout occurs  
- A scaling wave begins  
- Any major architectural change is proposed  
- Roadmap is updated  

**Outcome:** Ensures both partners stay informed & empowered.

---

# 🧭 Weekly Sync (Optional)

Short 15–20 minute weekly check-in:  

- What's happening this week  
- What's been done  
- Any blockers  
- Questions or ideas  
- Emotional/psychological check-in  

**Outcome:** Tight feedback loops + emotional support for the journey.

---

# 💡 Business Partner Feedback Loop

Your business partner can provide structured input on:  

- Priorities  
- Feature requirements  
- UX preferences  
- Business direction  
- Capital allocation decisions  
- Prop scaling waves  
- Wealth strategy  
- Lifestyle priorities  

Her feedback is treated as an **input to the roadmap**, and new items are integrated accordingly.

---

# ✨ Communication Principles

1. **Transparency** — Open progress reports, clear communication.  
2. **Inclusion** — She is included in all major decisions.  
3. **Visibility** — She sees everything meaningful that is built.  
4. **Celebration** — Wins and milestones are celebrated together.  
5. **Alignment** — Decisions reflect shared goals & values.  

---

# 📌 Partner Communication Is a Permanent Roadmap Layer

This is NOT optional.  It is an essential part of the business functioning properly, ensuring:

- shared vision  
- shared excitement  
- shared confidence  
- shared ownership  
- shared success  

The project becomes something **built together**, not alone.

---

# 🛡️ ENGINEERING VALIDATION & REPO SYNC GUARDRAILS  

**Purpose:** Ensure every patch, upgrade, or multi-file implementation is validated, complete, and correctly synchronized to the local Windows Git repository to prevent broken deployments caused by empty files, missed changes, and partial updates.

These guardrails form part of the core engineering process for Second Skies.

---

## 🔍 1. The Phase Validation Protocol (Mandatory After Every Patch)

After *every* Kiro implementation, regardless of size:

### **A. Run Phase Validation Prompt**

This checks:
- all target files  
- missing logic  
- mock data remnants  
- missing functions  
- incorrect imports  
- JS/HTML mismatches  
- broken backend routes  
- partial Kiro implementations  
- inconsistencies between phases  

### **B. If validation fails → run Corrective Patch**

No proceeding until validation returns:

> **PHASE VALID — FULLY IMPLEMENTED**

This step prevented multiple major production failures and is now *permanent*.

---

## 🧱 2. File Integrity Check (Pre-Deployment Safety Step)

Before deployment, for *each modified file*:

Run in Kiro:

STRICT KIRO MODE — FILE CONTENT EXPORT  

Please print the FULL contents of <filename> exactly as it exists in your workspace.

This verifies:
- file has REAL content  
- file is not partially created  
- no 0-byte files  
- no missing logic due to Kiro session resets  
- the Windows repo version matches Kiro's cloud workspace version  

---

## 💾 3. Windows Repo Synchronization Protocol

Because Kiro works inside a **cloud workspace** and GitHub Desktop watches a **local Windows folder**, synchronization errors can occur.

To prevent this:

### Before committing:

- Verify the file content printed by Kiro  
- Confirm that the Windows file matches it  
- If needed, copy/paste Kiro's version into Windows manually  
- Save the file  
- Confirm GitHub Desktop now sees it under "Changes"  

### Only THEN:

- Stage  
- Commit  
- Push  
- Let Railway auto-deploy  

This prevents:
- 0-byte file deployments  
- empty modules  
- import crashes  
- missing patches  

---

## 🧪 4. Pre-Deploy Sanity Check

Before pressing "Push origin":

Confirm:
- All expected files appear in GitHub Desktop  
- No unexpected files are empty  
- No missing modules  
- No untracked files  
- All roadmap updates included  
- No accidental reverts  

---

## 🔥 5. Final Production Readiness Checklist

A patch CANNOT deploy to Railway until:

- Validation Passes  
- File Content Export matches Windows copy  
- GitHub Desktop shows correct tracked changes  
- Kiro confirms no missing components  
- No 0-byte files exist  
- No empty modules exist  
- No incomplete feature sets remain  
- Roadmap updated if required  

---

## 🧠 6. Why These Guardrails Exist

To prevent:
- Crashes caused by incomplete modules  
- Empty files committed by mistake  
- Kiro session interruptions  
- Silently skipped logic  
- Incorrect assumptions about file syncing  
- GitHub Desktop deploying stale or empty code  
- Broken production environments  
- Regression in critical systems (ULTRA, ingestion, routing, ML)  

These guardrails ensure:
- production stability  
- consistent development  
- accurate deployments  
- safe automation growth  
- reliable data flow  
- confidence in live trading phases  

---

## 🟩 7. Permanent Rule  

**Every future feature, module, patch, roadmap update, or release MUST use these guardrails.**

This is now a permanent engineering discipline for the Second Skies platform.

---

# 🚀 SECOND SKIES TRADING FUND
**Core Capital Growth Engine**

A top-level roadmap pillar

Purpose:
To create a self-sustaining, scalable trading capital engine independent of prop-firm rules, capable of compounding aggressively over time using the NQ strategy as its foundational alpha source.

This Trading Fund operates parallel to:
- Prop firm accounts (external scaling engine)
- The Second Skies Capital Fund (long-term wealth engine)

Together, these form the tri-engine financial model:
1. Prop Firm Scaling (external leverage engine)
2. Second Skies Trading Fund (core compounding engine)
3. Second Skies Capital Fund (long-term investment engine)

---

## 🎯 Strategic Goals

- Build a **central trading capital pool** under your control
- Grow capital without prop-firm restrictions
- Eliminate daily loss limits and arbitrary rules
- Scale position sizing based on your own risk rules
- Enable multi-strategy execution long-term
- Become the primary source of trading income
- Free yourself from reliance on external capital providers

---

## 🧠 Why This Fund Matters

Prop firms provide:
- leverage
- scaling acceleration
- income events

BUT they are **rule-constrained**.

The Second Skies Trading Fund:
- is NOT rule-restricted
- is controlled entirely by you
- scales without cap
- compounds faster
- becomes the heart of the business

---

## 🧱 Trading Fund Structure

### Phase 1 — NQ Only (Your Strongest Alpha Source)
- 1m timeframe
- Defined rules: entry → confirmation → BE → MFE → exit
- Session-specific alpha structure
- Time-of-day windows
- Stable, repeatable execution
- Hard-coded risk rules

### Phase 2 — Multi-Account Internal Execution
- Trade the same strategy across multiple sub-accounts
- Risk allocation engine assigns capital dynamically

### Phase 3 — Multi-Strategy Expansion
- Add S/T breakout, reversal, volatility compression
- Add session-based sub-strategies
- Add ML-driven regime awareness

---

## 💰 Profit Flows INTO the Trading Fund

Every prop-firm payout contributes a % to:
- Second Skies Trading Fund (scaling capital)
- Second Skies Capital Fund (long-term wealth)
- Personal Income (lifestyle)

This ensures:
- growth
- safety
- sustainability

---

## 📈 Long-Term Vision

The Trading Fund becomes:
- your main trading income
- your scalable compounding engine
- your hedge-fund-like portfolio
- your platform's showcase
- the foundation of full-time independence

---

## 🔒 Risk Framework (Initial Version)

- 1R fixed per trade
- Max 3R session drawdown
- Max 2-loss streak rule
- No trading during low expectancy windows
- Strict session filters
- 3-tier volatility rule
- Daily review inside dashboards

A more advanced version comes in Phase 7.

---

## 📊 Metrics Used to Run the Trading Fund

Powered by:
- ULTRA (signal lifecycle engine)
- Time Analysis (session/TOD edge)
- Financial Summary (performance data)
- Reporting (daily/weekly analytics)
- ML Hub (future confidence scoring)

---

## 🧩 Activation Requirements (Before Trading It)

The Trading Fund becomes active only once:
1. Dataset V2 has significant real data
2. ULTRA lifecycle is stable
3. Phase 2.5 evaluations prove consistency
4. Dashboard metrics are reliable
5. Phase 3–6 automation pieces are complete

Activation happens in **Phase 7**.

---

# 🔥 PHASE 7 — SECOND SKIES TRADING FUND AUTOMATION
**The Execution Engine Phase**

Purpose:
Automate execution of the NQ strategy for the internal Second Skies Trading Fund, using validated real-time signals, ML-assisted regime awareness, and strict risk control.

This is the phase where the platform becomes a **self-operating trading machine**.

---

## 🎯 Objectives

1. Execute trades automatically in the Trading Fund
2. Scale capital dynamically
3. Use the automated risk engine for protection
4. Use ML regime detection for position sizing
5. Allow strategies to compete for capital
6. Track and adjust performance in real-time
7. Begin multi-account internal execution

---

## 🧩 Core Components Required (Completed in earlier phases)

- ULTRA lifecycle engine
- Automated validation engine (Phase 4)
- Execution router (Phase 5)
- Risk engine enforcement (Phase 6)
- ML confidence overlays (Phase 6)
- Strategy evaluation pipeline (Phase 6)

Phase 7 ties these into a unified automated trading system.

---

## 🚀 Trading Fund Operations in Phase 7

### ✔ Automated Entry & Exit
Based on:
- normalized signals
- lifecycle state
- validated rule engine
- risk engine checks

### ✔ Multi-Account Internal Execution
The execution router commands:
- Trading Fund master account
- Trading Fund sub-accounts
- Scaling pools

### ✔ ML-Assisted Position Sizing
Models provide:
- regime classification
- expectancy adjustment
- volatility buckets
- confidence weighting

### ✔ Capital Allocation
Strategies with superior performance get more capital.
Poor performers decrease in weight.

### ✔ Risk Engine Autonomous Control
- daily loss safeguards
- session drawdown limits
- exposure limits
- volatility filters
- automatic trade disabling when needed

### ✔ Real-Time Monitoring
Dashboards show:
- realized P&L
- active exposure
- performance attribution
- account health
- strategy drift detection

---

## 🧱 Completion Criteria

Phase 7 is complete when the Trading Fund can:
1. Execute trades automatically
2. Adjust position size using ML or risk rules
3. Scale capital dynamically
4. Operate with zero manual intervention
5. Produce consistent, trackable returns
6. Maintain full risk compliance
7. Integrate into the unified wealth architecture

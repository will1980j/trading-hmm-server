# 📊 DATA QUALITY SYSTEM - COMPLETE SPECIFICATION

**Status:** Ready for Implementation
**Date:** December 14, 2025
**Location:** Automated Signals Dashboard - Tab 3

---

## 🎯 SYSTEM OVERVIEW

### Purpose
Ensure 100% signal coverage and data accuracy through automated daily reconciliation between indicator (source of truth) and real-time webhooks.

### Components
1. **Frontend:** Data Quality tab on Automated Signals Dashboard
2. **Backend APIs:** Data quality metrics, conflict resolution, reconciliation
3. **Services:** Daily export service, nightly reconciliation engine
4. **Database:** Reconciliation logs, conflict tracking

---

## 📋 DATABASE SCHEMA

### New Tables

#### 1. `data_quality_reconciliations`
```sql
CREATE TABLE data_quality_reconciliations (
    id SERIAL PRIMARY KEY,
    reconciliation_date DATE NOT NULL,
    reconciliation_time TIMESTAMP NOT NULL,
    signals_in_indicator INTEGER NOT NULL,
    signals_in_database INTEGER NOT NULL,
    missing_signals INTEGER DEFAULT 0,
    incomplete_signals INTEGER DEFAULT 0,
    mfe_mismatches INTEGER DEFAULT 0,
    conflicts_requiring_review INTEGER DEFAULT 0,
    auto_resolved INTEGER DEFAULT 0,
    webhook_success_rate DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'complete',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `data_quality_conflicts`
```sql
CREATE TABLE data_quality_conflicts (
    id SERIAL PRIMARY KEY,
    reconciliation_id INTEGER REFERENCES data_quality_reconciliations(id),
    trade_id VARCHAR(50) NOT NULL,
    conflict_type VARCHAR(50) NOT NULL,
    webhook_value TEXT,
    indicator_value TEXT,
    field_name VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'pending',
    resolution VARCHAR(20),
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. `data_quality_metrics`
```sql
CREATE TABLE data_quality_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    webhook_success_rate DECIMAL(5,2),
    signals_captured INTEGER,
    signals_missed INTEGER,
    avg_reconciliation_time INTEGER,
    system_health VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔌 API ENDPOINTS

### 1. Data Quality Overview
```
GET /api/data-quality/overview
Response: {
    last_sync: "2025-12-14T15:35:00",
    status: "healthy",
    webhook_success_rate: 98.5,
    signals_today: 47,
    gaps_filled: 1,
    conflicts_pending: 2
}
```

### 2. System Health Status
```
GET /api/data-quality/health
Response: {
    webhooks: {status: "active", last_received: "2m ago"},
    daily_export: {status: "scheduled", next_run: "3:30 PM ET"},
    reconciliation: {status: "complete", last_run: "11:00 PM ET"},
    next_sync: "4h 25m"
}
```

### 3. Conflicts List
```
GET /api/data-quality/conflicts?status=pending
Response: {
    conflicts: [
        {
            id: 123,
            trade_id: "20251214_093000000_BULLISH",
            conflict_type: "mfe_mismatch",
            webhook_value: "5.2",
            indicator_value: "5.8",
            field_name: "no_be_mfe",
            severity: "medium"
        }
    ]
}
```

### 4. Resolve Conflict
```
POST /api/data-quality/resolve
Body: {
    conflict_id: 123,
    resolution: "trust_indicator"
}
Response: {
    success: true,
    updated_value: "5.8",
    message: "Conflict resolved, database updated"
}
```

### 5. Gap Analysis
```
GET /api/data-quality/gaps?date=2025-12-14
Response: {
    missing_signals: [
        {
            trade_id: "20251214_140000000_BULLISH",
            source: "indicator",
            auto_filled: true,
            filled_at: "2025-12-14T23:05:00"
        }
    ]
}
```

### 6. Historical Metrics
```
GET /api/data-quality/metrics?days=30
Response: {
    metrics: [
        {date: "2025-12-14", success_rate: 98.5, signals: 47},
        {date: "2025-12-13", success_rate: 100.0, signals: 52}
    ],
    average: 97.8,
    best_day: {date: "2025-12-10", rate: 100.0},
    worst_day: {date: "2025-12-05", rate: 92.3}
}
```

### 7. Reconciliation Log
```
GET /api/data-quality/reconciliations?limit=10
Response: {
    reconciliations: [
        {
            date: "2025-12-14",
            time: "23:00",
            status: "complete",
            signals: "47/48",
            gaps_filled: 1,
            mfe_updated: 2,
            conflicts: 0
        }
    ]
}
```

### 8. Trigger Manual Reconciliation
```
POST /api/data-quality/reconcile
Response: {
    success: true,
    job_id: "rec_20251214_153000",
    message: "Reconciliation started"
}
```

---

## 🤖 BACKEND SERVICES

### 1. Daily Export Service
**File:** `services/daily_export_service.py`

```python
class DailyExportService:
    def __init__(self):
        self.export_time = "15:30"  # 3:30 PM ET
        
    def run(self):
        # 1. Check if market day (Mon-Fri)
        # 2. Wait for 3:30 PM ET
        # 3. Monitor indicator export endpoint
        # 4. Store exported data in temporary table
        # 5. Mark as ready for reconciliation
        # 6. Log export completion
```

### 2. Reconciliation Engine
**File:** `services/reconciliation_engine.py`

```python
class ReconciliationEngine:
    def __init__(self):
        self.reconciliation_time = "23:00"  # 11:00 PM ET
        
    def run(self):
        # 1. Get today's indicator export
        # 2. Get today's webhook signals
        # 3. Compare and identify discrepancies
        # 4. Apply auto-resolution rules
        # 5. Flag conflicts for review
        # 6. Update database
        # 7. Generate reconciliation record
        # 8. Calculate metrics
        
    def auto_resolve(self, conflict):
        # Apply resolution rules
        # Return: resolved=True/False
```

### 3. Conflict Resolver
**File:** `services/conflict_resolver.py`

```python
class ConflictResolver:
    RULES = {
        'missing_signal': 'auto_fill',
        'missing_field': 'auto_fill',
        'mfe_mismatch_small': 'trust_indicator',
        'mfe_mismatch_large': 'require_review',
        'timestamp_mismatch': 'trust_indicator',
        'direction_mismatch': 'critical_review'
    }
    
    def resolve(self, conflict, resolution=None):
        # Apply resolution
        # Update database
        # Log resolution
```

---

## 🎨 FRONTEND COMPONENTS

### Tab Navigation
```html
<div class="tab-navigation">
    <button class="tab-btn active" data-tab="confirmed">Confirmed Signals</button>
    <button class="tab-btn" data-tab="all-signals">All Signals</button>
    <button class="tab-btn" data-tab="data-quality">Data Quality</button>
</div>
```

### Data Quality Tab Sections
1. System Health Overview (always visible)
2. Real-Time Monitoring (status indicators)
3. Conflicts Requiring Review (expandable)
4. Gap Analysis (expandable)
5. Historical Metrics (chart)
6. Reconciliation Log (table)

---

## 🔄 DATA FLOW

### Daily Workflow
```
3:30 PM ET: Daily Export Service
    ↓
    Monitor /api/indicator-inspector/summary
    ↓
    Wait for export completion
    ↓
    Store in temporary table
    ↓
11:00 PM ET: Reconciliation Engine
    ↓
    Compare indicator vs database
    ↓
    Apply auto-resolution rules
    ↓
    Flag conflicts
    ↓
    Update database
    ↓
    Generate metrics
    ↓
Next Morning: User Reviews Dashboard
```

### Conflict Resolution Flow
```
User opens Data Quality tab
    ↓
    Sees conflicts list
    ↓
    Clicks "Trust Indicator" button
    ↓
    POST /api/data-quality/resolve
    ↓
    Backend updates database
    ↓
    Frontend refreshes
    ↓
    Conflict removed from list
```

---

## ✅ AUTO-RESOLUTION RULES

### Rule 1: Missing Signal
```python
if signal in indicator and signal not in database:
    action = "auto_fill"
    severity = "low"
    review_required = False
```

### Rule 2: Missing Field
```python
if signal.entry_price is None and indicator.entry_price is not None:
    action = "auto_fill"
    severity = "low"
    review_required = False
```

### Rule 3: Small MFE Mismatch
```python
if abs(webhook.mfe - indicator.mfe) < 0.5:
    action = "trust_indicator"
    severity = "low"
    review_required = False
```

### Rule 4: Large MFE Mismatch
```python
if abs(webhook.mfe - indicator.mfe) >= 0.5:
    action = "flag_for_review"
    severity = "medium"
    review_required = True
```

### Rule 5: Direction Mismatch
```python
if webhook.direction != indicator.direction:
    action = "critical_review"
    severity = "critical"
    review_required = True
    alert = True
```

---

## 📊 METRICS TRACKED

### Daily Metrics
- Webhook success rate (%)
- Signals captured vs missed
- Gaps auto-filled
- Conflicts requiring review
- Average reconciliation time

### Weekly Metrics
- 7-day webhook success rate trend
- Total gaps filled
- Total conflicts resolved
- System uptime

### Monthly Metrics
- 30-day quality score
- Best/worst days
- Improvement trends
- System reliability

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Database & APIs (Day 1)
- Create database tables
- Build API endpoints
- Test API responses

### Phase 2: Backend Services (Day 2)
- Build daily export service
- Build reconciliation engine
- Build conflict resolver
- Test automation

### Phase 3: Frontend Tab (Day 3)
- Add Data Quality tab
- Build UI components
- Connect to APIs
- Test user workflows

### Phase 4: Integration & Testing (Day 4)
- End-to-end testing
- Validate auto-resolution
- Test conflict resolution
- Performance testing

---

## 📝 DEPLOYMENT CHECKLIST

- [ ] Database migrations run
- [ ] API endpoints registered
- [ ] Services deployed
- [ ] Frontend tab added
- [ ] Cron jobs scheduled
- [ ] Monitoring enabled
- [ ] Documentation updated
- [ ] User training completed

---

**Ready to implement. All dependencies mapped. All APIs defined. All flows documented.**

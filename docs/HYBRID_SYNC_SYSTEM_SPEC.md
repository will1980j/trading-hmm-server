# Hybrid Backend-Indicator Synchronization System
## Enterprise-Grade Self-Healing Signal Tracking

---

## Vision

**Zero data gaps. Ever.**

A collaborative system where backend and indicator work together to ensure every signal has complete, accurate data at all times. The system automatically detects gaps, fills missing data, and self-heals without manual intervention.

---

## Core Principles

1. **Backend is Source of Truth** - Database has authoritative record
2. **Indicator is Real-Time Engine** - Provides live calculations
3. **Automatic Gap Detection** - System identifies missing data
4. **Self-Healing** - Gaps filled automatically
5. **Non-Destructive** - Never overwrites good data
6. **Auditable** - All operations logged and traceable

---

## System Components

### **1. Backend Sync Engine**

**Responsibilities:**
- Maintain complete signal registry
- Detect data gaps
- Calculate synthetic data when needed
- Coordinate with indicator
- Monitor system health

**Key Functions:**
```python
def detect_gaps():
    """Identify signals with missing/stale data"""
    
def calculate_synthetic_mfe():
    """Calculate MFE from entry/stop/price when indicator data unavailable"""
    
def request_indicator_update():
    """Ask indicator to send update for specific signal"""
    
def validate_data_completeness():
    """Check every signal has all required fields"""
```

### **2. Indicator Sync Client**

**Responsibilities:**
- Send real-time updates
- Respond to backend requests
- Report tracking status
- Handle sync commands

**Key Functions:**
```pinescript
f_sendSyncStatus():
    """Report which signals are being tracked"""
    
f_handleSyncRequest():
    """Process backend request for specific signal update"""
    
f_sendFullSnapshot():
    """Send complete state of all tracked signals"""
```

### **3. Gap Detection Service**

**Runs every 2 minutes, checks:**

**Missing MFE Updates:**
```sql
SELECT trade_id FROM automated_signals
WHERE event_type = 'ENTRY'
AND trade_id NOT IN (
    SELECT trade_id FROM automated_signals
    WHERE event_type = 'MFE_UPDATE'
    AND timestamp > NOW() - INTERVAL '10 minutes'
)
AND trade_id NOT IN (
    SELECT trade_id FROM automated_signals
    WHERE event_type LIKE 'EXIT_%'
)
```

**Missing ENTRY Fields:**
```sql
SELECT trade_id FROM automated_signals
WHERE event_type = 'ENTRY'
AND (entry_price IS NULL OR stop_loss IS NULL OR session IS NULL)
```

**Missing MAE:**
```sql
SELECT trade_id FROM automated_signals
WHERE event_type = 'MFE_UPDATE'
AND mae_global_r IS NULL
```

**Stale Data:**
```sql
SELECT trade_id, MAX(timestamp) as last_update
FROM automated_signals
WHERE event_type = 'MFE_UPDATE'
GROUP BY trade_id
HAVING MAX(timestamp) < NOW() - INTERVAL '15 minutes'
```

### **4. Data Filling Strategies**

**Priority 1: Request from Indicator**
- Backend asks indicator to send update
- Indicator responds with current data
- Most accurate method

**Priority 2: Calculate from Database**
- Use existing ENTRY data
- Calculate MFE from current price
- Mark as "calculated"

**Priority 3: Estimate Conservatively**
- Use safe defaults (MFE=0, MAE=0)
- Mark as "estimated"
- Flag for manual review

### **5. Communication Protocol**

**Message Types:**

**Indicator → Backend:**
```json
{
  "type": "HEARTBEAT",
  "tracked_signals": 45,
  "indicator_version": "1.0.0",
  "timestamp": "2025-12-11T10:00:00"
}
```

```json
{
  "type": "SYNC_STATUS",
  "tracking": ["20251211_100400000_BULLISH", "..."],
  "not_tracking": ["20251211_055900000_BEARISH", "..."]
}
```

**Backend → Indicator:**
```json
{
  "type": "SYNC_REQUEST",
  "signals": ["20251211_055900000_BEARISH"],
  "reason": "missing_mfe_update"
}
```

```json
{
  "type": "FULL_SYNC_REQUEST",
  "reason": "gap_detected"
}
```

### **6. Self-Healing Workflows**

**Scenario 1: Indicator Restart**
```
1. Indicator starts → Sends HEARTBEAT with tracked_signals=0
2. Backend detects → Responds with active signal list
3. Indicator receives → Rebuilds arrays from list
4. Indicator confirms → Sends SYNC_STATUS
5. Backend validates → All signals now tracked
```

**Scenario 2: Missing MFE Update**
```
1. Backend detects → Signal has no MFE_UPDATE in 10 min
2. Backend checks → Is indicator tracking this signal?
3. If YES → Send SYNC_REQUEST to indicator
4. If NO → Calculate synthetic MFE, insert with "reconciled" flag
5. Backend monitors → Verify gap filled
```

**Scenario 3: Data Corruption**
```
1. Backend detects → MFE value seems wrong (negative, too high)
2. Backend validates → Check against entry/stop constraints
3. Backend requests → Fresh update from indicator
4. Backend compares → Indicator vs calculated value
5. Backend resolves → Use most reliable source
```

**Scenario 4: Indicator Offline**
```
1. Backend detects → No HEARTBEAT in 5 minutes
2. Backend activates → Full reconciliation mode
3. Backend calculates → Synthetic MFE for all active signals
4. Backend monitors → Wait for indicator return
5. Indicator returns → Sends full snapshot, backend validates
```

### **7. Data Completeness Validation**

**Every signal must have:**
- ✅ ENTRY event with entry_price, stop_loss, session
- ✅ MFE_UPDATE within last 10 minutes (if active)
- ✅ MAE value (if any drawdown occurred)
- ✅ signal_date and signal_time
- ✅ EXIT event (if stopped out)

**Validation runs every 5 minutes:**
```python
def validate_all_signals():
    for signal in get_active_signals():
        gaps = detect_gaps(signal)
        if gaps:
            fill_gaps(signal, gaps)
            log_gap_fill(signal, gaps)
```

### **8. Performance Requirements**

- **Latency:** Gap detection < 2 minutes
- **Throughput:** Handle 1000+ active signals
- **Reliability:** 99.9% uptime
- **Data Accuracy:** 100% of signals have complete data
- **Recovery Time:** < 5 minutes after indicator restart

### **9. Monitoring Dashboard**

**Real-time metrics:**
- Active signals count
- Signals with complete data %
- Gaps detected (last hour)
- Gaps filled (last hour)
- Indicator connection status
- Last sync timestamp
- Error rate

### **10. Advanced Features**

**Price Feed Integration:**
- Real-time price from Polygon/TradingView
- Historical price for MAE calculation
- Accurate MFE without indicator

**Machine Learning:**
- Predict likely MFE based on similar signals
- Detect anomalies in MFE values
- Improve synthetic data accuracy

**Multi-Indicator Support:**
- Track multiple indicators simultaneously
- Aggregate data from different sources
- Handle conflicts intelligently

**Disaster Recovery:**
- Automatic database backups
- Point-in-time recovery
- Data export for migration

---

## Implementation Phases

### **Phase 1: Foundation (Week 1)**
- Backend gap detection service
- Basic reconciliation (MFE calculation)
- Logging and monitoring

### **Phase 2: Communication (Week 2)**
- Indicator sync protocol
- Backend request/response handling
- Heartbeat system

### **Phase 3: Self-Healing (Week 3)**
- Automatic gap filling
- Conflict resolution
- Error recovery

### **Phase 4: Advanced (Week 4)**
- Price feed integration
- ML-based estimation
- Performance optimization

---

## Success Metrics

- **Zero orphaned signals** - All signals have complete data
- **< 2 min gap detection** - Issues identified quickly
- **< 5 min gap resolution** - Issues fixed automatically
- **100% data completeness** - Every signal fully populated
- **No manual intervention** - System self-heals

---

**This system ensures your trading platform has enterprise-grade reliability with zero data gaps.**

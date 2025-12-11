# Hybrid Signal Synchronization System - Implementation Tasks

**Project:** Enterprise-Grade Signal Data Integrity System  
**Status:** Ready for Implementation  
**Priority:** CRITICAL - Backbone of entire trading platform

---

## 📋 TASK BREAKDOWN

### PHASE 1: FOUNDATION (Week 1)

#### Task 1.1: Database Schema Enhancement
**Priority:** CRITICAL  
**Estimated Time:** 4 hours  
**Dependencies:** None

**Subtasks:**
- [ ] 1.1.1 Add `data_source` column (ENUM: 'indicator_realtime', 'indicator_polling', 'backend_calculated', 'reconciled')
- [ ] 1.1.2 Add `confidence_score` column (DECIMAL 0.0-1.0)
- [ ] 1.1.3 Add `reconciliation_timestamp` column (TIMESTAMP)
- [ ] 1.1.4 Add `reconciliation_reason` column (TEXT)
- [ ] 1.1.5 Add `payload_checksum` column (VARCHAR(64) for SHA-256)
- [ ] 1.1.6 Add `sequence_number` column (BIGINT for event ordering)
- [ ] 1.1.7 Add `confirmation_time` column (TIMESTAMP for signal → confirmation tracking)
- [ ] 1.1.8 Add `bars_to_confirmation` column (INTEGER)
- [ ] 1.1.9 Create indexes on new columns for query performance
- [ ] 1.1.10 Write migration script with rollback capability
- [ ] 1.1.11 Test migration on local database
- [ ] 1.1.12 Deploy to Railway with backup

**Acceptance Criteria:**
- All new columns exist in automated_signals table
- Indexes improve query performance by >50%
- Migration completes in <30 seconds
- Rollback script tested and working

---

#### Task 1.2: Signal Health Metrics Table
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] 1.2.1 Create `signal_health_metrics` table schema
- [ ] 1.2.2 Add columns: trade_id, last_update, gap_flags (JSONB), health_score, last_check
- [ ] 1.2.3 Add gap flag fields: no_mfe_update, no_entry_price, no_stop_loss, no_mae, no_session, no_signal_date
- [ ] 1.2.4 Create indexes on trade_id and last_check
- [ ] 1.2.5 Write table creation script
- [ ] 1.2.6 Add foreign key to automated_signals.trade_id
- [ ] 1.2.7 Test table creation locally
- [ ] 1.2.8 Deploy to Railway

**Acceptance Criteria:**
- Table exists with all columns
- Foreign key constraint enforced
- Can query health metrics in <100ms
- Gap flags stored as structured JSON

---

#### Task 1.3: Webhook Routing Infrastructure
**Priority:** CRITICAL  
**Estimated Time:** 6 hours  
**Dependencies:** None

**Subtasks:**
- [ ] 1.3.1 Create `/api/sync/primary` endpoint (ENTRY, EXIT, BE_TRIGGERED)
- [ ] 1.3.2 Create `/api/sync/batch` endpoint (MFE_UPDATE_BATCH)
- [ ] 1.3.3 Create `/api/sync/polling` endpoint (POLLING_RESPONSE)
- [ ] 1.3.4 Create `/api/sync/heartbeat` endpoint (HEARTBEAT, HEALTH_STATUS)
- [ ] 1.3.5 Add webhook authentication (API key validation)
- [ ] 1.3.6 Add rate limiting per webhook (different limits per type)
- [ ] 1.3.7 Add payload validation schemas for each webhook type
- [ ] 1.3.8 Add checksum verification for data integrity
- [ ] 1.3.9 Add retry logic with exponential backoff
- [ ] 1.3.10 Add webhook health monitoring (track success/failure rates)
- [ ] 1.3.11 Add logging for all webhook events
- [ ] 1.3.12 Test each webhook endpoint independently
- [ ] 1.3.13 Test failover between webhooks
- [ ] 1.3.14 Deploy to Railway

**Acceptance Criteria:**
- All 4 webhook endpoints operational
- Each handles 100+ requests/min without errors
- Failed webhooks retry automatically
- Health metrics tracked per webhook
- Checksum validation prevents corrupted data

---

### PHASE 2: INDICATOR ENHANCEMENT (Week 1-2)

#### Task 2.1: Indicator Polling Function
**Priority:** CRITICAL  
**Estimated Time:** 8 hours  
**Dependencies:** Task 1.3

**Subtasks:**
- [ ] 2.1.1 Create `f_handlePollingRequest()` function in indicator
- [ ] 2.1.2 Add polling request detection (special alert format)
- [ ] 2.1.3 Add signal lookup by trade_id in arrays
- [ ] 2.1.4 Build polling response payload with full signal data
- [ ] 2.1.5 Add batch polling support (multiple trade_ids in one request)
- [ ] 2.1.6 Add error handling for missing signals
- [ ] 2.1.7 Add response timeout (5 seconds max)
- [ ] 2.1.8 Test polling with 1 signal
- [ ] 2.1.9 Test polling with 10 signals
- [ ] 2.1.10 Test polling with 50 signals
- [ ] 2.1.11 Test polling when signal not found
- [ ] 2.1.12 Measure response time (<2 seconds for 50 signals)
- [ ] 2.1.13 Deploy to TradingView

**Acceptance Criteria:**
- Indicator responds to polling requests within 2 seconds
- Returns accurate data for requested signals
- Handles up to 50 signals per request
- Gracefully handles missing signals
- No impact on real-time tracking performance

---

#### Task 2.2: Enhanced Batch System
**Priority:** CRITICAL  
**Estimated Time:** 6 hours  
**Dependencies:** Task 2.1

**Subtasks:**
- [ ] 2.2.1 Fix batch to include ALL active signals (not just active_signal_ids)
- [ ] 2.2.2 Loop through signal arrays directly (last 500 signals)
- [ ] 2.2.3 Check sig_no_be_stopped flag to filter completed signals
- [ ] 2.2.4 Add payload size monitoring (stay under 4000 chars)
- [ ] 2.2.5 Add signal priority (recent signals first if size limit hit)
- [ ] 2.2.6 Add batch sequence numbers for ordering
- [ ] 2.2.7 Add batch checksum for integrity
- [ ] 2.2.8 Test with 10 active signals
- [ ] 2.2.9 Test with 50 active signals
- [ ] 2.2.10 Test with 100 active signals
- [ ] 2.2.11 Verify all signals eventually included (rotation)
- [ ] 2.2.12 Measure coverage (% of signals updated per minute)
- [ ] 2.2.13 Deploy to TradingView

**Acceptance Criteria:**
- Batch includes all active signals within 3 minutes
- No signals orphaned or missed
- Payload stays under 4096 character limit
- 100% of active signals updated every 3 minutes
- No TradingView rate limiting

---

#### Task 2.3: Heartbeat System
**Priority:** HIGH  
**Estimated Time:** 3 hours  
**Dependencies:** Task 1.3

**Subtasks:**
- [ ] 2.3.1 Add heartbeat alert (every minute)
- [ ] 2.3.2 Include signal count in heartbeat
- [ ] 2.3.3 Include indicator version in heartbeat
- [ ] 2.3.4 Include last error message (if any)
- [ ] 2.3.5 Add indicator health status (OK, WARNING, ERROR)
- [ ] 2.3.6 Test heartbeat delivery
- [ ] 2.3.7 Verify backend receives and logs heartbeats
- [ ] 2.3.8 Deploy to TradingView

**Acceptance Criteria:**
- Heartbeat sent every minute
- Backend detects missing heartbeats within 3 minutes
- Indicator health status accurate
- Alerts triggered when heartbeat stops

---

### PHASE 3: BACKEND GAP DETECTION (Week 2)

#### Task 3.1: Gap Detection Service
**Priority:** CRITICAL  
**Estimated Time:** 8 hours  
**Dependencies:** Task 1.1, Task 1.2

**Subtasks:**
- [ ] 3.1.1 Create `gap_detector.py` service
- [ ] 3.1.2 Add function: `detect_no_mfe_update()` (no update in 2 min)
- [ ] 3.1.3 Add function: `detect_no_entry_price()` (NULL entry_price)
- [ ] 3.1.4 Add function: `detect_no_stop_loss()` (NULL stop_loss)
- [ ] 3.1.5 Add function: `detect_no_mae()` (NULL or 0 mae_global_r)
- [ ] 3.1.6 Add function: `detect_no_session()` (NULL session)
- [ ] 3.1.7 Add function: `detect_no_signal_date()` (NULL signal_date)
- [ ] 3.1.8 Add function: `calculate_health_score()` (0-100 based on gaps)
- [ ] 3.1.9 Add function: `update_health_metrics()` (write to signal_health_metrics table)
- [ ] 3.1.10 Add background thread (runs every 2 minutes)
- [ ] 3.1.11 Add logging for all detected gaps
- [ ] 3.1.12 Test gap detection with known incomplete signals
- [ ] 3.1.13 Verify health scores calculated correctly
- [ ] 3.1.14 Test performance (scan 1000 signals in <5 seconds)
- [ ] 3.1.15 Deploy to Railway

**Acceptance Criteria:**
- Detects all 6 gap types accurately
- Runs every 2 minutes without blocking
- Updates health metrics table
- Processes 1000 signals in <5 seconds
- Logs all gaps for monitoring

---

#### Task 3.2: Gap Notification System
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Task 3.1

**Subtasks:**
- [ ] 3.2.1 Create alert thresholds (>10 signals with gaps = WARNING)
- [ ] 3.2.2 Add dashboard notification banner for critical gaps
- [ ] 3.2.3 Add email alerts for persistent gaps (>1 hour)
- [ ] 3.2.4 Add Slack/Discord webhook for real-time alerts
- [ ] 3.2.5 Add gap summary API endpoint
- [ ] 3.2.6 Test notification delivery
- [ ] 3.2.7 Deploy to Railway

**Acceptance Criteria:**
- Alerts triggered when gap threshold exceeded
- Dashboard shows gap warnings
- Email sent for persistent gaps
- Gap summary accessible via API

---

### PHASE 4: BACKEND RECONCILIATION (Week 2-3)

#### Task 4.1: Indicator Polling Client
**Priority:** CRITICAL  
**Estimated Time:** 6 hours  
**Dependencies:** Task 2.1, Task 3.1

**Subtasks:**
- [ ] 4.1.1 Create `indicator_polling_client.py` service
- [ ] 4.1.2 Add function: `request_signal_data(trade_ids)` (sends polling request to indicator)
- [ ] 4.1.3 Add function: `wait_for_response(timeout=10s)` (listens for POLLING_RESPONSE webhook)
- [ ] 4.1.4 Add function: `parse_polling_response()` (extract signal data)
- [ ] 4.1.5 Add request queue (batch multiple requests)
- [ ] 4.1.6 Add timeout handling (fallback if no response)
- [ ] 4.1.7 Add retry logic (3 attempts with backoff)
- [ ] 4.1.8 Test polling for 1 signal
- [ ] 4.1.9 Test polling for 10 signals
- [ ] 4.1.10 Test timeout scenario
- [ ] 4.1.11 Test retry logic
- [ ] 4.1.12 Deploy to Railway

**Acceptance Criteria:**
- Successfully polls indicator for signal data
- Receives response within 10 seconds
- Handles timeouts gracefully
- Retries failed requests
- Batches multiple requests efficiently

---

#### Task 4.2: Reconciliation Engine
**Priority:** CRITICAL  
**Estimated Time:** 10 hours  
**Dependencies:** Task 4.1

**Subtasks:**
- [ ] 4.2.1 Create `reconciliation_engine.py` service
- [ ] 4.2.2 Add three-tier gap filling logic:
  - Tier 1: Request from indicator (most accurate)
  - Tier 2: Calculate from database (entry/stop/price)
  - Tier 3: Extract from trade_id (metadata only)
- [ ] 4.2.3 Add function: `fill_missing_mfe()` (calculate from entry/stop/current_price)
- [ ] 4.2.4 Add function: `fill_missing_mae()` (estimate from historical price data)
- [ ] 4.2.5 Add function: `fill_missing_entry_data()` (extract from trade_id or query indicator)
- [ ] 4.2.6 Add function: `fill_missing_metadata()` (session, date from trade_id)
- [ ] 4.2.7 Add function: `detect_missing_exits()` (check if stop hit based on price)
- [ ] 4.2.8 Add function: `insert_reconciled_event()` (mark as reconciled with confidence)
- [ ] 4.2.9 Add background thread (runs every 2 minutes)
- [ ] 4.2.10 Add reconciliation priority queue (critical gaps first)
- [ ] 4.2.11 Test reconciliation for each gap type
- [ ] 4.2.12 Verify confidence scores assigned correctly
- [ ] 4.2.13 Test with 50 orphaned signals
- [ ] 4.2.14 Measure reconciliation speed (<10 seconds for 50 signals)
- [ ] 4.2.15 Deploy to Railway

**Acceptance Criteria:**
- Fills all 6 gap types automatically
- Prefers indicator data over calculations
- Marks reconciled data with confidence scores
- Processes 50 signals in <10 seconds
- Runs continuously without blocking

---

#### Task 4.3: Price Feed Integration
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Task 4.2

**Subtasks:**
- [ ] 4.3.1 Integrate Polygon.io API for real-time NQ price
- [ ] 4.3.2 Add price caching (1-second granularity)
- [ ] 4.3.3 Add function: `get_current_price()` (latest NQ price)
- [ ] 4.3.4 Add function: `get_historical_price(timestamp)` (price at specific time)
- [ ] 4.3.5 Add function: `get_price_range(start, end)` (high/low in range for MAE)
- [ ] 4.3.6 Add fallback to TradingView price webhook if Polygon fails
- [ ] 4.3.7 Test price accuracy (compare to TradingView)
- [ ] 4.3.8 Test historical price retrieval
- [ ] 4.3.9 Measure API latency (<500ms)
- [ ] 4.3.10 Deploy to Railway

**Acceptance Criteria:**
- Real-time price available within 1 second
- Historical prices accurate to tick level
- Fallback works if primary source fails
- API latency <500ms average

---

### PHASE 5: FRONTEND INTEGRATION (Week 3)

#### Task 5.1: Signal Lifecycle Visualization
**Priority:** HIGH  
**Estimated Time:** 8 hours  
**Dependencies:** Task 1.1, Task 1.2

**Subtasks:**
- [ ] 5.1.1 Create signal detail modal component
- [ ] 5.1.2 Add timeline view (all events chronologically)
- [ ] 5.1.3 Add event cards (ENTRY, MFE_UPDATE, BE_TRIGGERED, EXIT)
- [ ] 5.1.4 Add gap indicators (red flags for missing data)
- [ ] 5.1.5 Add data source badges (indicator vs reconciled)
- [ ] 5.1.6 Add confidence score display
- [ ] 5.1.7 Add raw payload viewer (collapsible JSON)
- [ ] 5.1.8 Add copy-to-clipboard functionality
- [ ] 5.1.9 Add visual gap highlighting (missing events in red)
- [ ] 5.1.10 Add health score gauge (0-100)
- [ ] 5.1.11 Style with ultra theme CSS
- [ ] 5.1.12 Test with complete signal (no gaps)
- [ ] 5.1.13 Test with incomplete signal (multiple gaps)
- [ ] 5.1.14 Test copy functionality
- [ ] 5.1.15 Deploy to Railway

**Acceptance Criteria:**
- Click any signal → modal opens with full lifecycle
- All events displayed chronologically
- Gaps clearly highlighted in red
- Raw payloads viewable and copyable
- Health score visible at a glance

---

#### Task 5.2: Health Dashboard Widget
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Task 3.1, Task 5.1

**Subtasks:**
- [ ] 5.2.1 Add health summary card to dashboard header
- [ ] 5.2.2 Display: Total signals, Healthy %, Signals with gaps
- [ ] 5.2.3 Add color coding (green >95%, yellow 90-95%, red <90%)
- [ ] 5.2.4 Add click → expand to show gap breakdown
- [ ] 5.2.5 Add "Fix All Gaps" button (triggers reconciliation)
- [ ] 5.2.6 Add real-time updates via WebSocket
- [ ] 5.2.7 Test health metrics display
- [ ] 5.2.8 Test "Fix All Gaps" functionality
- [ ] 5.2.9 Deploy to Railway

**Acceptance Criteria:**
- Health summary always visible
- Updates in real-time
- Gap breakdown shows specific issues
- Manual reconciliation trigger works

---

#### Task 5.3: All Signals Tab Implementation
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Task 5.1

**Subtasks:**
- [ ] 5.3.1 Create backend API: `/api/automated-signals/all-signals`
- [ ] 5.3.2 Query SIGNAL_CREATED events from database
- [ ] 5.3.3 Join with ENTRY events (confirmation data)
- [ ] 5.3.4 Join with CANCELLED events
- [ ] 5.3.5 Calculate bars_to_confirmation
- [ ] 5.3.6 Add HTF alignment display
- [ ] 5.3.7 Add confirmation status (Pending, Confirmed, Cancelled)
- [ ] 5.3.8 Add frontend table rendering
- [ ] 5.3.9 Add filters (session, HTF alignment, status)
- [ ] 5.3.10 Add sorting (by time, bars to confirmation)
- [ ] 5.3.11 Test with 100+ signals
- [ ] 5.3.12 Deploy to Railway

**Acceptance Criteria:**
- All Signals tab shows every triangle printed
- Displays signal time, confirmation time, bars between
- Shows HTF alignment at signal time
- Filters and sorting work correctly
- Handles 1000+ signals without performance issues

---

### PHASE 6: MONITORING & OBSERVABILITY (Week 3-4)

#### Task 6.1: Sync Health Monitoring
**Priority:** HIGH  
**Estimated Time:** 6 hours  
**Dependencies:** Task 3.1, Task 4.2

**Subtasks:**
- [ ] 6.1.1 Create monitoring dashboard page
- [ ] 6.1.2 Add real-time metrics:
  - Signals tracked by indicator
  - Signals in database
  - Coverage percentage
  - Gap count by type
  - Reconciliation success rate
- [ ] 6.1.3 Add charts (coverage over time, gap trends)
- [ ] 6.1.4 Add webhook health (success rate per webhook)
- [ ] 6.1.5 Add indicator health (heartbeat status, last seen)
- [ ] 6.1.6 Add alert history (recent gaps detected)
- [ ] 6.1.7 Test monitoring display
- [ ] 6.1.8 Deploy to Railway

**Acceptance Criteria:**
- Monitoring dashboard shows real-time system health
- Coverage percentage visible
- Gap trends tracked over time
- Webhook health monitored
- Indicator connectivity status shown

---

#### Task 6.2: Audit Trail System
**Priority:** MEDIUM  
**Estimated Time:** 5 hours  
**Dependencies:** Task 1.1

**Subtasks:**
- [ ] 6.2.1 Create `sync_audit_log` table
- [ ] 6.2.2 Log all reconciliation actions
- [ ] 6.2.3 Log all gap detections
- [ ] 6.2.4 Log all polling requests/responses
- [ ] 6.2.5 Add audit log viewer in dashboard
- [ ] 6.2.6 Add filtering (by signal, by action type, by date)
- [ ] 6.2.7 Test audit log completeness
- [ ] 6.2.8 Deploy to Railway

**Acceptance Criteria:**
- All sync actions logged
- Audit trail queryable by signal
- Shows what data was filled and when
- Shows data source for each field

---

### PHASE 7: TESTING & VALIDATION (Week 4)

#### Task 7.1: Integration Testing
**Priority:** CRITICAL  
**Estimated Time:** 8 hours  
**Dependencies:** All previous tasks

**Subtasks:**
- [ ] 7.1.1 Test complete signal lifecycle (SIGNAL_CREATED → ENTRY → MFE → EXIT)
- [ ] 7.1.2 Test orphaned signal recovery (indicator restart scenario)
- [ ] 7.1.3 Test gap filling (manually create gaps, verify filled)
- [ ] 7.1.4 Test indicator polling (request data, verify response)
- [ ] 7.1.5 Test batch coverage (verify all signals updated)
- [ ] 7.1.6 Test webhook failover (disable primary, verify backup works)
- [ ] 7.1.7 Test high load (100 active signals)
- [ ] 7.1.8 Test indicator restart (verify arrays rebuild)
- [ ] 7.1.9 Test database failure (verify graceful degradation)
- [ ] 7.1.10 Test network issues (verify retry logic)
- [ ] 7.1.11 Measure end-to-end latency (signal → dashboard)
- [ ] 7.1.12 Measure system reliability (uptime, error rate)

**Acceptance Criteria:**
- 100% signal coverage achieved
- Zero orphaned signals after 5 minutes
- All gaps filled within 5 minutes
- System recovers from all failure scenarios
- End-to-end latency <5 seconds

---

#### Task 7.2: Performance Optimization
**Priority:** MEDIUM  
**Estimated Time:** 6 hours  
**Dependencies:** Task 7.1

**Subtasks:**
- [ ] 7.2.1 Profile database queries (identify slow queries)
- [ ] 7.2.2 Add database indexes for common queries
- [ ] 7.2.3 Optimize gap detection queries
- [ ] 7.2.4 Optimize reconciliation queries
- [ ] 7.2.5 Add query result caching (5-second TTL)
- [ ] 7.2.6 Optimize batch processing (parallel inserts)
- [ ] 7.2.7 Test performance improvements
- [ ] 7.2.8 Deploy to Railway

**Acceptance Criteria:**
- Dashboard loads in <2 seconds
- Gap detection completes in <3 seconds
- Reconciliation processes 100 signals in <10 seconds
- Database queries optimized (all <100ms)

---

#### Task 7.3: Documentation
**Priority:** MEDIUM  
**Estimated Time:** 4 hours  
**Dependencies:** Task 7.1

**Subtasks:**
- [ ] 7.3.1 Document system architecture (diagrams)
- [ ] 7.3.2 Document webhook formats and endpoints
- [ ] 7.3.3 Document gap detection logic
- [ ] 7.3.4 Document reconciliation workflows
- [ ] 7.3.5 Document troubleshooting procedures
- [ ] 7.3.6 Document monitoring and alerts
- [ ] 7.3.7 Create operator runbook
- [ ] 7.3.8 Create developer guide

**Acceptance Criteria:**
- Complete system documentation
- Troubleshooting guide for common issues
- Operator runbook for daily operations
- Developer guide for future enhancements

---

## 📊 IMPLEMENTATION SUMMARY

**Total Tasks:** 7 major phases  
**Total Subtasks:** 180+ individual tasks  
**Estimated Timeline:** 4 weeks  
**Team Size:** 1 developer (you + Kiro)

**Critical Path:**
1. Database schema (Task 1.1, 1.2) - Week 1
2. Webhook infrastructure (Task 1.3) - Week 1
3. Indicator enhancements (Task 2.1, 2.2) - Week 1-2
4. Gap detection (Task 3.1) - Week 2
5. Reconciliation (Task 4.1, 4.2) - Week 2-3
6. Frontend integration (Task 5.1, 5.2, 5.3) - Week 3
7. Testing & optimization (Task 7.1, 7.2) - Week 4

**Success Metrics:**
- 100% signal coverage (zero orphaned signals)
- <2 minute gap detection and filling
- 99.9% data accuracy
- <5 second end-to-end latency
- Zero manual intervention required

---

## 🚀 QUICK START (First Session)

**Immediate Actions:**
1. Run Task 1.1 (Database Schema) - Add new columns
2. Run Task 1.3 (Webhook Routing) - Create 4 webhook endpoints
3. Run Task 2.2 (Enhanced Batch) - Fix batch to include all signals

**Expected Outcome:**
- Database ready for enhanced tracking
- Webhook infrastructure in place
- Batch system covering all active signals

**Time Required:** 4-6 hours

---

## 📝 NOTES

**Lessons Learned Integration:**
- All timestamps in NY EST (matches TradingView)
- UTC storage in database (proper practice)
- Timezone conversion at query time
- No synthetic data without clear confidence scores
- Indicator as source of truth for calculations
- Backend as source of truth for signal list
- Robust error handling at every layer
- Comprehensive logging for diagnosis

**Risk Mitigation:**
- Incremental deployment (phase by phase)
- Rollback capability at each phase
- Parallel testing (don't break existing system)
- Comprehensive monitoring (detect issues immediately)
- Graceful degradation (system continues if components fail)

**Future Enhancements:**
- ML-based gap prediction (predict which signals will have gaps)
- Automated indicator restart (if heartbeat stops)
- Cross-market support (ES, YM, RTY)
- Multi-timeframe sync (1m, 5m, 15m)
- Historical data backfill (reconstruct old signals)

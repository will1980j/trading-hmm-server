# Requirements Document - Hybrid Signal Synchronization System

## Introduction

The Hybrid Signal Synchronization System is the foundational data integrity layer for the Second Skies Trading Platform. It ensures every signal has complete, accurate data throughout its lifecycle by intelligently coordinating between the TradingView indicator (real-time source) and the backend database (source of truth). This system is critical infrastructure that underpins all ML training, AI analysis, strategy optimization, and trading decisions.

## Glossary

- **Signal**: A trading opportunity identified by the indicator (triangle on chart)
- **Confirmed Signal**: A signal that has been validated and entered (ENTRY event sent)
- **Orphaned Signal**: A signal with incomplete data due to indicator restart or tracking gaps
- **Lifecycle**: Complete journey of a signal from creation → confirmation → tracking → completion
- **Reconciliation**: Process of detecting and filling data gaps automatically
- **Synthetic Data**: Calculated values used to fill gaps when real-time data unavailable
- **Source of Truth**: The authoritative data source (backend database)
- **Real-Time Engine**: The live calculation source (TradingView indicator)
- **Gap**: Missing or incomplete data for a signal
- **Health Metric**: Measurement of data completeness and system integrity

## Requirements

### Requirement 1: Complete Signal Registry

**User Story:** As a trader, I want every signal to have complete data, so that I can trust the platform's analytics and make informed decisions.

#### Acceptance Criteria

1. WHEN a signal is created THEN the system SHALL capture signal time, direction, session, and HTF alignment
2. WHEN a signal is confirmed THEN the system SHALL record entry price, stop loss, risk distance, and targets
3. WHEN a signal is active THEN the system SHALL update MFE (BE and No-BE) and MAE every minute
4. WHEN a signal completes THEN the system SHALL record final MFE, exit price, exit reason, and duration
5. WHEN querying any signal THEN the system SHALL return complete data with no NULL fields

### Requirement 2: Automatic Gap Detection

**User Story:** As a system administrator, I want gaps in signal data to be detected automatically, so that data quality issues are identified immediately without manual checking.

#### Acceptance Criteria

1. WHEN a signal has no MFE_UPDATE for 10 minutes THEN the system SHALL flag it as "stale data"
2. WHEN a signal has NULL entry_price or stop_loss THEN the system SHALL flag it as "incomplete ENTRY"
3. WHEN a signal has no MAE value THEN the system SHALL flag it as "missing drawdown data"
4. WHEN a signal has no session or signal_date THEN the system SHALL flag it as "missing metadata"
5. WHEN gaps are detected THEN the system SHALL log the gap type, signal ID, and detection timestamp

### Requirement 3: Intelligent Gap Filling

**User Story:** As a data analyst, I want gaps to be filled automatically with accurate data, so that analytics and ML training have complete datasets.

#### Acceptance Criteria

1. WHEN a gap is detected THEN the system SHALL attempt to fill it from the most reliable source
2. WHEN indicator is tracking a signal THEN the system SHALL request fresh data from indicator
3. WHEN indicator is not tracking a signal THEN the system SHALL calculate synthetic data from entry/stop/price
4. WHEN filling gaps THEN the system SHALL mark synthetic data with "reconciled" flag
5. WHEN multiple data sources conflict THEN the system SHALL prefer indicator data over calculated data

### Requirement 4: Backend-Indicator Communication

**User Story:** As a system architect, I want the backend and indicator to communicate bidirectionally, so that they can coordinate to maintain data completeness.

#### Acceptance Criteria

1. WHEN indicator starts THEN the system SHALL send HEARTBEAT with tracking status
2. WHEN backend detects gaps THEN the system SHALL send SYNC_REQUEST to indicator
3. WHEN indicator receives SYNC_REQUEST THEN the system SHALL respond with requested signal data
4. WHEN communication fails THEN the system SHALL retry with exponential backoff
5. WHEN indicator is offline THEN the system SHALL activate full reconciliation mode

### Requirement 5: Data Integrity Validation

**User Story:** As a trader, I want signal data to be validated for correctness, so that I can trust the MFE/MAE values for trading decisions.

#### Acceptance Criteria

1. WHEN MFE is negative THEN the system SHALL flag it as invalid and recalculate
2. WHEN BE MFE exceeds No-BE MFE (before BE exit) THEN the system SHALL flag as logic error
3. WHEN MAE is positive THEN the system SHALL flag it as invalid and correct to 0
4. WHEN entry_price equals stop_loss THEN the system SHALL flag as invalid configuration
5. WHEN validation fails THEN the system SHALL log the error and attempt correction

### Requirement 6: Scalable Architecture

**User Story:** As a business owner, I want the system to handle thousands of signals, so that the platform can scale as the trading operation grows.

#### Acceptance Criteria

1. WHEN processing 1000 active signals THEN the system SHALL complete gap detection within 2 minutes
2. WHEN sending batch updates THEN the system SHALL handle payload size limits gracefully
3. WHEN database load increases THEN the system SHALL maintain sub-second query performance
4. WHEN indicator processes signals THEN the system SHALL avoid timeout errors
5. WHEN scaling to multiple indicators THEN the system SHALL coordinate updates without conflicts

### Requirement 7: Self-Healing Capabilities

**User Story:** As a system administrator, I want the system to recover from failures automatically, so that manual intervention is never required.

#### Acceptance Criteria

1. WHEN indicator restarts THEN the system SHALL rebuild signal tracking from database
2. WHEN database connection fails THEN the system SHALL retry and buffer updates
3. WHEN webhook delivery fails THEN the system SHALL queue and retry
4. WHEN data corruption is detected THEN the system SHALL restore from last known good state
5. WHEN system recovers THEN the system SHALL log recovery actions and verify data completeness

### Requirement 8: Comprehensive Monitoring

**User Story:** As a system administrator, I want detailed health metrics, so that I can monitor system performance and identify issues proactively.

#### Acceptance Criteria

1. WHEN monitoring system health THEN the system SHALL report signal coverage percentage
2. WHEN gaps are detected THEN the system SHALL report gap count by type
3. WHEN gaps are filled THEN the system SHALL report fill success rate
4. WHEN indicator communicates THEN the system SHALL report connection status and latency
5. WHEN errors occur THEN the system SHALL report error type, frequency, and affected signals

### Requirement 9: Audit Trail

**User Story:** As a compliance officer, I want complete audit logs, so that I can trace every data modification and verify system integrity.

#### Acceptance Criteria

1. WHEN data is inserted THEN the system SHALL log source (indicator vs reconciler)
2. WHEN data is modified THEN the system SHALL log old value, new value, and reason
3. WHEN gaps are filled THEN the system SHALL log gap type, fill method, and timestamp
4. WHEN conflicts are resolved THEN the system SHALL log both values and resolution logic
5. WHEN querying audit trail THEN the system SHALL provide complete history for any signal

### Requirement 10: Integration with Downstream Systems

**User Story:** As a platform architect, I want the sync system to feed clean data to all downstream systems, so that ML, AI, and analytics have reliable inputs.

#### Acceptance Criteria

1. WHEN ML training runs THEN the system SHALL provide complete MFE/MAE datasets with no gaps
2. WHEN AI analyzes patterns THEN the system SHALL provide complete lifecycle data for all signals
3. WHEN strategy optimizer runs THEN the system SHALL provide accurate performance metrics
4. WHEN dashboard displays data THEN the system SHALL provide real-time updates with no stale data
5. WHEN exporting data THEN the system SHALL mark synthetic data clearly for transparency

---

**This system is the foundation of data integrity for the entire Second Skies Trading Platform. Every downstream system depends on its reliability and completeness.**

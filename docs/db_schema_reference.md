# Second Skies Database Schema Reference (H1.7 Foundation)

## Overview
This document defines the foundational database schema for the Second Skies Trading Platform.
It covers current H1 tables and planned future schemas (H2–H13). This file is the authoritative
source of truth for all future database design decisions.

---

## H1 — Core Platform Tables (Active)

### automated_signals (Lifecycle Event Store)
Stores all lifecycle events for every trade.

Schema:
- id SERIAL PRIMARY KEY
- trade_id VARCHAR(64) NOT NULL
- event_type VARCHAR(32) NOT NULL
- timestamp TIMESTAMPTZ NOT NULL
- signal_date DATE
- signal_time TIMETZ
- direction VARCHAR(16)
- session VARCHAR(16)
- bias VARCHAR(32)
- entry_price NUMERIC(12,4)
- stop_loss NUMERIC(12,4)
- current_price NUMERIC(12,4)
- exit_price NUMERIC(12,4)
- mfe NUMERIC(10,4)
- no_be_mfe NUMERIC(10,4)
- be_mfe NUMERIC(10,4)
- final_mfe NUMERIC(10,4)
- risk_distance NUMERIC(12,4)
- targets JSONB
- telemetry JSONB

---

### telemetry_automated_signals_log
Ingestion telemetry and processing insights.

Schema:
- id SERIAL PRIMARY KEY
- received_at TIMESTAMPTZ DEFAULT NOW()
- raw_payload JSONB
- fused_event JSONB
- validation_error TEXT
- handler_result JSONB
- processing_time_ms INTEGER
- ai_detail JSONB
- ai_rl_score JSONB

---

### execution_tasks (Future: H2/H13)
- id SERIAL PRIMARY KEY
- trade_id VARCHAR(64)
- event_type VARCHAR(50)
- payload JSONB
- attempts INTEGER DEFAULT 0
- status VARCHAR(20) DEFAULT 'PENDING'
- created_at TIMESTAMPTZ DEFAULT NOW()
- updated_at TIMESTAMPTZ DEFAULT NOW()
- last_attempt_at TIMESTAMPTZ
- last_error TEXT

### execution_logs (Future: H2/H13)
- id SERIAL PRIMARY KEY
- task_id INTEGER
- log_message TEXT
- created_at TIMESTAMPTZ DEFAULT NOW()

---

## H1.7 Indexing Plan (Design Only)

Recommended future indexes:
- trade_id
- timestamp DESC
- event_type
- (session, timestamp) DESC
- signal_date (optional)
- direction (optional)

---

## H1.7 Partition Strategy (Design Only)

Parent table:
- automated_signals partitioned by RANGE(timestamp)

Recommended child partitions:
- Monthly partitions (default)
- Daily partitions (high volume case)

---

## Future Schemas (Design Only)

### H5 — ML Feature Store
- ml_feature_vectors
- ml_training_labels
- model_registry
- model_predictions

### H8 — Prop Engine
- prop_firms
- prop_firm_programs
- prop_firm_rules
- prop_account_state

### H13 — Execution & Automation
- execution_tasks
- execution_logs
- trade_outcome_events

---

## Notes

- This file defines the canonical DB schema.
- Any future schema change must update this document.
- Indexes and partitions should be implemented after ingestion stabilizes.

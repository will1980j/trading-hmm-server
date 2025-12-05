-- Migration: Add payload_ts column to automated_signals table
-- This column stores the canonical TradingView timestamp from the webhook payload

ALTER TABLE automated_signals
ADD COLUMN payload_ts TIMESTAMPTZ NULL;

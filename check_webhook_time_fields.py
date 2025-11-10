"""
Check what time fields are in the webhook payload vs what's stored in database
"""

# The webhook sends:
webhook_payload = {
    "type": "signal_created",
    "signal_id": "ABC123",
    "date": "2024-01-15",  # ← Signal candle date
    "time": "10:00:00",    # ← Signal candle time
    "bias": "Bullish",
    "entry_price": 4150.25,
    "sl_price": 4125.00,
    # ... other fields
}

# But the database INSERT only stores:
database_insert = """
INSERT INTO automated_signals (
    trade_id, event_type, direction, entry_price, stop_loss,
    session, bias, risk_distance, targets
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# The 'date' and 'time' fields from webhook are IGNORED!
# The database uses timestamp = NOW() which is when webhook received, not signal candle time

print("❌ PROBLEM: Webhook sends 'date' and 'time' but database doesn't store them!")
print("✅ SOLUTION: Store signal_date and signal_time in database OR format time in dashboard from webhook data")

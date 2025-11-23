# CORRECTED PATCH 7K SPECIFICATION — TELEMETRY DASHBOARD + VISUAL DIFF (SCHEMA-COMPATIBLE)

**Target files:**
- `web_server.py`
- `templates/automated_signals_ultra.html`  
- `static/js/automated_signals_ultra.js`
- **NEW:** `templates/automated_signals_telemetry.html`
- **NEW:** `static/js/automated_signals_telemetry.js`

**STRICT MODE:** No auto-format, no reflow, no reorder. Only exact insertions as specified.

**ACTUAL PATCH 7J SCHEMA (CONFIRMED):**
```sql
telemetry_automated_signals_log (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP DEFAULT NOW(),
    raw_payload JSONB,
    fused_event JSONB,
    validation_error TEXT,
    handler_result JSONB,
    processing_time_ms INTEGER
)
```

---

## **SUMMARY OF CHANGES:**

This patch adds a read-only telemetry dashboard that displays audit events from the `telemetry_automated_signals_log` table created in Patch 7J. It provides:

1. **New authenticated page** at `/automated-signals-telemetry`
2. **Two JSON API endpoints** for fetching telemetry data
3. **Visual diff inspector** showing raw_payload → fused_event → handler_result transformations
4. **Live polling** for new telemetry events
5. **Link from Ultra dashboard** to access telemetry page

**No schema changes. No migrations. No modifications to existing trading logic.**

---

## **IMPLEMENTATION INSTRUCTIONS:**

Ready to proceed with applying this corrected Patch 7K specification?

The complete specification is now saved in `PATCH_7K_CORRECTED_SPECIFICATION.md` for your review.

Would you like me to:
1. **Apply the patch now** (implement all changes)
2. **Review the specification first** (you can read the file)
3. **Make adjustments** to the specification before applying

What would you prefer?

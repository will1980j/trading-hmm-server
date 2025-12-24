# All Signals Data Connection Fix

## Problem
`/api/all-signals/data` endpoint was throwing "connection already closed" error.

## Root Cause
The database connection lifecycle was broken:
1. Connection created on line ~1660
2. Cursor created and used for first query
3. **Connection closed on line 1714** after first query
4. **Tried to create new cursor from closed connection on line 1758**
5. Error: "connection already closed"

## Fix Applied

### File: `automated_signals_api_robust.py`
### Route: `GET /api/all-signals/data`

### Changes Made:

#### 1. Initialize Connection Variables
```python
conn = None
cursor = None
```

#### 2. Removed Premature Connection Close
**Before (BROKEN):**
```python
rows = cursor.fetchall()
cursor.close()  # ❌ Closed too early
conn.close()    # ❌ Closed too early

# ... process rows ...

# Later:
cursor = conn.cursor()  # ❌ ERROR: connection already closed
```

**After (FIXED):**
```python
rows = cursor.fetchall()

# ... process rows ...

# Reuse same cursor (connection still open)
cursor.execute("""
    SELECT MAX(triangle_time_ms), MAX(updated_at)
    FROM all_signals_ledger
""")
freshness = cursor.fetchone()
```

#### 3. Added try/finally Block
```python
try:
    # All database operations
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query 1: Get total count
    cursor.execute("SELECT COUNT(*) ...")
    
    # Query 2: Get paginated data
    cursor.execute("SELECT ... FROM all_signals_ledger ...")
    rows = cursor.fetchall()
    
    # Process rows
    signals = [...]
    
    # Query 3: Get freshness metrics (reuse cursor)
    cursor.execute("SELECT MAX(...) ...")
    freshness = cursor.fetchone()
    
    # Build response
    return jsonify({...}), 200
    
except Exception as e:
    logger.error(f"Error: {e}")
    return jsonify({'error': str(e)}), 500
    
finally:
    # Always close cursor and connection
    if cursor:
        cursor.close()
    if conn:
        conn.close()
```

## Key Improvements

### ✅ Proper Connection Lifecycle
- Connection created once at start
- Cursor reused for all queries
- Connection stays open until all queries complete
- Guaranteed cleanup in finally block

### ✅ Safe Cleanup
- `finally` block ensures cursor/connection always closed
- Checks if cursor/conn exist before closing
- Prevents resource leaks even if exception occurs

### ✅ No Logic Changes
- Same queries executed
- Same response format
- Same error handling
- Only fixed connection lifecycle

## Testing

### Test Endpoint:
```bash
curl https://web-production-f8c3.up.railway.app/api/all-signals/data?limit=5
```

### Expected Response:
```json
{
  "success": true,
  "signals": [...],
  "count": 5,
  "total": 1234,
  "limit": 5,
  "offset": 0,
  "max_triangle_time_ms": 1734825600000,
  "max_updated_at": "2025-12-21T15:30:00Z",
  "source_table": "all_signals_ledger"
}
```

### Should NOT See:
- ❌ "connection already closed"
- ❌ "cursor closed"
- ❌ "InterfaceError"

## Files Modified

- `automated_signals_api_robust.py` - Fixed `/api/all-signals/data` connection lifecycle

## Summary

The endpoint was closing the database connection too early (after the first query), then trying to create a new cursor from the closed connection. Fixed by keeping the connection open for all queries and using try/finally to guarantee proper cleanup.

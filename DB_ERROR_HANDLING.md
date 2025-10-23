# Automatic Database Error Handling

## Overview
The platform now has **3 layers of automatic database error protection**:

### Layer 1: Health Monitor (Background)
- **File**: `database_health_monitor.py`
- **Runs**: Every 30 seconds
- **Fixes**: Aborted transactions, dead connections
- **Purpose**: Safety net for long-running issues

### Layer 2: Request Handler (Per-Request)
- **File**: `web_server.py` - `@app.before_request`
- **Runs**: Before every HTTP request
- **Fixes**: Aborted transactions from previous requests
- **Purpose**: Clean slate for each API call

### Layer 3: Function Decorator (Per-Function) ⭐ NEW
- **File**: `db_error_handler.py` - `@auto_fix_db_errors`
- **Runs**: Before every decorated function
- **Fixes**: Aborted transactions, connection errors
- **Purpose**: Immediate error handling for critical functions

## How to Use the Decorator

### Basic Usage
```python
from db_error_handler import auto_fix_db_errors

class MyClass:
    def __init__(self, db):
        self.db = db
    
    @auto_fix_db_errors
    def my_database_function(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM my_table")
        return cursor.fetchall()
```

### What It Does Automatically
1. ✅ Checks transaction status before function runs
2. ✅ Rolls back aborted transactions
3. ✅ Commits hanging transactions
4. ✅ Retries on connection errors (up to 2 attempts)
5. ✅ Logs all fixes for monitoring

### When to Use It
Use `@auto_fix_db_errors` on any function that:
- Executes database queries
- Is called outside HTTP request context (webhooks, background tasks)
- Needs high reliability (signal processing, logging)

### Already Protected Functions
- ✅ `webhook_debugger.py` - All logging functions
- ✅ `contract_manager.py` - All database operations
- ✅ More to be added as needed

## Error Handling Flow

```
Incoming Request/Webhook
    ↓
Layer 3: @auto_fix_db_errors decorator
    ├─ Check transaction status
    ├─ Fix if needed
    └─ Execute function
        ↓
    If error occurs:
        ├─ Rollback transaction
        ├─ Retry (up to 2 times)
        └─ Log error
            ↓
Layer 2: @app.before_request (next request)
    └─ Clean up any remaining issues
            ↓
Layer 1: Health Monitor (every 30s)
    └─ Final safety net
```

## Benefits
- 🚀 **Automatic**: No manual intervention needed
- 🔄 **Self-healing**: Fixes errors before they cause failures
- 📊 **Logged**: All fixes are logged for monitoring
- 🎯 **Targeted**: Only affects functions that need it
- ⚡ **Fast**: Immediate fix, no waiting for health monitor

## Future Enhancements
- Add decorator to more critical functions
- Implement connection pooling with auto-recovery
- Add metrics dashboard for error tracking
- Create alerts for repeated errors

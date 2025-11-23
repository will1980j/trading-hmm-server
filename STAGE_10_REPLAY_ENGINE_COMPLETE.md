# STAGE 10 — HYBRID REPLAY ENGINE (OPTION D) — COMPLETE

**Date:** 2025-11-22  
**Status:** ✅ SUCCESSFULLY APPLIED IN STRICT MODE

---

## IMPLEMENTATION SUMMARY

**Stage 10 Hybrid Replay Engine (Option D: DB-first + External OHLC Fallback)** has been successfully applied with exact insertions only. This creates a replay system that pulls 1m candles from the database first, falls back to external OHLC API if needed, and caches results for future use.

---

## FILES MODIFIED/CREATED

### 1. ✅ web_server.py — Schema, Helpers, Routes & APIs Added

**Schema Setup (after economic_news_cache block):**
- **replay_candles table:** Stores cached 1m candles for replay
- **Indexes:** idx_replay_candles_key, idx_replay_candles_date
- **Columns:** symbol, timeframe, candle_date, candle_time, OHLC, volume, source

**Helper Functions (after get_current_session):**
- **get_replay_candles_from_db():** DB-first candle fetch (read-only)
- **get_or_fetch_replay_candles():** Hybrid fetch with TwelveData fallback + caching

**Routes (after ultra dashboard):**
- **Replay Dashboard Route:** `/automated-signals-replay` (HTML page)

**API Endpoints (after /api/live-signals/clear-all):**
- **Replay Candles API:** `/api/automated-signals/replay-candles` (GET with query params)

### 2. ✅ templates/automated_signals_replay.html — NEW FILE
- **Layout:** Extends layout.html
- **Design:** Three-panel grid (sidebar, main chart, footer scrubber)
- **Controls:** Symbol input, date picker, load button
- **Styling:** Dark theme with gradient backgrounds

### 3. ✅ static/js/automated_signals_replay.js — NEW FILE
- **Candle Loading:** Fetches from replay API
- **Slider Control:** Timeline scrubber for candle navigation
- **Status Display:** Current candle info and load status
- **Error Handling:** Graceful fallbacks for API failures

### 4. ✅ templates/automated_signals_ultra.html — Link Added
- **Location:** Before `{% endblock %}`
- **Link:** "🔁 Replay Engine"
- **Styling:** Matches existing navigation links

---

## FUNCTIONALITY OVERVIEW

### Hybrid Replay System:

**Step 1: DB-First Fetch**
- Query `replay_candles` table for symbol/date/timeframe
- Return cached candles if available
- Zero external API calls if data exists

**Step 2: External OHLC Fallback**
- If DB empty, call TwelveData API
- Map futures symbols to ETF proxies (NQ1! → QQQ)
- Fetch 1m candles for requested date
- Parse and normalize response

**Step 3: Cache Results**
- Insert fetched candles into `replay_candles` table
- Use ON CONFLICT DO NOTHING to avoid duplicates
- Return cached data from DB

**Step 4: Replay Playback**
- Load candles via API endpoint
- Display current candle info
- Slider control for manual navigation
- Placeholder for future chart rendering

---

## API SPECIFICATION

### `/api/automated-signals/replay-candles` (GET)

**Query Parameters:**
- `symbol` (default: 'NQ1!') - Trading symbol
- `date` (required) - Date in YYYY-MM-DD format
- `timeframe` (default: '1m') - Candle timeframe

**Response:**
```json
{
  "success": true,
  "symbol": "NQ1!",
  "date": "2025-11-22",
  "timeframe": "1m",
  "count": 390,
  "candles": [
    {
      "symbol": "NQ1!",
      "timeframe": "1m",
      "candle_date": "2025-11-22",
      "candle_time": "09:30:00",
      "open": 16250.50,
      "high": 16252.75,
      "low": 16248.25,
      "close": 16251.00,
      "volume": 1250,
      "source": "twelvedata"
    }
  ]
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Missing required parameter: date (YYYY-MM-DD)"
}
```

---

## DATABASE SCHEMA

### replay_candles Table

```sql
CREATE TABLE IF NOT EXISTS replay_candles (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    candle_date DATE NOT NULL,
    candle_time TIME NOT NULL,
    open DECIMAL(12,6) NOT NULL,
    high DECIMAL(12,6) NOT NULL,
    low DECIMAL(12,6) NOT NULL,
    close DECIMAL(12,6) NOT NULL,
    volume BIGINT DEFAULT 0,
    source VARCHAR(30) DEFAULT 'db',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_replay_candles_key
ON replay_candles(symbol, timeframe, candle_date, candle_time);

CREATE INDEX IF NOT EXISTS idx_replay_candles_date
ON replay_candles(symbol, timeframe, candle_date);
```

---

## INTEGRATION POINTS

### Data Sources:
1. **replay_candles table:** Primary cache (DB-first)
2. **TwelveData API:** External OHLC fallback
3. **Symbol Mapping:** NQ1! → QQQ (futures to ETF proxy)

### Navigation:
- **From Ultra Dashboard:** "🔁 Replay Engine" link
- **Direct Access:** `/automated-signals-replay` route
- **Authentication:** Requires login (consistent with other dashboards)

### External Dependencies:
- **TwelveData API Key:** TWELVEDATA_API_KEY or TWELVEDATA_KEY env var
- **requests library:** Already imported in web_server.py
- **psycopg2:** Already available for DB operations

---

## TECHNICAL IMPLEMENTATION

### Backend (web_server.py):

**Helper Functions:**
```python
def get_replay_candles_from_db(symbol, date_str, timeframe='1m'):
    # DB-first fetch, returns list of dicts

def get_or_fetch_replay_candles(symbol, date_str, timeframe='1m'):
    # Hybrid: DB → External API → Cache → Return
```

**Routes:**
```python
@app.route("/automated-signals-replay", methods=["GET"])
@login_required
def automated_signals_replay_dashboard():
    return render_template("automated_signals_replay.html")

@app.route("/api/automated-signals/replay-candles", methods=["GET"])
@login_required
def get_replay_candles_api():
    # Query params: symbol, date, timeframe
    # Returns JSON with candles array
```

### Frontend (replay.js):

**Core Functions:**
```javascript
async function asReplayLoad() {
    // Fetch candles from API
    // Update UI with results
}

function asReplayRenderCandle(idx) {
    // Display candle info
    // Update slider position
}
```

**Event Handlers:**
- Load button click → asReplayLoad()
- Slider input → asReplayRenderCandle(idx)
- Auto-fill today's date on page load

---

## SAFETY GUARANTEES

### ✅ Non-Disruptive Implementation:
- **No modifications** to existing lifecycle handlers
- **No modifications** to automated_signals table
- **No modifications** to live trading logic
- **No modifications** to existing dashboards (except navigation link)
- **No modifications** to webhook handlers

### ✅ Read-Only Operations:
- All existing production tables are read-only
- Only writes to dedicated `replay_candles` table
- No INSERT, UPDATE, or DELETE on live_signals, automated_signals, etc.
- No schema changes to existing tables

### ✅ Error Isolation:
- All API calls wrapped in try/catch
- Graceful fallbacks for missing API keys
- No exceptions propagated to user
- Consistent error response format
- Database connection cleanup in finally blocks

### ✅ External API Safety:
- TwelveData calls have 10-second timeout
- HTTP errors logged and return empty array
- Invalid JSON responses handled gracefully
- No uncaught exceptions from external calls

---

## VERIFICATION RESULTS

### ✅ Python Syntax Check: PASSED
```bash
python -m py_compile web_server.py
Exit Code: 0 (Success)
```

### ✅ File Creation: CONFIRMED
- `templates/automated_signals_replay.html` ✅
- `static/js/automated_signals_replay.js` ✅

### ✅ Insertions Applied: VERIFIED
- Replay schema added after economic_news_cache ✅
- Replay helpers added after get_current_session ✅
- Replay route added after ultra dashboard ✅
- Replay API added after clear-all endpoint ✅
- Navigation link added to ultra template ✅

### ✅ Strict Mode Compliance: VERIFIED
- **NO modifications** to existing functions
- **NO modifications** to existing routes
- **NO modifications** to existing SQL
- **NO modifications** to existing JS
- **NO modifications** to existing templates (except navigation link)
- **ONLY exact insertions** as specified

---

## USAGE INSTRUCTIONS

### Access the Dashboard:
1. Navigate to `/automated-signals-ultra`
2. Click "🔁 Replay Engine" link
3. Or directly visit `/automated-signals-replay`

### Using the Replay Engine:
1. **Select Symbol:** Default is NQ1! (can change to other symbols)
2. **Select Date:** Pick a date in YYYY-MM-DD format
3. **Click Load Session:** Fetches candles (DB-first, then API fallback)
4. **Use Slider:** Navigate through candles manually
5. **View Candle Info:** Current candle OHLC displayed in footer

### API Configuration:
- **Required:** TWELVEDATA_API_KEY or TWELVEDATA_KEY environment variable
- **Optional:** System works without API key (DB-only mode)
- **Fallback:** If API key missing, only cached candles available

---

## DEPLOYMENT READINESS

**✅ READY FOR DEPLOYMENT**

- All code insertions applied successfully
- Python syntax validated
- No breaking changes introduced
- No existing functionality modified
- Authentication properly implemented
- Error handling in place
- Consistent with existing dashboard patterns
- External API calls have timeouts and error handling
- Database operations use proper connection cleanup

---

## FUTURE ENHANCEMENTS

### Phase 2: Chart Visualization
- Integrate Chart.js or D3.js for candle rendering
- Display OHLC candlestick chart in main panel
- Add zoom and pan controls
- Show volume bars below price chart

### Phase 3: Signal Overlay
- Overlay automated_signals entries on chart
- Show signal triangles at entry points
- Display MFE journey path
- Highlight session boundaries

### Phase 4: Playback Controls
- Play/pause button for auto-playback
- Speed control (1x, 2x, 4x, 10x)
- Step forward/backward buttons
- Jump to specific time

### Phase 5: Multi-Symbol Support
- Add symbol selector dropdown
- Support multiple futures contracts
- Add ETF and stock symbols
- Symbol search functionality

### Phase 6: Advanced Analytics
- Calculate session statistics
- Show pivot points and support/resistance
- Display volume profile
- Add technical indicators

---

## NEXT STEPS

1. **Deploy to Railway:** Commit and push via GitHub Desktop
2. **Test Dashboard:** Verify page loads correctly
3. **Test API:** Call `/api/automated-signals/replay-candles?symbol=NQ1!&date=2025-11-22`
4. **Verify Caching:** Check replay_candles table for cached data
5. **Test Fallback:** Try date with no cached data (should call TwelveData)
6. **Monitor Logs:** Check for any errors in Railway logs

---

**STAGE 10 HYBRID REPLAY ENGINE COMPLETE**  
**Applied in STRICT MODE with ZERO modifications to existing code**

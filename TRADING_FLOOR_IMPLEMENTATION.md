# Trading Floor Command Center - Implementation Plan

## Status: IN PROGRESS

### Phase 1: Backend API ✅ COMPLETE
- Created `automated_signals_api.py` with real data endpoints
- `/api/automated-signals/dashboard-data` - Complete dashboard data
- `/api/automated-signals/mfe-distribution` - MFE histogram data
- NO FAKE DATA - All queries from signal_lab_v2_trades table

### Phase 2: Integration (NEXT)
1. Import API module in web_server.py
2. Register API endpoints
3. Test endpoints return real data

### Phase 3: Frontend Dashboard (AFTER PHASE 2)
Will rebuild `automated_signals_dashboard.html` with:
- Enhanced sidebar with navigation
- Active trades cards with real-time MFE
- Calendar heatmap (hourly trading activity)
- Completed trades list with DB verification
- Session performance breakdown
- MFE distribution chart
- Real-time WebSocket updates

### Phase 4: News Integration (OPTIONAL)
- Economic calendar API integration
- High/medium impact event display
- Auto-pause warnings

## Data Sources (ALL REAL):
- `signal_lab_v2_trades` table for all trade data
- `active_trade` boolean for active vs completed
- `current_mfe` for live tracking
- `mfe` for final results
- Session, bias, entry_price, stop_loss all from DB

## Next Step:
Integrate API into web_server.py

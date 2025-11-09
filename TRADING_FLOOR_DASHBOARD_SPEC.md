# Trading Floor Command Center - Complete Implementation Spec

## Dashboard Structure

### Layout
- **Sidebar (280px fixed)**: Navigation, quick stats, session breakdown
- **Main Content**: Active trades, calendar, completed trades, charts
- **Connection Indicator**: Live WebSocket status

### Color Scheme (Dark Theme)
- Background: `#0a0e27`
- Sidebar: `#1a1f2e`
- Accent: `#00d4ff` (cyan)
- Success: `#10b981` (green)
- Danger: `#ef4444` (red)
- Warning: `#fbbf24` (yellow)

## Sections to Build

### 1. Sidebar
- Platform branding
- Today's Performance (Total Signals, Win Rate, Avg MFE)
- Session Breakdown (All 6 sessions with counts)
- Navigation links

### 2. Top Stats Bar
- Total Signals Today
- Active Trades
- Completed Today
- Avg MFE

### 3. Active Trades Section
- Trade cards with:
  - Trade ID, Direction (LONG/SHORT)
  - Current MFE (pulsing animation)
  - Entry price, Stop loss
  - Session info
  - Duration timer
  - Pulsing indicator for live status

### 4. Calendar Heatmap
- Hourly blocks (6 AM - 8 PM)
- Color intensity by trade count
- Hover: trade details for that hour

### 5. Completed Trades List
- Trade outcome (BE/SL)
- Final MFE
- Entry/exit info
- Duration
- Database verification badge

### 6. Session Performance Chart
- Bar chart showing trades per session
- All 6 sessions

### 7. MFE Distribution Chart
- Histogram showing MFE distribution
- 7 buckets (0-0.5R through 3R+)

## Data Flow
- Initial load: Fetch `/api/automated-signals/dashboard-data`
- MFE chart: Fetch `/api/automated-signals/mfe-distribution`
- WebSocket: Real-time MFE updates
- Refresh: Every 5 seconds

## Implementation Notes
- NO FAKE DATA - Show empty states when no data
- Real-time WebSocket for active trade updates
- Proper error handling
- Loading states
- Responsive design

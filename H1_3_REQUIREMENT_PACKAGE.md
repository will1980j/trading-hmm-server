=== H1.3 REQUIREMENT PACKAGE ===

Objective:
Build a production-ready Time Analysis dashboard that analyzes trading performance across temporal dimensions (sessions, hours, days, months) using REAL DATA ONLY from the Signal Lab database, with NO FAKE DATA fallbacks.

Description:
H1.3 Time Analysis is a comprehensive temporal analytics dashboard that helps traders identify optimal trading windows by analyzing historical performance patterns. The dashboard must display session-based performance (ASIA, LONDON, NY PRE, NY AM, NY LUNCH, NY PM), hourly distributions, day-of-week patterns, and monthly trends. All data must come from the existing `signal_lab_trades` table with proper timezone handling (US Eastern Time). The dashboard follows the deep blue fintech theme established in H1.1 and H1.2, with consistent navigation and NO FAKE DATA.

Functional Requirements:
- FR1: Display overall performance metrics (Win Rate, Expectancy, Avg R, Total Trades, Best Session) at the top of the dashboard
- FR2: Implement session performance analysis showing win rate, expectancy, and trade count for each of the 6 trading sessions (ASIA, LONDON, NY PRE, NY AM, NY LUNCH, NY PM)
- FR3: Create session heatmap visualization showing performance intensity across all sessions
- FR4: Build hourly analysis chart (24-hour distribution) showing performance by hour of day in Eastern Time
- FR5: Implement day-of-week analysis showing which days (Monday-Friday) perform best
- FR6: Create monthly performance trends showing performance evolution over time
- FR7: Add date range filter allowing users to analyze specific time periods
- FR8: Display "Best Time Windows" for each session showing optimal trading hours
- FR9: Implement data tables alongside charts showing detailed statistics
- FR10: Query data from `signal_lab_trades` table using proper timezone conversion
- FR11: Handle empty states gracefully with clear "No data available" messages (NO FAKE DATA)
- FR12: Calculate all metrics using R-multiple methodology (not dollar amounts)
- FR13: Integrate with existing navigation system (consistent header/nav from H1.1/H1.2)
- FR14: Use roadmap lock macros for future features (Dataset V2, Advanced Filters)
- FR15: Implement responsive design that works on desktop and tablet devices

Non-Functional Requirements:
- NFR1: Performance - Dashboard must load and render within 2 seconds with up to 2000 trades
- NFR2: Data Integrity - ZERO tolerance for fake/fallback data; show errors instead
- NFR3: Timezone Accuracy - All time-based calculations must use US Eastern Time (matching Signal Lab)
- NFR4: Visual Consistency - Must match deep blue fintech theme from H1.1/H1.2 (#0a1324, #0d1b33, #1e2a44)
- NFR5: Code Quality - Clean, documented JavaScript with proper error handling
- NFR6: Database Efficiency - Optimize queries to minimize database load
- NFR7: Browser Compatibility - Must work in Chrome, Firefox, Safari, Edge (latest versions)
- NFR8: Accessibility - Proper ARIA labels, keyboard navigation, screen reader support
- NFR9: Security - All database queries must use parameterized statements (SQL injection prevention)
- NFR10: Maintainability - Follow existing code patterns from H1.1/H1.2 implementations

File Impact Map:

Frontend Files:
- templates/time_analysis.html - CREATE/REPLACE - Main dashboard HTML template
- static/css/time_analysis.css - CREATE/REPLACE - Dashboard-specific styles
- static/js/time_analysis.js - CREATE/REPLACE - Dashboard JavaScript logic
- templates/layout.html - NO CHANGE - Uses existing navigation

Backend Files:
- web_server.py - MODIFY - Add `/time-analysis` route with @login_required decorator
- web_server.py - MODIFY - Add `/api/time-analysis/data` API endpoint for fetching analytics
- web_server.py - MODIFY - Add `/api/time-analysis/session-breakdown` API endpoint
- web_server.py - MODIFY - Add `/api/time-analysis/hourly-distribution` API endpoint
- db_connection.py - NO CHANGE - Uses existing database connection

Database Files:
- NO NEW TABLES - Uses existing `signal_lab_trades` table
- Query columns: signal_date, signal_time, session, direction, mfe, outcome, r_multiple

Configuration Files:
- roadmap_state.py - NO CHANGE (module completion handled separately)
- templates/_macros.html - NO CHANGE - Uses existing roadmap_locked macro

Documentation Files:
- H1_3_TIME_ANALYSIS_COMPLETE.md - CREATE - Implementation completion documentation

Data Flow Summary:
1. User navigates to `/time-analysis` route (authenticated)
2. Frontend loads and requests data from `/api/time-analysis/data` with optional date range filters
3. Backend queries `signal_lab_trades` table, filtering by date range if provided
4. Backend performs timezone conversion (database UTC → Eastern Time for display)
5. Backend calculates session-based metrics (win rate, expectancy, avg R per session)
6. Backend calculates hourly distribution (performance by hour 0-23 Eastern Time)
7. Backend calculates day-of-week performance (Monday-Friday)
8. Backend calculates monthly trends (performance by month)
9. Backend returns JSON response with all calculated metrics
10. Frontend renders charts using Chart.js library
11. Frontend displays session heatmap with color-coded performance
12. Frontend displays data tables with detailed breakdowns
13. User can adjust date range filters, triggering new API requests
14. If no data exists, frontend displays "No data available" (NO FAKE DATA)

Dependencies:
- Chart.js (CDN) - Already used in platform for chart rendering
- Python Flask - Existing backend framework
- PostgreSQL (Railway) - Existing database
- pytz - Python timezone library for Eastern Time conversion
- datetime - Python standard library for date/time manipulation
- Bootstrap (optional) - For responsive grid layout
- Existing authentication system (@login_required decorator)
- Existing navigation system (templates/layout.html)
- Existing roadmap lock system (templates/_macros.html)

Edge Cases:
- EC1: No trades in database → Display "No data available for analysis" message
- EC2: Date range filter returns zero trades → Display "No trades in selected date range"
- EC3: Session has zero trades → Display "0 trades" with N/A for win rate/expectancy
- EC4: All trades in one session → Other sessions show "No data"
- EC5: Timezone edge cases (DST transitions) → Use pytz for proper handling
- EC6: Invalid date range (end before start) → Show validation error
- EC7: Database connection failure → Display error message with retry option
- EC8: Extremely large dataset (>5000 trades) → Implement pagination or aggregation
- EC9: User not authenticated → Redirect to login page
- EC10: API endpoint returns error → Display user-friendly error message
- EC11: Chart.js fails to load → Display fallback data tables only
- EC12: Browser doesn't support JavaScript → Display message requiring JavaScript
- EC13: Mobile device access → Responsive layout adapts to smaller screens
- EC14: Trades with missing session data → Categorize as "Unknown" or exclude from session analysis
- EC15: Trades with invalid R-multiple values → Exclude from calculations, log warning

Acceptance Criteria:
- AC1: Dashboard displays at `/time-analysis` route with authentication required
- AC2: Overall metrics (Win Rate, Expectancy, Avg R, Total Trades, Best Session) display correctly at top
- AC3: Session performance section shows accurate metrics for all 6 sessions (ASIA, LONDON, NY PRE, NY AM, NY LUNCH, NY PM)
- AC4: Session heatmap visualizes performance intensity with color coding
- AC5: Hourly analysis chart displays 24-hour distribution with accurate Eastern Time
- AC6: Day-of-week analysis shows Monday-Friday performance correctly
- AC7: Monthly trends chart displays performance evolution over time
- AC8: Date range filter successfully filters data and updates all charts/metrics
- AC9: "Best Time Windows" section identifies optimal trading hours per session
- AC10: Data tables display alongside charts with detailed statistics
- AC11: All data comes from `signal_lab_trades` table (verified by database query logs)
- AC12: NO FAKE DATA appears anywhere on the dashboard (strict validation)
- AC13: Empty states display "No data available" messages (not fake data)
- AC14: Dashboard matches deep blue fintech theme from H1.1/H1.2
- AC15: Navigation header is consistent with other dashboards
- AC16: Roadmap lock macros display for future features (Dataset V2)
- AC17: All timezone calculations use US Eastern Time correctly
- AC18: Dashboard loads within 2 seconds with typical dataset (500-2000 trades)
- AC19: All API endpoints return proper JSON responses with error handling
- AC20: Dashboard is responsive and works on desktop/tablet devices
- AC21: No console errors in browser developer tools
- AC22: All charts render correctly using Chart.js
- AC23: Database queries use parameterized statements (no SQL injection vulnerabilities)
- AC24: Code follows existing patterns from H1.1/H1.2 implementations
- AC25: Documentation file (H1_3_TIME_ANALYSIS_COMPLETE.md) is created with implementation details

=== END OF H1.3 REQUIREMENT PACKAGE ===

FORWARD THIS ENTIRE DOCUMENT TO CHATGPT FOR H1.3 STRICT PATCH PROMPT GENERATION.

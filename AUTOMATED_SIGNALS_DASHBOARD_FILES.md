# Files to Share for Automated Signals Dashboard Development

## Essential Files (Must Share)

### 1. Frontend Files
```
templates/automated_signals_ultra.html
static/js/automated_signals_ultra.js
static/css/automated_signals_ultra.css
```
**Why:** These are the actual dashboard files that need enhancement

### 2. Backend API Files
```
automated_signals_api_robust.py
web_server.py (relevant routes only)
```
**Why:** API endpoints that provide data to the dashboard

### 3. Database Schema
```
database/data_quality_schema.sql
```
**Why:** Shows the `automated_signals` table structure and available fields

### 4. Data Quality System
```
data_quality_api.py
```
**Why:** Import system and data quality endpoints

## Context Files (Recommended)

### 5. Architecture Documentation
```
ARCHITECTURE_DOCUMENTATION.md
API_QUICK_REFERENCE.md
WEBAPP_STRUCTURE_SPECIFICATION.md
```
**Why:** Complete system architecture and API reference

### 6. Current Status
```
DATA_QUALITY_PHASE1_COMPLETE.md
AUTOMATED_SIGNALS_COMPLETE_SYSTEM_REVIEW.md
```
**Why:** What's already built and what needs work

### 7. Specifications
```
DATA_QUALITY_SYSTEM_SPEC.md
ALL_SIGNALS_TABLE_ENHANCEMENT_SPEC.md
```
**Why:** Requirements and design specs

## Optional Files (If Needed)

### 8. Example Data
```
indicator_data_inspector.py
test_data_quality_phase1.py
```
**Why:** Shows data structure and testing approach

### 9. Import System
```
indicator_bulk_import.py
```
**Why:** How indicator data gets imported

### 10. Indicator Reference
```
complete_automated_trading_system.pine (first 500 lines only)
```
**Why:** Shows what data is available from indicator (don't share entire 2,537 line file)

## Minimal File List (If Limited)

If you can only share a few files, share these 5:

1. **templates/automated_signals_ultra.html** - Dashboard HTML
2. **static/js/automated_signals_ultra.js** - Dashboard JavaScript
3. **automated_signals_api_robust.py** - Backend API
4. **API_QUICK_REFERENCE.md** - API documentation
5. **DATA_QUALITY_SYSTEM_SPEC.md** - Requirements

## What to Tell the AI

### Context to Provide:
```
"I have an Automated Signals Dashboard for a NASDAQ day trading platform. 
The dashboard displays trading signals with dual strategy tracking (BE=1 and No-BE).

Current features:
- Active Trades table
- Completed Trades table
- Cancelled Signals table
- Calendar view
- Data Quality tab (Phase 1 complete)

Data source:
- PostgreSQL database (Railway)
- Table: automated_signals
- Event-based architecture (multiple rows per trade_id)
- Real-time WebSocket updates

Tech stack:
- Frontend: HTML, JavaScript, Bootstrap, Chart.js
- Backend: Python Flask
- Database: PostgreSQL
- Deployment: Railway cloud

I need help enhancing the dashboard with [specific request]."
```

### Specific Requests You Might Have:
- Enhanced visualizations (charts, graphs)
- Better filtering and sorting
- Performance improvements
- Mobile responsiveness
- New features (trade journey, analytics, etc.)
- UI/UX improvements

## Files NOT to Share

❌ **Don't share these** (too large or not relevant):
- Complete indicator file (2,537 lines - too large)
- All the check_*.py diagnostic scripts
- All the fix_*.py scripts
- All the test_*.py scripts
- Documentation files (unless specifically needed)
- Backup files
- Git-related files

## How to Share

### Option 1: Create a Package
```bash
# Create a folder with essential files
mkdir automated_signals_package
cp templates/automated_signals_ultra.html automated_signals_package/
cp static/js/automated_signals_ultra.js automated_signals_package/
cp static/css/automated_signals_ultra.css automated_signals_package/
cp automated_signals_api_robust.py automated_signals_package/
cp API_QUICK_REFERENCE.md automated_signals_package/
cp DATA_QUALITY_SYSTEM_SPEC.md automated_signals_package/
```

### Option 2: Share via GitHub Gist
1. Create a new Gist
2. Add the 5-6 essential files
3. Share the Gist URL

### Option 3: Copy-Paste in Chat
Share files in this order:
1. API_QUICK_REFERENCE.md (context)
2. DATA_QUALITY_SYSTEM_SPEC.md (requirements)
3. automated_signals_api_robust.py (backend)
4. automated_signals_ultra.html (frontend HTML)
5. automated_signals_ultra.js (frontend JS)

## Summary

**Minimum viable set:** 5 files
**Recommended set:** 10 files
**Complete set:** 15 files

**Start with the minimum set and add more files if the AI needs additional context.**

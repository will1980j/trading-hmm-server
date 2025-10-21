@echo off
echo ========================================
echo Webhook Signal Debugging Setup
echo ========================================
echo.

echo Step 1: Initializing database tables...
python init_webhook_debug.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Database initialization failed
    pause
    exit /b 1
)
echo.

echo Step 2: Testing database connection...
python -c "from database.railway_db import RailwayDB; db = RailwayDB(); print('✅ Database connected')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Database connection failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start your server: python web_server.py
echo 2. Open webhook monitor: http://localhost:5000/webhook-monitor
echo 3. Test both signal types using the dashboard buttons
echo 4. Monitor signal reception for both Bullish and Bearish
echo.
echo Monitoring endpoints:
echo - Dashboard: /webhook-monitor
echo - Stats: /api/webhook-stats
echo - Health: /api/webhook-health
echo - Diagnostic: /api/webhook-diagnostic
echo.
pause

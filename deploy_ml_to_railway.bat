@echo off
echo ========================================
echo   Deploying ML Intelligence to Railway
echo ========================================
echo.

echo Step 1: Testing ML locally...
python test_ml_local.py
if errorlevel 1 (
    echo.
    echo ❌ Local tests failed! Fix errors before deploying.
    pause
    exit /b 1
)

echo.
echo Step 2: Adding files to git...
git add unified_ml_intelligence.py
git add ml_intelligence_dashboard.html
git add ML_INTELLIGENCE_SOLUTION.md
git add RAILWAY_ML_DEPLOYMENT.md
git add test_ml_local.py
git add deploy_ml_to_railway.bat
git add web_server.py

echo.
echo Step 3: Committing changes...
git commit -m "Deploy unified ML intelligence system to Railway"

echo.
echo Step 4: Pushing to Railway...
git push origin main

echo.
echo ========================================
echo   ✅ Deployment Complete!
echo ========================================
echo.
echo Railway will auto-deploy in ~2 minutes
echo.
echo Next steps:
echo 1. Visit: https://your-app.railway.app/ml-dashboard
echo 2. Click: "Train ML Models"
echo 3. Review: ML insights and recommendations
echo.
pause

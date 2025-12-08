# Auto-deploy script for Railway
# Run this after making changes to deploy them

Write-Host "=== Auto Deploy Script ===" -ForegroundColor Cyan

# Stage modified files
Write-Host "Staging files..." -ForegroundColor Yellow
git add web_server.py
git add automated_signals_api_robust.py
git add automated_signals_state.py
git add .env
git add "static/js/automated_signals_ultra.js"
git add "templates/automated_signals_ultra.html"

# Show status
Write-Host "`nGit status:" -ForegroundColor Yellow
git status --short

# Commit with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$message = "Auto-deploy: Phase E2 lifecycle fixes - $timestamp"

Write-Host "`nCommitting with message: $message" -ForegroundColor Yellow
git commit -m $message

# Push to trigger Railway deployment
Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✅ Push complete! Railway will auto-deploy in 2-3 minutes." -ForegroundColor Green
Write-Host "Check Railway logs for deployment progress." -ForegroundColor Cyan

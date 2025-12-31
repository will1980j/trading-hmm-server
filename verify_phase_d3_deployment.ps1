# Phase D.3 Deployment Verification Script
# Verifies Historical API v1 endpoints are operational

$base = "https://web-production-f8c3.up.railway.app"

Write-Host "Phase D.3 Deployment Verification" -ForegroundColor Cyan
Write-Host "=" * 80

# Test 1: Homepage loads
Write-Host "`nTest 1: Homepage loads..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest "$base/" -TimeoutSec 20
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Homepage: $($response.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "❌ Homepage: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Homepage failed: $_" -ForegroundColor Red
}

# Test 2: Roadmap API
Write-Host "`nTest 2: Roadmap API..." -ForegroundColor Yellow
try {
    $roadmap = Invoke-RestMethod "$base/api/roadmap" -TimeoutSec 20
    Write-Host "✅ Roadmap API: 200" -ForegroundColor Green
} catch {
    Write-Host "❌ Roadmap API failed: $_" -ForegroundColor Red
}

# Test 3: Historical API - World endpoint
Write-Host "`nTest 3: Historical API - World endpoint..." -ForegroundColor Yellow
try {
    $world = Invoke-RestMethod "$base/api/hist/v1/world?symbol=GLBX.MDP3:NQ&ts=2025-12-02T00:14:00Z" -TimeoutSec 20
    if ($world.timestamp -and $world.symbol) {
        Write-Host "✅ World endpoint: 200" -ForegroundColor Green
        Write-Host "   Symbol: $($world.symbol)" -ForegroundColor Gray
        Write-Host "   Timestamp: $($world.timestamp)" -ForegroundColor Gray
    } else {
        Write-Host "❌ World endpoint: Invalid response structure" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ World endpoint failed: $_" -ForegroundColor Red
}

# Test 4: Historical API - Quality Coverage
Write-Host "`nTest 4: Historical API - Quality Coverage..." -ForegroundColor Yellow
try {
    $coverage = Invoke-RestMethod "$base/api/hist/v1/quality/coverage?symbol=GLBX.MDP3:NQ&start=2025-12-02T00:10:00Z&end=2025-12-02T00:30:00Z" -TimeoutSec 20
    if ($coverage.pass -ne $null) {
        $status = if ($coverage.pass) { "PASS" } else { "FAIL" }
        $color = if ($coverage.pass) { "Green" } else { "Red" }
        Write-Host "✅ Coverage endpoint: 200 ($status)" -ForegroundColor $color
    } else {
        Write-Host "❌ Coverage endpoint: Invalid response" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Coverage endpoint failed: $_" -ForegroundColor Red
}

# Test 5: Historical API - Quality Determinism
Write-Host "`nTest 5: Historical API - Quality Determinism..." -ForegroundColor Yellow
try {
    $det = Invoke-RestMethod "$base/api/hist/v1/quality/determinism?symbol=GLBX.MDP3:NQ&start=2025-12-02T00:10:00Z&end=2025-12-02T00:20:00Z" -TimeoutSec 20
    if ($det.dataset_hash) {
        Write-Host "✅ Determinism endpoint: 200" -ForegroundColor Green
        Write-Host "   Hash: $($det.dataset_hash)" -ForegroundColor Gray
        Write-Host "   Rows: $($det.row_count)" -ForegroundColor Gray
    } else {
        Write-Host "❌ Determinism endpoint: Invalid response" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Determinism endpoint failed: $_" -ForegroundColor Red
}

Write-Host "`n" + "=" * 80
Write-Host "Verification complete" -ForegroundColor Cyan

# Verify Homepage Canonical Template
# Checks: No video tag, /roadmap link exists, fingerprint comment present

Write-Host "=" -NoNewline; Write-Host ("=" * 70)
Write-Host "HOMEPAGE CANONICAL TEMPLATE VERIFICATION"
Write-Host "=" -NoNewline; Write-Host ("=" * 70)
Write-Host ""

$templatePath = "templates/homepage.html"

if (-not (Test-Path $templatePath)) {
    Write-Host "❌ ERROR: $templatePath not found!" -ForegroundColor Red
    exit 1
}

$content = Get-Content $templatePath -Raw

# Check 1: No <video> tag
Write-Host "CHECK 1: No <video> tag" -ForegroundColor Cyan
if ($content -match '<video') {
    Write-Host "  ❌ FAIL: <video> tag found in template" -ForegroundColor Red
    $videoMatch = [regex]::Match($content, '<video[^>]*>')
    Write-Host "  Found: $($videoMatch.Value)" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ PASS: No <video> tag found" -ForegroundColor Green
}
Write-Host ""

# Check 2: /roadmap link exists
Write-Host "CHECK 2: /roadmap link exists" -ForegroundColor Cyan
if ($content -match 'href=[''"]*/roadmap[''"]') {
    Write-Host "  ✅ PASS: /roadmap link found" -ForegroundColor Green
    $roadmapMatch = [regex]::Match($content, 'href=[''"]*/roadmap[''"][^>]*>([^<]+)')
    if ($roadmapMatch.Success) {
        Write-Host "  Link text: $($roadmapMatch.Groups[1].Value)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ❌ FAIL: /roadmap link not found" -ForegroundColor Red
}
Write-Host ""

# Check 3: Fingerprint comment exists
Write-Host "CHECK 3: Fingerprint comment exists" -ForegroundColor Cyan
if ($content -match '<!-- SERVED_TEMPLATE: homepage\.html') {
    Write-Host "  ✅ PASS: Fingerprint comment found" -ForegroundColor Green
    $fingerprintMatch = [regex]::Match($content, '<!-- SERVED_TEMPLATE: ([^>]+) -->')
    if ($fingerprintMatch.Success) {
        Write-Host "  Fingerprint: $($fingerprintMatch.Groups[1].Value)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ❌ FAIL: Fingerprint comment not found" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "=" -NoNewline; Write-Host ("=" * 70)
$checks = @(
    ($content -notmatch '<video'),
    ($content -match 'href=[''"]*/roadmap[''"]'),
    ($content -match '<!-- SERVED_TEMPLATE: homepage\.html')
)
$passCount = ($checks | Where-Object { $_ }).Count
$totalChecks = $checks.Count

if ($passCount -eq $totalChecks) {
    Write-Host "✅ ALL CHECKS PASSED ($passCount/$totalChecks)" -ForegroundColor Green
} else {
    Write-Host "❌ SOME CHECKS FAILED ($passCount/$totalChecks)" -ForegroundColor Red
}
Write-Host "=" -NoNewline; Write-Host ("=" * 70)

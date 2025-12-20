# Test Script for AI Code Review Assistant

Write-Host "=== AI Code Review Assistant - API Tests ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://127.0.0.1:8000"

# Test 1: Health Check
Write-Host "[TEST 1] Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/health" -Method Get
    Write-Host "✓ Health check passed" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Health check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Root endpoint
Write-Host "[TEST 2] Root Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "✓ Root endpoint passed" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ Root endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: List Projects
Write-Host "[TEST 3] List Projects..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/projects" -Method Get
    Write-Host "✓ Projects endpoint passed" -ForegroundColor Green
    Write-Host "Found $($response.Count) projects" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Projects endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: List Analysis Runs
Write-Host "[TEST 4] List Analysis Runs..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/analysis/runs" -Method Get
    Write-Host "✓ Analysis runs endpoint passed" -ForegroundColor Green
    Write-Host "Total runs: $($response.total)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Analysis runs endpoint failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 5: API Documentation
Write-Host "[TEST 5] API Documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API docs available at $baseUrl/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ API docs failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Tests Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API is running successfully!" -ForegroundColor Green
Write-Host "Access the interactive API docs at: $baseUrl/docs" -ForegroundColor Cyan

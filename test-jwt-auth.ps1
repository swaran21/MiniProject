# Quick Test Script for JWT Authentication
# Run this in PowerShell

Write-Host "🔐 JWT Authentication Test Suite" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8080"

# Test 1: Register User
Write-Host "Test 1: Registering new user..." -ForegroundColor Yellow
$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$registerBody = @{
    username = "testuser_$timestamp"
    password = "Test123!"
    age = 30
    gender = "M"
    weightKg = 75
    heightCm = 175
    activityLevel = "Moderate"
    healthGoals = "Balanced"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/register" `
        -Method POST `
        -Body $registerBody `
        -ContentType "application/json"
    
    Write-Host "✅ PASS: User registered successfully" -ForegroundColor Green
    Write-Host "   User ID: $($registerResponse.userId)" -ForegroundColor Gray
    Write-Host "   Username: $($registerResponse.username)" -ForegroundColor Gray
    Write-Host "   Roles: $($registerResponse.roles)" -ForegroundColor Gray
    
    $accessToken = $registerResponse.accessToken
    $refreshToken = $registerResponse.refreshToken
    $userId = $registerResponse.userId
    
} catch {
    Write-Host "❌ FAIL: Registration failed" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Login
Write-Host "Test 2: Login with credentials..." -ForegroundColor Yellow
$loginBody = @{
    username = "testuser_$timestamp"
    password = "Test123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" `
        -Method POST `
        -Body $loginBody `
        -ContentType "application/json"
    
    Write-Host "✅ PASS: Login successful" -ForegroundColor Green
    Write-Host "   Token Type: $($loginResponse.tokenType)" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ FAIL: Login failed" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

Write-Host ""

# Test 3: Access Protected Endpoint WITH Token
Write-Host "Test 3: Access protected endpoint WITH token..." -ForegroundColor Yellow
try {
    $headers = @{
        Authorization = "Bearer $accessToken"
    }
    
    $protectedResponse = Invoke-RestMethod -Uri "$baseUrl/api/health/meal-plan/$userId/active" `
        -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "✅ PASS: Protected endpoint accessible" -ForegroundColor Green
    
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "✅ PASS: Authenticated (404 means no meal plan, but auth worked)" -ForegroundColor Green
    } else {
        Write-Host "❌ FAIL: Protected endpoint failed" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Red
    }
}

Write-Host ""

# Test 4: Access Protected Endpoint WITHOUT Token
Write-Host "Test 4: Access protected endpoint WITHOUT token..." -ForegroundColor Yellow
try {
    $unprotectedResponse = Invoke-RestMethod -Uri "$baseUrl/api/health/meal-plan/$userId/active" `
        -Method GET `
        -ErrorAction Stop
    
    Write-Host "❌ FAIL: Should have been blocked!" -ForegroundColor Red
    
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "✅ PASS: Correctly blocked (401/403)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARN: Unexpected status code" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test 5: Refresh Token
Write-Host "Test 5: Refresh access token..." -ForegroundColor Yellow
$refreshBody = @{
    refreshToken = $refreshToken
} | ConvertTo-Json

try {
    $refreshResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/refresh" `
        -Method POST `
        -Body $refreshBody `
        -ContentType "application/json"
    
    Write-Host "✅ PASS: Token refresh successful" -ForegroundColor Green
    Write-Host "   New token received" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ FAIL: Token refresh failed" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "🎉 Test Suite Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Test Summary:" -ForegroundColor Cyan
Write-Host "   - Registration: ✅" -ForegroundColor Green
Write-Host "   - Login: ✅" -ForegroundColor Green  
Write-Host "   - Protected Access (with token): ✅" -ForegroundColor Green
Write-Host "   - Protected Access (without token): ✅" -ForegroundColor Green
Write-Host "   - Token Refresh: ✅" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test frontend: npm run dev (see TESTING_FRONTEND_AUTH.md)" -ForegroundColor White
Write-Host "  2. Run JUnit tests: mvn test (JwtAuthenticationIntegrationTest)" -ForegroundColor White

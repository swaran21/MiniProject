# JWT Authentication API Testing with cURL

## Prerequisites
- Backend running on `http://localhost:8080`
- Commands are for PowerShell (Windows)

---

## 1. Register a New User

```powershell
curl -X POST http://localhost:8080/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "password": "Test123!",
    "age": 30,
    "gender": "M",
    "weightKg": 75,
    "heightCm": 175,
    "activityLevel": "Moderate",
    "healthGoals": "Balanced",
    "dietaryRestrictions": "None"
  }'
```

**Expected Response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiJ9...",
  "tokenType": "Bearer",
  "userId": 1,
  "username": "testuser",
  "roles": "USER",
  "expiresIn": 900000
}
```

---

## 2. Login with Existing User

```powershell
curl -X POST http://localhost:8080/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }'
```

**Expected Response:** Same as registration

**Save the tokens:**
```powershell
# Copy accessToken from response
$token = "YOUR_ACCESS_TOKEN_HERE"
```

---

## 3. Access Protected Endpoint (WITH Token)

```powershell
# Get active meal plan (requires JWT)
curl -X GET "http://localhost:8080/api/health/meal-plan/1/active" `
  -H "Authorization: Bearer $token"
```

**Expected:** 
- If meal plan exists: Returns meal plan JSON
- If no meal plan: 404 (but authenticated)

---

## 4. Access Protected Endpoint (WITHOUT Token)

```powershell
# Try without authentication
curl -X GET "http://localhost:8080/api/health/meal-plan/1/active"
```

**Expected Response:** `401 Unauthorized` or `403 Forbidden`

---

## 5. Test Invalid Token

```powershell
curl -X GET "http://localhost:8080/api/health/meal-plan/1/active" `
  -H "Authorization: Bearer INVALID_TOKEN_HERE"
```

**Expected:** `401 Unauthorized`

---

## 6. Refresh Access Token

```powershell
# Use refreshToken from login response
$refreshToken = "YOUR_REFRESH_TOKEN_HERE"

curl -X POST http://localhost:8080/api/auth/refresh `
  -H "Content-Type: application/json" `
  -d "{\"refreshToken\": \"$refreshToken\"}"
```

**Expected Response:**
```json
{
  "accessToken": "NEW_ACCESS_TOKEN",
  "tokenType": "Bearer",
  "expiresIn": 900000
}
```

---

## 7. Test Other Protected Endpoints

### Recipe Details (Protected)
```powershell
curl -X GET http://localhost:8080/api/recipes/1/details `
  -H "Authorization: Bearer $token"
```

### Save Meal Plan (Protected)
```powershell
curl -X POST http://localhost:8080/api/health/meal-plan/save `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "userId": 1,
    "planData": {
      "planId": "test-plan-123",
      "durationDays": 7,
      "dailyPlan": []
    }
  }'
```

---

## 8. Test Public Endpoints (Should Work Without Token)

### Health Check
```powershell
curl http://localhost:8080/health
```

### Root Endpoint
```powershell
curl http://localhost:8080/
```

---

## Testing Checklist

- [ ] ✅ Register new user → Returns JWT tokens
- [ ] ✅ Login with credentials → Returns tokens
- [ ] ✅ Access protected endpoint WITH token → Success
- [ ] ✅ Access protected endpoint WITHOUT token → 401/403
- [ ] ✅ Access with invalid token → 401
- [ ] ✅ Refresh token → New access token
- [ ] ✅ Public endpoints work without token

---

## Troubleshooting

### Error: Connection Refused
- **Solution:** Make sure backend is running: `mvn spring-boot:run`

### Error: 401 Unauthorized
- **Check:** Is token included in Authorization header?
- **Check:** Is token formatted as `Bearer <token>`?
- **Check:** Has token expired? (15 min for access token)

### Error: 403 Forbidden
- **Check:** Does user have required role?
- **Check:** Is endpoint actually protected?

---

## Bash/Linux Version

For Linux/Mac users, replace `` ` `` with `\`:

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }'
```

# Frontend JWT Authentication Manual Testing Guide

## Test Environment Setup

1. **Start Backend:**
   ```powershell
   cd recipe-backend/recipe
   mvn spring-boot:run
   ```

2. **Start Frontend:**
   ```powershell
   cd recipe-ai-frontend
   npm run dev
   ```

3. **Open Browser:** http://localhost:5173

---

## Test Scenarios

### ✅ Test 1: User Registration

**Steps:**
1. Open http://localhost:5173
2. Click "Register" (toggle link at bottom)
3. Fill in the form:
   - Username: `testuser123`
   - Password: `Test123!`
   - Age: `30`
   - Gender: `Male`
   - Weight: `75`
   - Height: `175`
   - Activity Level: `Moderate`
   - Health Goal: `Balanced Diet`
4. Click "Create Account"

**Expected Result:**
- ✅ Redirected to main app dashboard
- ✅ User logged in automatically
- ✅ Can see username in sidebar
- ✅ No errors in console

**Check localStorage (F12 → Application → localStorage):**
- `accessToken` - Present (JWT token)
- `refreshToken` - Present (JWT token)
- `user` - JSON with userId, username, roles

---

### ✅ Test 2: User Login

**Steps:**
1. If logged in, logout first (click logout in sidebar)
2. On login screen, enter:
   - Username: `testuser123`
   - Password: `Test123!`
3. Click "Login"

**Expected Result:**
- ✅ Redirected to dashboard
- ✅ Tokens stored in localStorage
- ✅ User info displayed

---

### ✅ Test 3: Invalid Login

**Steps:**
1. Try to login with wrong password
2. Try to login with non-existent username

**Expected Result:**
- ❌ Error message displayed
- ❌ "Invalid credentials" or similar
- ❌ Not logged in

---

### ✅ Test 4: Protected Routes Access

**Steps:**
1. After successful login
2. Navigate to different tabs:
   - Diet Tracker
   - Health Profile
   - Medical Meal Planner
   - Browse Recipes

**Expected Result:**
- ✅ All tabs accessible
- ✅ Data loads correctly
- ✅ No 401/403 errors in console (F12 → Network tab)

---

### ✅ Test 5: Automatic Token Refresh

**Steps:**
1. Login successfully
2. Open browser DevTools (F12) → Network tab
3. Wait 15-20 minutes (or modify JWT expiration to 1 min for faster testing)
4. Make an API call (e.g., view meal plan, click any tab)

**Expected Result:**
- ✅ Request initially fails with 401
- ✅ Axios interceptor automatically calls `/api/auth/refresh`
- ✅ New access token received
- ✅ Original request retried and succeeds
- ✅ User stays logged in

**Check Network Tab:**
- Look for `/api/auth/refresh` call
- Original request should show twice (failed, then succeeded)

---

### ✅ Test 6: Logout Functionality

**Steps:**
1. While logged in, click "Logout" button in sidebar
2. Check localStorage
3. Try to access protected routes

**Expected Result:**
- ✅ Redirected to login page
- ✅ localStorage tokens cleared
- ❌ Cannot access protected routes
- ✅ No user info displayed

---

### ✅ Test 7: Session Persistence

**Steps:**
1. Login successfully
2. Refresh the page (F5)
3. Close browser and reopen
4. Navigate to http://localhost:5173

**Expected Result:**
- ✅ Still logged in after refresh
- ✅ Still logged in after browser restart (until tokens expire)
- ✅ User data persists

---

### ✅ Test 8: Manual Token Expiration

**Steps:**
1. Login successfully
2. Open DevTools → Application → localStorage
3. Delete `accessToken`
4. Try to navigate or make API call

**Expected Result:**
- ❌ 401 error
- ✅ Interceptor tries to refresh
- ✅ If refresh token valid → new access token
- ❌ If refresh token invalid/expired → logout

---

### ✅ Test 9: Multiple Tabs

**Steps:**
1. Login in Tab 1
2. Open Tab 2 → http://localhost:5173
3. Logout from Tab 1
4. Try to use Tab 2

**Expected Result:**
- ✅ Tab 2 should detect logout (on next API call)
- ✅ Tab 2 redirects to login

---

### ✅ Test 10: Network Errors

**Steps:**
1. Login successfully
2. Stop backend server
3. Try to make API call (save meal plan, etc.)

**Expected Result:**
- ❌ Error message displayed
- ✅ Frontend handles error gracefully
- ✅ No app crash

---

## Browser Console Checks

### Good Signs ✅
- No 401/403 errors after login
- `Authorization: Bearer <token>` in request headers (Network tab)
- Clean console (no errors)

### Bad Signs ❌
- 401/403 errors on protected endpoints
- Missing Authorization header
- Token refresh loops
- Console errors about auth

---

## Testing Checklist

**Registration & Login:**
- [ ] Can register new user
- [ ] Registration returns JWT tokens
- [ ] Can login with credentials
- [ ] Invalid credentials rejected
- [ ] Tokens stored in localStorage

**Authentication:**
- [ ] Protected routes accessible with token
- [ ] Protected routes blocked without token
- [ ] Token auto-attached to API requests

**Token Management:**
- [ ] Token refresh works automatically
- [ ] Expired access token refreshed
- [ ] Invalid refresh token triggers logout
- [ ] Logout clears all tokens

**User Experience:**
- [ ] Session persists on page refresh
- [ ] User info displayed correctly
- [ ] Logout works properly
- [ ] No UI errors or crashes

---

## Common Issues & Solutions

### Issue: "401 Unauthorized" after login
**Solution:** Check if backend is running and JWT secret is configured

### Issue: Token refresh infinite loop
**Solution:** Check if refresh token endpoint is public in SecurityConfig

### Issue: Can't access any routes
**Solution:** Verify SecurityConfig allows `/api/auth/**` as public

### Issue: localStorage not persisting
**Solution:** Check browser privacy settings (incognito blocks localStorage in some browsers)

---

## Next: Automated Frontend Tests

After manual testing, run automated tests:
```bash
npm test
```

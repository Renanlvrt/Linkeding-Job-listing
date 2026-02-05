# Supabase Dashboard Configuration

**Complete these steps in your Supabase project dashboard before testing the app:**

## 1. Authentication → URL Configuration

Navigate to: **Authentication → URL Configuration**

### Redirect URLs

Add the following URLs (one per line):

```
http://localhost:5173/auth/callback
http://localhost:5173/dashboard
```

> **Note**: When deploying to staging/production, add those URLs here too:
>
> - `https://staging.careergold.app/auth/callback`
> - `https://app.careergold.app/auth/callback`

### Site URL

Set to: `http://localhost:5173` (update per environment)

---

## 2. Authentication → Providers → Email

Navigate to: **Authentication → Providers → Email**

### Enable Email Provider

- ✅ **Enable Email Provider**: ON

### Email Configuration

- **Confirm email**:
  - OFF (for local development—faster testing)
  - ON (for production—security)
- **Secure email change**: ON

### Password Requirements

Configure strong password rules:

- Minimum length: **12 characters**
- Require:
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 number
  - At least 1 special character
- **Enable breach check**: ON (uses Have I Been Pwned)

---

## 3. Authentication → Settings

Navigate to: **Authentication → Settings**

### JWT Configuration

- **JWT expiry**: 1 hour (default—can keep as is)
- **Refresh token rotation**: Enabled (default)
- **Session timeout**: 24 hours (default)

### Rate Limiting

- **Login attempts**: 30 per hour per IP (Supabase default)
- No changes needed unless you see abuse

---

## 4. Create Test User

Navigate to: **Authentication → Users**

Click **"Add User"** → **"Create New User"**

### User Details

- **Email**: Your test email (e.g., `test@example.com`)
- **Password**: Use a strong password (at least 12 chars)
- ✅ **Auto Confirm User**: ON (skip email confirmation for testing)

Click **"Create User"**

> **Important**: If you skip "Auto Confirm User", the account will require email verification before login works.

---

## 5. Verify RLS Policies (CRITICAL)

Navigate to: **Database → Tables**

For each user-data table (`users`, `jobs`, `applications`, `saved_jobs`):

### Check Policies

1. Click table name
2. Go to **Policies** tab
3. Verify that policies exist and use `auth.uid()`

### Test RLS

1. Create 2 test users (User A and User B)
2. Use Supabase REST API or SQL editor to try:
   - User A reading User B's data → should fail
   - Unauthenticated reading protected table → should fail

> **If RLS is not set up**: Run the `backend/db_schema_hardened.sql` script in the SQL editor first.

---

## 6. Optional: Content Security Policy

For extra security on login pages, add CSP to `index.html`:

```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' https://*.supabase.co; 
               style-src 'self' 'unsafe-inline'; 
               connect-src 'self' https://*.supabase.co">
```

---

## Troubleshooting

### "Redirect URL mismatch" error

1. Check that `http://localhost:5173/auth/callback` is in **Authentication → URL Configuration**
2. Clear browser localStorage and try again
3. Check browser console for exact mismatch message

### Login fails with "Invalid credentials"

1. Verify user exists in **Authentication → Users**
2. Check that "Auto Confirm User" was enabled
3. Try password reset if unsure of password

### Token not working in backend

1. Verify `.env` has correct `SUPABASE_URL` and `SUPABASE_ANON_KEY`
2. Check backend logs for JWT validation errors
3. Ensure backend middleware is using correct JWKS/secret

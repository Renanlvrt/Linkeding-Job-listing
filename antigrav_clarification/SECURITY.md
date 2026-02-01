# CareerGold Security Implementation Guide

## Executive Summary

This document outlines the security measures implemented and recommended for CareerGold. Security is enforced at **multiple layers**: database (RLS), API (JWT validation), frontend (route protection), and infrastructure (HTTPS, secrets management).

---

## 1. Authentication Security (Supabase Auth)

### ✅ Currently Implemented
| Feature | Status | Notes |
|---------|--------|-------|
| Magic Link (passwordless) | ✅ | Eliminates password-related vulnerabilities |
| JWT-based sessions | ✅ | Handled by Supabase |
| Session persistence | ✅ | Via `onAuthStateChange` listener |

### 🔧 Required Configuration (You Must Do)

#### A. Supabase Dashboard Settings
1. **Authentication → Providers → Email**
   - ✅ Enable Email provider
   - ✅ Disable "Confirm email" for dev (enable for production)

2. **Authentication → URL Configuration**
   - **Site URL**: `http://localhost:5173` (dev) or your production URL
   - **Redirect URLs**: Add all allowed callback URLs

3. **Authentication → Security**
   - **Enable CAPTCHA** (recommended for production)
   - **Rate limiting** is on by default

4. **Project Settings → API**
   - Scroll to **JWT Expiry** → Set to `3600` (1 hour) for security

---

## 2. Row Level Security (RLS) - Database

RLS is your **primary defense**. It ensures users can only access their own data, even if the frontend or API is compromised.

### ✅ Already Configured in `db_schema.sql`

| Table | RLS Enabled | Policies |
|-------|-------------|----------|
| `users` | ✅ | Read/write own profile only |
| `jobs` | ✅ | Read: all authenticated; Write: service_role only |
| `applications` | ✅ | Read/write own applications only |
| `saved_jobs` | ✅ | Manage own saved jobs only |
| `cv_versions` | ✅ | Manage own CVs only |
| `scrape_runs` | ✅ | Write: service_role; Read: authenticated |

### 🔧 Verify RLS is Working

1. Go to **Supabase Dashboard → Table Editor**
2. Select any table → Click **RLS Policies**
3. Ensure policies are active (green toggle)

### ⚠️ Critical RLS Rules
- **Never disable RLS** on tables with user data
- **Test policies** using the Policy Simulator in Supabase Dashboard
- The `service_role` key **bypasses RLS** – never expose it client-side

---

## 3. API Key Security

### Key Types & Usage

| Key Type | Where to Use | Security Level |
|----------|--------------|----------------|
| `anon` / `publishable` | Frontend (React) | ✅ Safe - RLS protects data |
| `service_role` / `secret` | Backend only (FastAPI) | ⚠️ Never expose client-side |

### ✅ Best Practices Implemented
- Backend `.env` keeps `service_role` server-side only
- Frontend uses `anon` key (subject to RLS)
- Keys not committed to Git (`.gitignore`)

---

## 4. Frontend Security

### ✅ Implemented
| Feature | Location |
|---------|----------|
| Auth Context | `contexts/AuthContext.tsx` |
| Protected Routes | `components/auth/ProtectedRoute.tsx` |
| Automatic redirect on auth fail | LoginPage & ProtectedRoute |

### 🔧 Recommended Additions

#### A. HTTPS Only (Production)
Vercel enforces HTTPS by default. For local dev, this is not needed.

#### B. Content Security Policy (CSP)
Add to `index.html` in production:
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src fonts.gstatic.com;">
```

---

## 5. Environment Variables Security

### ✅ Current Setup
```
# Backend .env (NEVER commit)
SUPABASE_SERVICE_KEY=sb_secret_...  # Backend only
GEMINI_API_KEY=...                   # Backend only
RAPIDAPI_KEY=...                     # Backend only

# Frontend .env.local (Safe to use anon key)
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=sb_publishable_...
```

### 🔧 Production Deployment
- **Vercel**: Add env vars in Project Settings → Environment Variables
- **Railway/Render**: Add backend env vars in their dashboard
- **Never** commit `.env` files to Git

---

## 6. Data Protection Checklist

### User Data
- [x] Passwords hashed with bcrypt (Supabase handles this)
- [x] Email verified before account activation (enable in prod)
- [x] RLS prevents cross-user data access

### Job Data
- [x] Only service_role can insert jobs (scraper)
- [x] Authenticated users can read all jobs (intentional)

### Application Data
- [x] Users can only see their own applications
- [x] CV versions protected by RLS

---

## 7. Security Recommendations for Production

### High Priority
1. **Enable email confirmation** in Supabase Auth
2. **Enable CAPTCHA** for login/signup
3. **Set JWT expiry to 1 hour** max
4. **Enable MFA** for admin accounts

### Medium Priority
1. **Rotate API keys** every 90 days
2. **Monitor Supabase logs** for suspicious activity
3. **Add rate limiting** to backend scraper endpoints

---

## 8. What You Need to Do Manually

| Task | Where | Priority |
|------|-------|----------|
| Enable email confirmation | Supabase Auth Settings | High |
| Set Site URL & Redirect URLs | Supabase URL Configuration | High |
| Enable CAPTCHA | Supabase Auth Settings | Medium |
| Add production env vars | Vercel/Railway | High |
| Run `db_schema.sql` | Supabase SQL Editor | Done ✅ |

---

## Summary

CareerGold's security is built on:
1. **Supabase Auth** - Magic link authentication (no passwords to leak)
2. **RLS Policies** - Database-level access control
3. **Service Role Isolation** - Backend-only privileged operations
4. **React Auth Context** - Client-side session management

This architecture means even if the frontend code is inspected (which it always can be), attackers cannot access data they shouldn't see because RLS enforces access at the database level.

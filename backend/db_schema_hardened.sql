-- CareerGold HARDENED Database Schema
-- ======================================
-- This schema enforces maximum security at the database level.
-- Run this in the Supabase SQL Editor AFTER the initial db_schema.sql

-- ============================================================
-- STEP 1: DROP EXISTING WEAK POLICIES
-- ============================================================
-- First, drop all existing policies to replace with hardened versions

-- Users table
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;

-- Jobs table
DROP POLICY IF EXISTS "Authenticated users can view jobs" ON jobs;
DROP POLICY IF EXISTS "Service role can manage jobs" ON jobs;

-- Applications table
DROP POLICY IF EXISTS "Users can view own applications" ON applications;
DROP POLICY IF EXISTS "Users can create own applications" ON applications;
DROP POLICY IF EXISTS "Users can update own applications" ON applications;

-- Saved jobs
DROP POLICY IF EXISTS "Users can manage saved jobs" ON saved_jobs;

-- CV versions
DROP POLICY IF EXISTS "Users can manage own CVs" ON cv_versions;

-- Scrape runs
DROP POLICY IF EXISTS "Service role can manage scrape_runs" ON scrape_runs;
DROP POLICY IF EXISTS "Authenticated users can view scrape_runs" ON scrape_runs;

-- ============================================================
-- STEP 2: HELPER FUNCTION FOR EMAIL VERIFICATION CHECK
-- This function wraps auth checks for performance and reusability
-- ============================================================
CREATE OR REPLACE FUNCTION public.is_verified_user()
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if user is authenticated AND email is confirmed
    RETURN (
        auth.uid() IS NOT NULL 
        AND (
            SELECT email_confirmed_at IS NOT NULL 
            FROM auth.users 
            WHERE id = auth.uid()
        )
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = 'public', 'auth';

-- ============================================================
-- STEP 3: HARDENED USER POLICIES
-- Users can ONLY access their own data AND must be email-verified
-- ============================================================
CREATE POLICY "Users can view own profile (verified)" ON users
    FOR SELECT 
    USING (
        auth.uid() = id 
        AND public.is_verified_user()
    );

CREATE POLICY "Users can update own profile (verified)" ON users
    FOR UPDATE 
    USING (
        auth.uid() = id 
        AND public.is_verified_user()
    )
    WITH CHECK (
        auth.uid() = id 
        AND public.is_verified_user()
    );

CREATE POLICY "Users can insert own profile (verified)" ON users
    FOR INSERT 
    WITH CHECK (
        auth.uid() = id 
        AND public.is_verified_user()
    );

-- ============================================================
-- STEP 4: HARDENED JOB POLICIES
-- Only verified users can view jobs
-- Only service_role can write (scraper backend)
-- ============================================================
CREATE POLICY "Verified users can read jobs" ON jobs
    FOR SELECT 
    TO authenticated
    USING (public.is_verified_user());

CREATE POLICY "Service role manages jobs" ON jobs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- STEP 5: HARDENED APPLICATION POLICIES
-- Strict user_id checks with verified email requirement
-- ============================================================
CREATE POLICY "Users view own applications (verified)" ON applications
    FOR SELECT 
    USING (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    );

CREATE POLICY "Users create own applications (verified)" ON applications
    FOR INSERT 
    WITH CHECK (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    );

CREATE POLICY "Users update own applications (verified)" ON applications
    FOR UPDATE 
    USING (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    )
    WITH CHECK (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    );

CREATE POLICY "Users delete own applications (verified)" ON applications
    FOR DELETE 
    USING (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    );

-- ============================================================
-- STEP 6: HARDENED SAVED JOBS POLICIES
-- ============================================================
CREATE POLICY "Users manage own saved jobs (verified)" ON saved_jobs
    FOR ALL 
    USING (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    )
    WITH CHECK (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    );

-- ============================================================
-- STEP 7: HARDENED CV POLICIES
-- ============================================================
CREATE POLICY "Users manage own CVs (verified)" ON cv_versions
    FOR ALL 
    USING (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    )
    WITH CHECK (
        (SELECT auth.uid()) = user_id 
        AND public.is_verified_user()
    );

-- ============================================================
-- STEP 8: SCRAPE RUNS - SERVICE ROLE ONLY
-- Normal users cannot view scrape metadata (operational data)
-- ============================================================
CREATE POLICY "Service role manages scrape_runs" ON scrape_runs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- No SELECT for authenticated users - scrape runs are internal only

-- ============================================================
-- STEP 9: SESSION REVOCATION TABLE
-- Track when users change sensitive info to invalidate old tokens
-- ============================================================
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN ('email_change', 'password_change', 'logout_all', 'suspicious_activity')),
    revoke_before TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_security_events_user ON security_events(user_id, event_type);

-- RLS: Users can only see their own security events
ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users view own security events" ON security_events
    FOR SELECT 
    USING ((SELECT auth.uid()) = user_id);

CREATE POLICY "Service role manages security events" ON security_events
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- STEP 10: STORAGE BUCKET POLICIES (if using Supabase Storage)
-- Run these separately in Storage policies section
-- ============================================================
-- NOTE: These must be configured in Supabase Dashboard > Storage > Policies
-- 
-- For a "cvs" bucket:
-- Policy: "Users can only access own files"
-- SELECT: (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1])
-- INSERT: (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1])
-- UPDATE: (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1])
-- DELETE: (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1])

-- ============================================================
-- STEP 11: AUDIT LOG TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id UUID,
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS: Only service_role can access audit logs
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role only for audit" ON audit_log
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- No authenticated user policies = no access for regular users

-- ============================================================
-- VERIFICATION QUERIES
-- Run these to verify RLS is working correctly
-- ============================================================

-- Check all tables have RLS enabled:
-- SELECT schemaname, tablename, rowsecurity 
-- FROM pg_tables 
-- WHERE schemaname = 'public';

-- List all policies:
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
-- FROM pg_policies 
-- WHERE schemaname = 'public';

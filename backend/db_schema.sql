-- CareerGold Database Schema
-- Run this in the Supabase SQL Editor to set up the database
-- ============================================================

-- Enable UUID extension (Supabase has this enabled by default)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- USERS TABLE
-- Stores user profile and preferences
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    skills TEXT[] DEFAULT '{}',  -- Array of skill keywords
    location_pref TEXT,          -- Preferred job location
    job_title_pref TEXT,         -- Preferred job title/role
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only read/write their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- ============================================================
-- JOBS TABLE
-- Stores scraped job listings
-- ============================================================
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id TEXT,            -- LinkedIn job ID or source-specific ID
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    link TEXT,                   -- URL to job posting
    applicants INTEGER,          -- Number of applicants (if available)
    posted_at TIMESTAMPTZ,       -- When job was posted
    source TEXT DEFAULT 'linkedin',  -- linkedin, indeed, etc.
    match_score INTEGER DEFAULT 0,   -- 0-100 match percentage
    skills_matched TEXT[] DEFAULT '{}',  -- Skills that matched user profile
    status TEXT DEFAULT 'NEW' CHECK (status IN ('NEW', 'SAVED', 'APPLIED', 'REJECTED', 'EXPIRED')),
    scraped_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_match_score ON jobs(match_score DESC);
CREATE INDEX idx_jobs_scraped_at ON jobs(scraped_at DESC);
CREATE INDEX idx_jobs_external_id ON jobs(external_id);

-- Enable RLS
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- All authenticated users can read jobs
CREATE POLICY "Authenticated users can view jobs" ON jobs
    FOR SELECT TO authenticated USING (true);

-- Only service role can insert/update jobs (backend scraper)
CREATE POLICY "Service role can manage jobs" ON jobs
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- APPLICATIONS TABLE
-- Tracks user job applications
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    cv_version TEXT,             -- Which CV version was used
    status TEXT DEFAULT 'QUEUED' CHECK (status IN (
        'QUEUED',      -- Waiting to apply
        'SUBMITTING',  -- Currently submitting
        'SUBMITTED',   -- Successfully applied
        'REJECTED',    -- Application rejected
        'INTERVIEW',   -- Got interview
        'OFFER',       -- Got offer
        'MANUAL'       -- Needs manual follow-up
    )),
    applied_at TIMESTAMPTZ,      -- When application was submitted
    notes TEXT,                  -- User notes
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, job_id)      -- User can only apply once per job
);

-- Index for faster queries
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);

-- Enable RLS
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Users can only see their own applications
CREATE POLICY "Users can view own applications" ON applications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own applications" ON applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own applications" ON applications
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================================
-- SAVED_JOBS TABLE (User's saved/bookmarked jobs)
-- ============================================================
CREATE TABLE IF NOT EXISTS saved_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, job_id)
);

-- Enable RLS
ALTER TABLE saved_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage saved jobs" ON saved_jobs
    FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- SCRAPE_RUNS TABLE
-- Tracks scraping job history
-- ============================================================
CREATE TABLE IF NOT EXISTS scrape_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keywords TEXT,               -- Search keywords used
    location TEXT,               -- Location filter used
    source TEXT DEFAULT 'linkedin',
    status TEXT DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED')),
    jobs_found INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Only service role (backend) can manage scrape runs
ALTER TABLE scrape_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage scrape_runs" ON scrape_runs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Authenticated users can view scrape_runs" ON scrape_runs
    FOR SELECT TO authenticated USING (true);

-- ============================================================
-- CV_VERSIONS TABLE
-- Stores different CV versions for tailoring
-- ============================================================
CREATE TABLE IF NOT EXISTS cv_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,          -- e.g., "Base CV", "ML Focus", "Robotics Focus"
    content TEXT,                -- CV content (could be markdown or structured JSON)
    is_base BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'READY' CHECK (status IN ('DRAFTING', 'READY', 'NEEDS_REVIEW', 'ERROR')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE cv_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own CVs" ON cv_versions
    FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- UTILITY FUNCTIONS
-- ============================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_applications_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_cv_versions_updated_at
    BEFORE UPDATE ON cv_versions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- SAMPLE DATA (Optional - for testing)
-- Uncomment to insert test data
-- ============================================================

/*
INSERT INTO jobs (title, company, location, description, link, applicants, match_score, skills_matched, status) VALUES
('Software Engineer Intern', 'Tech Corp', 'San Francisco, CA (Remote)', 'Looking for a passionate intern...', 'https://linkedin.com/jobs/1', 45, 98, ARRAY['Python', 'React'], 'NEW'),
('ML Engineer', 'AI Labs', 'London, UK', 'Join our cutting-edge AI team...', 'https://linkedin.com/jobs/2', 120, 92, ARRAY['Python', 'PyTorch', 'ML'], 'NEW'),
('Robotics Developer', 'Boston Dynamics', 'Boston, MA', 'Work on next-gen robots...', 'https://linkedin.com/jobs/3', 78, 88, ARRAY['ROS2', 'C++', 'Python'], 'SAVED');
*/

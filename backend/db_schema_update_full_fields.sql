-- Database Schema Update: Full Job Data Preservation
-- ===================================================

-- 1. Add missing columns to 'jobs' table
-- We use DO blocks or separate statements to handle "IF NOT EXISTS" cleanly in Postgres

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS snippet TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS salary_range TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS job_type TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS posted_date TEXT; -- Keeping as text for "2 days ago" or raw strings
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS applicants_count INT; -- Explicit column for count
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS apply_link TEXT;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS raw_data JSONB; -- For storing the full scraped object

-- 2. Ensure RLS allows inserting these (the policies are on the TABLE, so columns are covered, 
-- but we should ensure the user has permission if we used column-level security - which we didn't).

-- 3. Update the unique constraint if needed (already done in hardened script, but safe to reiterate or skip)
-- The unique constraint is on 'external_id'.

-- 4. Grant permissions (standard service_role/authenticated checks apply from previous scripts)

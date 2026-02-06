-- Database migration for job_descriptions (CV Automation v2.1 - Polished)
-- Fixes: Initial table creation, JSONB default, pg_notify casting, and index quoting.

-- 0. Ensure table exists
CREATE TABLE IF NOT EXISTS job_descriptions (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    description text NOT NULL,
    created_by uuid REFERENCES auth.users(id) DEFAULT auth.uid(),
    created_at timestamp with time zone DEFAULT now()
);

-- 1. Ensure core columns exist
ALTER TABLE job_descriptions 
ADD COLUMN IF NOT EXISTS company text,
ADD COLUMN IF NOT EXISTS tailored_cv text,
ADD COLUMN IF NOT EXISTS pdf_url text,
ADD COLUMN IF NOT EXISTS status text DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS ats_score smallint DEFAULT 0,
ADD COLUMN IF NOT EXISTS keyword_match_json jsonb DEFAULT '[]'::jsonb, -- Fixed: added brackets
ADD COLUMN IF NOT EXISTS retry_count smallint DEFAULT 0,
ADD COLUMN IF NOT EXISTS error_log text,
ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone DEFAULT now();

-- 2. Scalability: Targeted Indexes (Fixed Quoting)
CREATE INDEX IF NOT EXISTS idx_jds_status_retry ON job_descriptions(status, retry_count) 
WHERE status IN ('pending', 'retry');

CREATE INDEX IF NOT EXISTS idx_jds_updated_at ON job_descriptions(updated_at DESC);

-- 3. Automatic updated_at Trigger
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_update_jds_timestamp ON job_descriptions;
CREATE TRIGGER tr_update_jds_timestamp
BEFORE UPDATE ON job_descriptions
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- 4. Real-time Notification Casting Fix
CREATE OR REPLACE FUNCTION notify_cv_ready()
RETURNS TRIGGER AS $$
BEGIN
    -- Only notify on transition to 'completed'
    IF NEW.status = 'completed' AND (OLD.status IS NULL OR OLD.status != 'completed') THEN
        PERFORM pg_notify('cv-ready', (json_build_object(
            'id', NEW.id, 
            'company', COALESCE(NEW.company, 'Unknown'), 
            'ats_score', NEW.ats_score,
            'pdf_url', NEW.pdf_url
        ))::text); -- Fixed: Added parens for casting
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tr_notify_cv_ready ON job_descriptions;
CREATE TRIGGER tr_notify_cv_ready
AFTER UPDATE ON job_descriptions
FOR EACH ROW
EXECUTE FUNCTION notify_cv_ready();

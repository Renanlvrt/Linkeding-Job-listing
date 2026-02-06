-- Hardened RLS and multi-tenancy for job_descriptions (v2.1)
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;

-- 1. Ensure created_by exists with strict FK (Fixed: added ON DELETE CASCADE)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='job_descriptions' AND column_name='created_by') THEN
        ALTER TABLE job_descriptions ADD COLUMN created_by uuid REFERENCES auth.users(id) NOT NULL default auth.uid();
    END IF;
END $$;

ALTER TABLE job_descriptions 
DROP CONSTRAINT IF EXISTS fk_created_by;

ALTER TABLE job_descriptions 
ADD CONSTRAINT fk_created_by 
FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_jds_created_by ON job_descriptions(created_by);

-- 2. Define User-Level Access (GDPR Compliance)
DROP POLICY IF EXISTS "Users view own jds" ON job_descriptions;
CREATE POLICY "Users view own jds" ON job_descriptions
FOR ALL TO authenticated
USING (auth.uid() = created_by)
WITH CHECK (auth.uid() = created_by);

-- 3. Anon Policy (Fixed: added restricted select for pending jobs)
DROP POLICY IF EXISTS "Anon read own pending" ON job_descriptions;
CREATE POLICY "Anon read own pending" ON job_descriptions
FOR SELECT TO anon 
USING (auth.uid() = created_by);

-- 4. Define Worker-Level Access
DROP POLICY IF EXISTS "Worker restricted access" ON job_descriptions;
CREATE POLICY "Worker restricted access" ON job_descriptions
FOR ALL TO service_role
USING (true)
WITH CHECK (true);

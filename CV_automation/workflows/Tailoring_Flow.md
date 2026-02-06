# Workflow: Tailoring Flow (Chained Implementation)

## Step 1: Realtime Subscription / Polling

- **Action**: `cv_worker.py` listens for `INSERT` or `UPDATE` on `job_descriptions` where `status='pending'`.
- **Logic**: Use `supabase.realtime` with a fallback 30s poll.

## Step 2: JD Extraction (Prompt Chain 1)

- **Input**: `jd_description`
- **Goal**: Extract critical hard/soft skills and seniority.
- **Output (YAML)**:

  ```yaml
  seniority: "Junior/Mid/Senior"
  top_hard_skills: ["Python", "PyTorch"]
  top_soft_skills: ["Leadership"]
  keywords: ["ATS", "BCI"]
  ```

## Step 3: CV Mapping & Drafting (Prompt Chain 2)

- **Input**: `Extracted_JD_YAML` + `master_CV.md`
- **Goal**: Draft the tailored CV Sections 1-4.
- **Rules**: UK spelling ("optimise"), Version B Balanced, no fabrication.

## Step 4: Validation & Quality Gate

- **Action**: Run `Validation Engine` (6-point scorer).
- **Branch**:
  - **Score >= 85**: Proceed to PDF.
  - **Score < 85**: Log failure, increment `retry_count`, set `status='retry'`.

## Step 5: PDF Generation (WeasyPrint)

- **Action**: Convert `Section 4` markdown to a clean, single-column PDF using Calibri style.
- **Storage**: Upload to Supabase Storage, update record with `pdf_url`.

## Step 6: User Notification

- **Action**: Broadcast `cv-ready` event via Supabase Realtime for the Streamlit dashboard.

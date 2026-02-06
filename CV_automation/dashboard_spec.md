# Streamlit Review Dashboard Specification (v2.1)

## Purpose

A "Human-in-the-loop" interface for auditing tailored CVs, especially those with scores in the 70-85% "Ambiguous" range.

## Security & Authentication

- **Supabase Auth Integration**:
  - Use `streamlit-supabase-auth` or a custom login flow.
  - **Filter**: All queries MUST filter by `auth.current_user.id == created_by`.
  - Prevent unauthorised access to PDFs/CVs by enforcing Supabase session tokens in the dashboard.

## Layout

- **Sidebar**:
  - Filter by Status: `pending`, `retry`, `completed`, `failed`.
  - Real-time Metrics: Total processed, Avg ATS Score, Failure Rate.
- **Main View**:
  - **Top Stats**: Selected Job Company, Seniority Level, and Overall Quality Score.
  - **Comparison Panes**:
    - Left: Job Description (Original).
    - Right: Tailored CV (Markdown Preview).
  - **Scorer Breakdown**: Expandable section showing points for each of the 6 metrics (inc. UK spelling & Seniority).
- **Actions**:
  - `Approve & Generate PDF`: Finalize the job.
  - `Regenerate`: Trigger a new worker loop with a custom prompt hint.
  - `Edit Manually`: Open a markdown editor for quick fixes.
- **PDF Preview**: Embedded PDF view of the WeasyPrint output.

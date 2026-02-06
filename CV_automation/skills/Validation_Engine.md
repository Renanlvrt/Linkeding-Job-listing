# Skill: Validation Engine (Hardened Scorer v2.1)

## Goal

Quantifiably evaluate and enforce production-grade quality for every generated CV.

## Validation Metrics (Pass >= 85%)

1. **Header Compliance (10 pts)**: PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE, EDUCATION present.
2. **ATS Cleanliness (15 pts)**: No `|`, `![]`, `<table`, or multiple columns.
3. **Keyword Density (20 pts)**: Target >= 80% coverage of Top 10 JD keywords.
4. **Semantic Integrity (25 pts)**: `difflib.SequenceMatcher` ratio against `master_CV.md` MUST be >= 0.75.
    - *Critical*: Any fabrication of employer/dates = 0 pts total.
5. **UK Spelling Check (10 pts)**:
    - Regex pattern match for '-ize', '-yze', 'color', 'program', 'center'.
    - Deduct 2 pts per occurrence.
6. **Seniority & Bullets (20 pts)**:
    - Min 4 bullets per experience.
    - Seniority Verb Check: Junior (e.g. 'developed', 'assisted') vs Senior (e.g. 'architected', 'strategised').
    - Penalty: -15 pts for seniority mismatch (e.g. using Junior verbs for a Lead role).

## Pre-Processing (PII Masking)

- **Action**: Before sending `master_CV.md` to the LLM, use a Pydantic model/regex to hash or placeholder PII (Phone, Email, Specific House Number).
- **Goal**: GDPR compliance and leak prevention.

## Scoring Logic

- **Score 0**: Critical failure (Hallucinations or Difflib < 0.6).
- **Score < 75**: Mark as `status='retry'`, log specific issues, increment `retry_count`.
- **Score >= 85**: Pass to PDF generation.

## Retry Mechanism

- Use **Exponential Backoff** (delay = 2^retry_count * 10 seconds).
- Max retries = 3.

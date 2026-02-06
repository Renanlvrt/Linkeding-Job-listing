# Skill: LLM Prompting for CV Tailoring

## Goal

Drive the LLM (Llama 3.1:8b) to produce high-fidelity, factually accurate, and contextually relevant CV content without fabrication.

## Configuration

- **Ollama Settings**:
  - `num_ctx`: 16384 (ensures full CV + JD + reasoning fits).
  - `temperature`: 0.1 (low for high factual consistency).
- **Core Prompting Techniques**:
  - **Few-Shot Prompting**: Provide clear "Before" and "After" bullet examples.
  - **Step-by-Step Reasoning**: Ask the LLM to analyze the JD, map it to the CV, and identify gaps *before* rewriting.
  - **Strict Negative Constraints**: Explicitly forbid inventing employers, dates, or specific metrics not in the master CV.

## Versioning

- **Version A (Conservative)**: Minimal changes, high fidelity to master text.
- **Version B (Balanced)**: Moderate rephrasing for impact, aligning with JD keywords.
- **Version C (Creative)**: More aggressive rewriting for impact, while maintaining factual integrity (no role/date changes).

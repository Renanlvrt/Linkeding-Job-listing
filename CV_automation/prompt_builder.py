import yaml
import re
from typing import Dict, Any
from models import JDExtraction, CVMapping

class PromptBuilder:
    """
    Constructs multi-stage prompts for the CV tailoring pipeline.
    Enforces the Sprout framework and UK spelling.
    """
    
    @staticmethod
    def build_extraction_prompt(job_description: str) -> str:
        """
        Creates a strict prompt to extract technical keywords AND context from a JD.
        """
        return f"""
You are an expert ATS parser. Extract key details from the Job Description below.

RULES:
1. OUTPUT PURE YAML ONLY. No markdown blocks, no chatter.
2. BE PRECISE. Extract exact phrases.

SCHEMA:
seniority: "Junior / Mid / Senior / Lead"
keywords:
  - "exact technical keyword 1"
  - "exact technical keyword 2"
top_hard_skills:
  - "Skill A"
  - "Skill B"
top_soft_skills:
  - "Trait A"
  - "Trait B"
major_responsibilities:
  - "Responsibility 1"
  - "Responsibility 2"

JOB DESCRIPTION:
{job_description}

OUTPUT YAML:
"""

    @staticmethod
    def build_mapping_prompt(jd_extraction: JDExtraction, master_cv: str) -> str:
        """
        Step 2: Mapping Agent (The "Strategist").
        Identifies which parts of the Master CV prove required skills.
        """
        keywords_str = "\n- ".join(jd_extraction.keywords)
        return f"""
You are an expert Career Strategist. Analyze the Master CV against the target Job Description (JD) keywords.

JD KEYWORDS:
- {keywords_str}

RULES:
1. OUTPUT PURE YAML ONLY. No chatter.
2. MAPPED_SKILLS: For each JD keyword, find the EXACT bullet point or phrase from the Master CV that proves it.
3. MISSING_SKILLS: List keywords that the candidate has NO evidence for.
4. SUGGESTED_PHRASINGS: Identify terms in the Master CV that should be renamed to match the JD (e.g., "Developer" -> "Engineer").

SCHEMA:
mapped_skills:
  "keyword1": "snippet from master cv"
missing_skills:
  - "missing keyword 1"
suggested_phrasings:
  "old term": "new jd term"

MASTER CV:
{master_cv}

OUTPUT YAML:
"""

    @staticmethod
    def build_tailoring_prompt(jd_extraction: JDExtraction, mapping: CVMapping, master_cv: str) -> str:
        """
        Step 3: Writing Agent (The "Resume Builder").
        Drafts the final CV using mapped context.
        """
        keywords_str = "\n- ".join(jd_extraction.keywords)
        phrasings_str = "\n".join([f"- Change '{old}' to '{new}'" for old, new in mapping.suggested_phrasings.items()])
        
        return f"""
You are a professional CV Editor. Rewrite the candidate's CV using the provided Mapping Strategy.

TARGET KEYWORDS:
- {keywords_str}

MAPPING STRATEGY (Proven Experience):
{mapping.mapped_skills}

TERMINOLOGY CHANGES:
{phrasings_str}

STRICT CONSTRAINTS:
1. OUTPUT FORMAT: Markdown only. No preambles. No "Sure, here is...".
2. STAR METHOD: Ensure all experience bullets follow the STAR framework (Situation, Task, Action, Result).
3. AT LEAST 80% COVERAGE: Mention at least 80% of the target keywords naturally.
4. DO NOT HALLUCINATE: Only use facts from the Master CV. Rephrase, but don't invent.

ORIGINAL CV:
{master_cv}

FINAL TAILORED CV (MARKDOWN):
"""

    @staticmethod
    def post_process_spelling(text: str) -> str:
        """
        Enforce UK spelling via regex as a safety net.
        """
        mapping = {
            r"\boptimize": "optimise",
            r"\banalyze": "analyse",
            r"\bprogram\b": "programme",
            r"\bcenter\b": "centre",
            r"\bmodeling": "modelling",
            r"\bcatalog\b": "catalogue",
            r"\bcolor": "colour"
        }
        processed = text
        for us, uk in mapping.items():
            processed = re.sub(us, uk, processed, flags=re.IGNORECASE)
        return processed

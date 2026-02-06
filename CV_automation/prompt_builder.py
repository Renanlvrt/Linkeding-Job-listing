import yaml
import re
from typing import Dict, Any
from models import JDExtraction

class PromptBuilder:
    """
    Constructs multi-stage prompts for the CV tailoring pipeline.
    Enforces the Sprout framework and UK spelling.
    """
    
    @staticmethod
    def build_extraction_prompt(jd_text: str) -> str:
        """
        Stage 1: Extract requirements from the Job Description.
        """
        return f"""
Analyze the following Job Description (JD) and extract the critical requirements into a YAML format.

JD TEXT:
\"\"\"
{jd_text}
\"\"\"

OUTPUT RULES:
1. Output ONLY valid YAML.
2. Seniority must be one of: Junior, Mid, Senior, Lead.
3. Extract Top 10 hard skills.
4. Extract Top 5 soft skills.
5. Identify critical ATS keywords (acronyms + unique terms).

YAML SCHEMA:
seniority: string
top_hard_skills: [string, ...]
top_soft_skills: [string, ...]
keywords: [string, ...]
major_responsibilities: [string, ...]
"""

    @staticmethod
    def build_tailoring_prompt(jd_extraction: JDExtraction, master_cv: str) -> str:
        """
        Stage 2: Draft the tailored CV based on extracted JD data and master CV.
        """
        return f"""
Using the provided JD ANALYSIS and the MASTER CV, draft a tailored, ATS-compliant CV.

---
JD ANALYSIS (YAML):
{jd_extraction.model_dump()}

---
MASTER CV (REDACTED):
{master_cv}

---
CRITICAL OUTPUT RULES:
1. OUTPUT THE CV CONTENT ONLY. 
2. DO NOT INCLUDE ANY PREAMBLE, INTRODUCTION, OR CONVERSATIONAL TEXT (e.g., "Based on...", "Here is...", "I have...").
3. DO NOT INCLUDE MARKDOWN TAGS LIKE ```markdown OR ```. START DIRECTLY WITH THE NAME.
4. APPLY SPROUT 5-PILLAR FRAMEWORK: British English, ATS Compliance, STAR Method, Keyword Mapping, No Graphics.
5. SENIORITY FOCUS: {jd_extraction.seniority}.
6. END YOUR RESPONSE WITH THE TAG '## END'.

CV OUTPUT:
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

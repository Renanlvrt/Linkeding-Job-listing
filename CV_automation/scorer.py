import re
import difflib
from typing import List, Dict
from models import CVScore, JDExtraction

class CVScorer:
    """
    Production-grade validation engine for tailored CVs.
    Enforces structural, semantic, and linguistic constraints.
    """
    
    def __init__(self, master_cv_clean: str):
        self.master_cv_clean = master_cv_clean
        self.uk_spelling_mistakes = [
            r"\boptimize", r"\banalyze", r"\bcolor\b", r"\bprogram\b", r"\bcenter\b"
        ]
        self.uk_spelling_us = re.compile(r'\b(color|optimize|realize|programme|analysed)\b', re.I)
        self.senior_verbs = ["strategised", "led", "architected", "transformed", "mentored"]
        self.junior_verbs = ["implemented", "developed", "executed", "assisted"]

    @staticmethod
    def normalize_text(text: str) -> set:
        """Converts text to unique lowercase alphanumeric tokens."""
        if not text:
            return set()
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return set(text.split())

    def calculate_score(self, tailored_cv: str, jd_extraction: JDExtraction) -> CVScore:
        """
        Robust validation engine. 
        Compatible with previous signature but uses the new quality metrics.
        """
        metrics = {}
        suggestions = []
        
        # 1. Formatting (Check for Markdown tables which are bad for ATS)
        # Look for | col | col | syntax
        has_tables = bool(re.search(r'\|.*\|.*\|', tailored_cv))
        metrics["ats_format"] = 0 if has_tables else 20
        if has_tables:
            suggestions.append("Detected Markdown table syntax (non-ATS compliant).")

        # 2. Structural Checks (Headers)
        headers = ["PROFESSIONAL SUMMARY", "EXPERIENCE", "SKILLS", "EDUCATION"]
        header_points = sum(5 for h in headers if h in tailored_cv.upper())
        # Normalized to 20 max
        metrics["headers"] = min(20, header_points)
        if metrics["headers"] < 20:
             suggestions.append("Missing or misnamed core section headers.")

        # 3. Integrity (Primary Gate - Length Ratio)
        # Passes if tailored CV retains at least 30% of Master CV's length (summary is OK).
        len_master = len(self.master_cv_clean)
        len_tailored = len(tailored_cv)
        integrity_ratio = (len_tailored / len_master) * 100 if len_master > 0 else 0
        
        # We target a score out of 20
        # If integrity is > 30%, they get full points for this metric (20)
        metrics["integrity_ratio"] = 20 if integrity_ratio >= 30 else (integrity_ratio / 30) * 20
        if integrity_ratio < 30:
            suggestions.append(f"CV Integrity check low ({int(integrity_ratio)}%). Tailored CV is too short.")

        # 4. Keywords (40 pts)
        # USES TOKEN SET INTERSECTION (Robust against paraphrasing)
        target_kws = set(jd_extraction.keywords)
        if hasattr(jd_extraction, 'top_hard_skills') and jd_extraction.top_hard_skills:
            target_kws.update(jd_extraction.top_hard_skills)
            
        cv_tokens = self.normalize_text(tailored_cv)
        matches = []
        missing = []

        if not target_kws:
            kw_score = 40.0
        else:
            for kw in target_kws:
                kw_tokens = self.normalize_text(kw)
                if not kw_tokens: continue
                # Match if at least 50% of the keyword's tokens exist in CV
                intersection = kw_tokens.intersection(cv_tokens)
                if len(intersection) / len(kw_tokens) >= 0.5:
                    matches.append(kw)
                else:
                    missing.append(kw)
            kw_score = (len(matches) / len(target_kws)) * 40

        metrics["keyword_coverage"] = round(kw_score, 2)
        if (kw_score / 40) < 0.7:
             suggestions.append(f"Low keyword density. Missing: {missing[:5]}")

        # Final aggregation
        total = sum(metrics.values())
        
        # Hallucination check based on extreme brevity or low keyword overlap
        hallucination = False
        if integrity_ratio < 15 or (kw_score / 40) < 0.1:
            hallucination = True
            
        return CVScore(
            total_score=total,
            metrics=metrics,
            hallucination_detected=hallucination,
            suggestions=suggestions,
            tailored_cv=tailored_cv
        )

        # 5. UK Spelling Check (10 pts)
        us_matches = len(self.uk_spelling_us.findall(tailored_cv))
        uk_penalty = min(10, us_matches * 2)
        metrics['uk_spelling'] = max(0, 10 - uk_penalty)
        if us_matches > 0:
            suggestions.append(f"US spelling detected ({us_matches} instances).")

        # 6. Seniority & Bullets (20 pts)
        bullet_count = len(re.findall(r"^\s*[-◦•]", tailored_cv, re.MULTILINE))
        bullet_score = min(10, (bullet_count / 10) * 10) # Target 10+ bullets total
        
        # Seniority match
        verb_score = 10.0
        if jd_extraction.seniority in ['Senior', 'Lead']:
            senior_ratio = sum(1 for v in self.senior_verbs if v.lower() in tailored_cv.lower()) / max(1, len(self.senior_verbs))
            verb_score = min(10, senior_ratio * 10)
            if senior_ratio < 0.3:
                suggestions.append("Language level too low for Senior/Lead role.")
        
        metrics["seniority_verbs"] = max(0, bullet_score + verb_score)

        # Final aggregation
        total = sum(metrics.values())
        
        # Final aggregation
        total = sum(metrics.values())
        
        return CVScore(
            total_score=total,
            metrics=metrics,
            hallucination_detected=hallucination,
            suggestions=suggestions,
            tailored_cv=tailored_cv
        )

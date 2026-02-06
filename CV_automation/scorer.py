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

    def calculate_score(self, tailored_cv: str, jd_extraction: JDExtraction) -> CVScore:
        score = 100.0
        metrics = {}
        suggestions = []
        hallucination = False
        
        # 1. Header Compliance (10 pts)
        headers = ["PROFESSIONAL SUMMARY", "SKILLS", "EXPERIENCE", "EDUCATION"]
        header_points = sum(5 for h in headers if h in tailored_cv.upper())
        # Normalized to 10 max
        header_score = (header_points / 20) * 10
        metrics["headers"] = header_score
        if header_score < 10:
            suggestions.append("Missing or misnamed core section headers.")

        # 2. ATS Cleanliness (15 pts)
        prohibited = [r"\|", r"!\[\]", r"<table", r"\{col\}"]
        cleanliness_penalty = 0
        for p in prohibited:
            if re.search(p, tailored_cv):
                cleanliness_penalty += 5
        metrics["ats_format"] = max(0, 15 - cleanliness_penalty)
        if cleanliness_penalty > 0:
            suggestions.append("Detected non-ATS-compliant formatting (tables/images).")

        # 3. Keyword Density (20 pts)
        kw_found = sum(1 for kw in jd_extraction.keywords if kw.lower() in tailored_cv.lower())
        kw_ratio = kw_found / max(1, len(jd_extraction.keywords))
        metrics["keyword_coverage"] = min(20, kw_ratio * 20)
        if kw_ratio < 0.8:
            suggestions.append(f"Low keyword density ({int(kw_ratio*100)}%). Target is 80%.")

        # 4. Semantic Integrity / Hallucination Check (25 pts)
        # Improved: We calculate how much of the tailored CV is "grounded" in the master CV.
        # This prevents the 6% ratio issue where a short tailored CV is compared to a long master.
        master_words = set(re.findall(r'\w+', self.master_cv_clean.lower()))
        tailored_words = set(re.findall(r'\w+', tailored_cv.lower()))
        
        # Intersection - what percentage of tailored words exist in master?
        # We exclude common stop words or tiny words for better signal
        ignored = {'the', 'and', 'with', 'for', 'from', 'that', 'this', 'your', 'was', 'were'}
        t_words_filtered = {w for w in tailored_words if len(w) > 3 and w not in ignored}
        
        if not t_words_filtered:
            ratio = 1.0
        else:
            overlap = t_words_filtered.intersection(master_words)
            # Add JD keywords to the "allowed" set
            jd_kws = {kw.lower() for kw in jd_extraction.keywords}
            overlap.update(t_words_filtered.intersection(jd_kws))
            
            ratio = len(overlap) / len(t_words_filtered)

        metrics["integrity_ratio"] = min(25, ratio * 25)
        if ratio < 0.60:
            suggestions.append(f"Low semantic integrity ({int(ratio*100)}%). Grounding check failed.")
        if ratio < 0.35:
            hallucination = True

        # 5. UK Spelling Check (10 pts)
        us_matches = len(self.uk_spelling_us.findall(tailored_cv))
        uk_penalty = min(10, us_matches * 2)
        metrics['uk_spelling'] = max(0, 10 - uk_penalty)
        if us_matches > 0:
            suggestions.append(f"US spelling detected ({us_matches} instances). Use 'colour/optimise'.")

        # 6. Seniority & Bullets (20 pts)
        bullet_count = len(re.findall(r"^\s*[-◦•]", tailored_cv, re.MULTILINE))
        bullet_score = min(10, (bullet_count / 12) * 10) # Target 12+ bullets total
        
        # Seniority match: Weight by JD extraction
        verb_score = 10.0
        if jd_extraction.seniority in ['Senior', 'Lead']:
            senior_ratio = sum(1 for v in self.senior_verbs if v.lower() in tailored_cv.lower()) / max(1, len(self.senior_verbs))
            verb_score = min(10, senior_ratio * 10)
            if senior_ratio < 0.4:
                suggestions.append("Language level too low for Senior/Lead role (low seniority verb density).")
        
        metrics["seniority_verbs"] = max(0, bullet_score + verb_score)

        # Final aggregation
        total = sum(metrics.values())
        
        return CVScore(
            total_score=total,
            metrics=metrics,
            hallucination_detected=hallucination,
            suggestions=suggestions,
            tailored_cv=tailored_cv
        )

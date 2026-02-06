from pydantic import BaseModel, Field
from typing import List, Optional

class JDExtraction(BaseModel):
    seniority: str = Field(description="One of: Junior, Mid, Senior, Lead")
    top_hard_skills: List[str] = Field(description="Top 10 hard skills required")
    top_soft_skills: List[str] = Field(description="Top 5 soft skills or traits")
    keywords: List[str] = Field(description="Critical ATS keywords (acronyms + terms)")
    major_responsibilities: List[str] = Field(description="Core duties to map against CV")

class CVScore(BaseModel):
    total_score: float = Field(ge=0, le=100)
    metrics: dict = Field(default_factory=lambda: {
        "headers": 0,
        "ats_format": 0,
        "keyword_coverage": 0,
        "integrity_ratio": 0,
        "uk_spelling": 0,
        "seniority_verbs": 0
    })
    hallucination_detected: bool
    suggestions: List[str]
    tailored_cv: Optional[str] = None

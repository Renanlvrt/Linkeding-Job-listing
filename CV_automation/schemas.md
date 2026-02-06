# CV Automation Logic Schemas (v2.1)

## 1. JD Extraction (Chain 1 Output)

The LLM must output YAML matching this Pydantic schema:

```python
from pydantic import BaseModel, Field
from typing import List

class JDExtraction(BaseModel):
    seniority: str = Field(description="One of: Junior, Mid, Senior, Lead")
    top_hard_skills: List[str] = Field(description="Top 10 hard skills required")
    top_soft_skills: List[str] = Field(description="Top 5 soft skills or traits")
    keywords: List[str] = Field(description="Critical ATS keywords (acronyms + terms)")
    major_responsibilities: List[str] = Field(description="Core duties to map against CV")
```

### Chain 1 Execution Parameters

- **Timeout**: Strictly 30 seconds.
- **Fallback**: If Chain 1 fails (timeout or unparsable YAML), use a "Conservative Catch-all" prompt for Chain 2 with generic tech keywords and 'Mid' seniority default to avoid total job failure.

## 2. CV Drafting (Chain 2 Input/Output)

- **Input**: `JDExtraction` + `MasterCV`
- **Output**: Markdown formatted string following the Sprout 5-pillar structure.
- **Post-Process**: Run `sed`-style regex to enforce 'optimise', 'analysed', etc., if the LLM slips.

## 3. Scorer Schema (Validation Engine)

```python
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
```

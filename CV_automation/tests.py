import pytest
import re
import json
from unittest.mock import MagicMock, patch
from secure_cv_loader import SecureCVLoader
from prompt_builder import PromptBuilder
from scorer import CVScorer
from models import JDExtraction, CVScore

# Fixtures
@pytest.fixture
def master_cv():
    return """
# Renan Lavirotte
renan.lavirotte@gmail.com | 07729 446958
## EXPERIENCE
### IBM Project | AI Engineer
- Architected an AI bot in VR environment.
- Optimized user engagement by 20%.
## EDUCATION
### Durham University | MEng Computer Science
## SKILLS
- Python, C, Machine Learning.
    """

@pytest.fixture
def jd_extraction():
    return JDExtraction(
        seniority="Mid",
        top_hard_skills=["Python", "AI"],
        top_soft_skills=["Leadership"],
        keywords=["AI", "IBM", "Python"],
        major_responsibilities=["Develop AI bots"]
    )

# 1. Test Security Loader (PII Sanitization)
def test_cv_loader_sanitization(tmp_path, master_cv):
    cv_file = tmp_path / "master_CV.md"
    cv_file.write_text(master_cv)
    
    loader = SecureCVLoader(str(cv_file))
    sanitized = loader.load_and_sanitize()
    
    assert "[REDACTED_EMAIL]" in sanitized
    assert "renan.lavirotte@gmail.com" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized

# 2. Test Prompt Builder (UK Spelling)
def test_prompt_builder_spelling_fix():
    us_text = "I optimized the program at the center."
    fixed = PromptBuilder.post_process_spelling(us_text)
    assert "optimised" in fixed
    assert "programme" in fixed
    assert "centre" in fixed

# 3. Test Scorer (Logic & Thresholds)
def test_scorer_metrics(master_cv, jd_extraction):
    scorer = CVScorer(master_cv)
    
    # Mock a high-quality tailored CV that closely matches the master structure
    good_cv = """
# RENAN LAVIROTTE
[REDACTED_EMAIL] | [REDACTED_PHONE]

PROFESSIONAL SUMMARY
Experienced AI Engineer with a background in Computer Science from Durham University.

SKILLS
- Python, C, Machine Learning, AI.

EXPERIENCE
### IBM Project | AI Engineer
- Architected an AI bot in VR environment.
- Optimized user engagement by 20%.
- Developed new features in Python.
- Mentored junior engineers.

EDUCATION
### Durham University | MEng Computer Science
    """
    
    result = scorer.calculate_score(good_cv, jd_extraction)
    assert result.total_score > 60
    assert result.metrics["keyword_coverage"] > 0
    assert result.hallucination_detected == False

def test_scorer_hallucination_detection(master_cv, jd_extraction):
    scorer = CVScorer(master_cv)
    # Totally different content
    bad_cv = "I am a space chef at NASA and I cooked 5000 pizzas in 1990."
    result = scorer.calculate_score(bad_cv, jd_extraction)
    # Should flag low integrity
    assert result.metrics["integrity_ratio"] < 10
    assert result.total_score < 40

# 4. Test Seniority Verb Check
def test_seniority_verb_logic(master_cv):
    scorer = CVScorer(master_cv)
    jd_sr = JDExtraction(
        seniority="Senior", 
        top_hard_skills=[], top_soft_skills=[], keywords=[], major_responsibilities=[]
    )
    
    # Senior role with junior verbs
    cv_jr = "### Role\n- developed the app\n- assisted the team\n"
    result = scorer.calculate_score(cv_jr, jd_sr)
    # Check for penalty in suggestions
    assert any("Senior/Lead" in s for s in result.suggestions)

if __name__ == "__main__":
    pytest.main([__file__])

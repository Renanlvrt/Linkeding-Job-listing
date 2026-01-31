"""
Gemini AI Job Parser
=====================
Uses Gemini Flash to parse and enrich job descriptions.

Extracts:
- Required skills
- Experience level
- Key responsibilities
- Match score against user profile
"""

import google.generativeai as genai
from typing import Optional
import json
import re

from app.config import settings


class GeminiParser:
    """Parse job descriptions using Gemini AI."""
    
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            # Use Flash model - fastest and cheapest
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    async def parse_job_description(self, job_text: str) -> dict:
        """
        Parse a job description and extract structured data.
        
        Args:
            job_text: Raw job description text
        
        Returns:
            Structured job data with skills, requirements, etc.
        """
        if not self.model:
            return {"error": "Gemini API key not configured"}
        
        prompt = f"""Analyze this job description and extract the following in JSON format:
{{
    "required_skills": ["list", "of", "skills"],
    "nice_to_have_skills": ["optional", "skills"],
    "experience_years": "e.g., 2-3 years or entry-level",
    "education": "degree requirements if any",
    "job_type": "full-time/part-time/contract/internship",
    "remote_status": "remote/hybrid/onsite",
    "key_responsibilities": ["top 3-5 responsibilities"],
    "company_info": "brief company description if mentioned",
    "salary_range": "if mentioned, else null"
}}

Job Description:
{job_text[:4000]}

Return ONLY valid JSON, no markdown or explanation."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if text.startswith("```"):
                text = re.sub(r'^```\w*\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            
            return json.loads(text)
            
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {e}", "raw": text}
        except Exception as e:
            return {"error": str(e)}
    
    async def calculate_match_score(
        self,
        job_skills: list[str],
        user_skills: list[str],
    ) -> dict:
        """
        Calculate how well a job matches user skills.
        
        Args:
            job_skills: Skills required by the job
            user_skills: User's skills from their profile
        
        Returns:
            Match score and details
        """
        if not job_skills or not user_skills:
            return {
                "score": 0,
                "matched_skills": [],
                "missing_skills": job_skills or [],
            }
        
        # Normalize skills for comparison
        job_skills_lower = {s.lower().strip() for s in job_skills}
        user_skills_lower = {s.lower().strip() for s in user_skills}
        
        # Find matches
        matched = job_skills_lower.intersection(user_skills_lower)
        missing = job_skills_lower - user_skills_lower
        
        # Calculate score
        score = int((len(matched) / len(job_skills_lower)) * 100) if job_skills_lower else 0
        
        return {
            "score": score,
            "matched_skills": list(matched),
            "missing_skills": list(missing),
            "match_ratio": f"{len(matched)}/{len(job_skills_lower)}",
        }
    
    async def enrich_job(
        self,
        job: dict,
        user_skills: list[str],
    ) -> dict:
        """
        Fully enrich a job with parsed data and match score.
        
        Args:
            job: Job dict with at least 'description' or 'snippet'
            user_skills: User's skills list
        
        Returns:
            Enriched job with parsed data and match score
        """
        description = job.get("description") or job.get("snippet", "")
        
        if not description:
            return {
                **job,
                "parsed": None,
                "match_score": 0,
                "skills_matched": [],
            }
        
        # Parse the description
        parsed = await self.parse_job_description(description)
        
        if "error" in parsed:
            return {
                **job,
                "parsed": parsed,
                "match_score": 0,
                "skills_matched": [],
            }
        
        # Calculate match score
        job_skills = parsed.get("required_skills", [])
        match_result = await self.calculate_match_score(job_skills, user_skills)
        
        return {
            **job,
            "parsed": parsed,
            "match_score": match_result["score"],
            "skills_matched": match_result["matched_skills"],
            "skills_missing": match_result["missing_skills"],
        }


# Singleton instance
gemini_parser = GeminiParser()

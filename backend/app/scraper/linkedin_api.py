"""
LinkedIn Jobs API Client (RapidAPI)
====================================
Rate-limited client for fetching LinkedIn job listings.

Free tier limits:
- 100 requests/month (HARD LIMIT)
- 1000 requests/hour

Use sparingly! Prefer DuckDuckGo discovery for initial searches.
"""

import httpx
from typing import Optional
from datetime import datetime
import json

from app.config import settings


class LinkedInAPIClient:
    """Client for LinkedIn Jobs Search API on RapidAPI."""
    
    BASE_URL = "https://linkedin-jobs-search.p.rapidapi.com"
    
    def __init__(self):
        self.api_key = settings.rapidapi_key
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "linkedin-jobs-search.p.rapidapi.com",
            "Content-Type": "application/json",
        }
        self._request_count = 0
        self._monthly_limit = 100  # Free tier limit
    
    @property
    def requests_remaining(self) -> int:
        """Estimate of remaining requests this month."""
        return max(0, self._monthly_limit - self._request_count)
    
    async def search_jobs(
        self,
        keywords: str,
        location: str = "Remote",
        posted_within_days: int = 7,
        max_applicants: int = 100,
        date_posted: str = None,  # DEPRECATED: use posted_within_days
        job_type: Optional[str] = None,  # full-time, part-time, contract
        experience_level: Optional[str] = None,  # entry, associate, mid-senior
        limit: int = 10,
    ) -> dict:
        """
        Search for jobs on LinkedIn via RapidAPI.
        
        IMPORTANT: Each call uses 1 of your 100 monthly requests!
        
        Args:
            keywords: Job title or keywords (e.g., "Software Engineer")
            location: Location filter (e.g., "London, UK" or "Remote")
            posted_within_days: Max job age in days (default 7)
            max_applicants: Max applicants to include (default 100)
            date_posted: DEPRECATED - mapped from posted_within_days
            job_type: Employment type filter
            experience_level: Experience level filter
            limit: Max results (keep low to save bandwidth)
        
        Returns:
            List of job listings from LinkedIn
        """
        if not self.api_key:
            return {"error": "RapidAPI key not configured", "jobs": []}
        
        if self._request_count >= self._monthly_limit:
            return {
                "error": "Monthly request limit reached (100/month on free tier)",
                "jobs": [],
                "requests_used": self._request_count,
            }
        
        # Map posted_within_days to RapidAPI date_posted param
        if not date_posted:
            if posted_within_days <= 1:
                date_posted = "day"
            elif posted_within_days <= 7:
                date_posted = "week"
            else:
                date_posted = "month"
        
        payload = {
            "search_terms": keywords,
            "location": location,
            "page": "1",
            "fetch_full_text": "yes",  # Get full job descriptions
        }
        
        # Add optional filters
        if date_posted:
            payload["date_posted"] = date_posted
        if job_type:
            payload["job_type"] = job_type
        if experience_level:
            payload["experience_level"] = experience_level
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/",
                    headers=self.headers,
                    json=payload,
                )
                
                self._request_count += 1
                
                if response.status_code == 200:
                    jobs = response.json()
                    
                    # Post-filter by applicant count
                    filtered_jobs = []
                    filtered_count = 0
                    
                    for job in jobs:
                        # Extract applicant count from job data
                        applicants = job.get("applicants_count") or job.get("num_applicants")
                        
                        # Parse if string
                        if isinstance(applicants, str):
                            try:
                                if "+" in applicants:
                                    applicants = int(applicants.replace("+", "")) + 1
                                else:
                                    applicants = int(applicants.replace(",", ""))
                            except ValueError:
                                applicants = None
                        
                        job["applicants"] = applicants
                        
                        # Filter by max_applicants
                        if applicants is not None and applicants > max_applicants:
                            filtered_count += 1
                            continue
                        
                        filtered_jobs.append(job)
                        
                        if len(filtered_jobs) >= limit:
                            break
                    
                    return {
                        "jobs": filtered_jobs,
                        "total_found": len(jobs),
                        "filtered_out": filtered_count,
                        "requests_used": self._request_count,
                        "requests_remaining": self.requests_remaining,
                    }
                elif response.status_code == 429:
                    return {
                        "error": "Rate limit exceeded",
                        "jobs": [],
                        "requests_used": self._request_count,
                    }
                else:
                    return {
                        "error": f"API error: {response.status_code}",
                        "details": response.text,
                        "jobs": [],
                    }
                    
        except httpx.TimeoutException:
            return {"error": "Request timeout", "jobs": []}
        except Exception as e:
            return {"error": str(e), "jobs": []}
    
    async def get_job_details(self, job_id: str) -> dict:
        """
        Get detailed information about a specific job.
        Uses 1 API request!
        """
        # Note: Some RapidAPI LinkedIn endpoints have this
        # Check your specific API documentation
        return {"error": "Not implemented for this API", "job": None}


# Singleton instance
linkedin_client = LinkedInAPIClient()

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
        date_posted: str = "month",  # day, week, month
        job_type: Optional[str] = None,  # full-time, part-time, contract
        experience_level: Optional[str] = None,  # entry, associate, mid-senior
        limit: int = 10,
    ) -> dict:
        """
        Search for jobs on LinkedIn.
        
        IMPORTANT: Each call uses 1 of your 100 monthly requests!
        
        Args:
            keywords: Job title or keywords (e.g., "Software Engineer")
            location: Location filter (e.g., "London, UK" or "Remote")
            date_posted: Time filter - "day", "week", or "month"
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
                    return {
                        "jobs": jobs[:limit],  # Limit results
                        "total_found": len(jobs),
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

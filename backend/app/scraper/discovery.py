"""
DuckDuckGo Job Discovery
=========================
Free, unlimited job discovery using DuckDuckGo search.

Use this as the PRIMARY discovery method to save RapidAPI quota.
"""

from ddgs import DDGS
from typing import Optional
import re


# Location exclusion patterns - jobs to filter out based on user's target location
LOCATION_EXCLUSIONS = {
    "uk": ["united states", "usa", "u.s.", "california", "new york", "texas", "florida", 
           "san francisco", "seattle", "boston", "chicago", "los angeles", "denver",
           "austin", "atlanta", "new jersey", "ohio", "pennsylvania", "michigan",
           "india", "bangalore", "hyderabad", "mumbai", "delhi", "pune"],
    "us": ["united kingdom", "london", "manchester", "birmingham", "uk", "england",
           "india", "bangalore", "hyderabad", "mumbai"],
    "remote": [],  # Remote jobs can be anywhere
}


class JobDiscovery:
    """Discover job listings via DuckDuckGo search."""
    
    def __init__(self):
        pass  # DDGS is created per-search now
    
    def search_linkedin_jobs(
        self,
        keywords: str,
        location: str = "",
        max_results: int = 20,
        date_filter: str = "week",  # day, week, month
    ) -> list[dict]:
        """
        Search for LinkedIn job postings via DuckDuckGo.
        
        This is FREE and UNLIMITED - use as primary discovery!
        
        Args:
            keywords: Job title or keywords
            location: Location filter (e.g., "UK", "London", "Remote")
            max_results: Maximum results to return
            date_filter: Time filter - "day", "week", or "month"
        
        Returns:
            List of discovered job URLs and snippets
        """
        # Build optimized search query
        # Include location more prominently and add recency terms
        location_terms = self._get_location_search_terms(location)
        
        query = f'site:linkedin.com/jobs "{keywords}" {location_terms}'
        
        # Add recency hints to the query
        if date_filter == "day":
            query += " posted today"
        elif date_filter == "week":
            query += " posted this week"
        
        print(f"🔍 DuckDuckGo query: {query}")
        
        try:
            # Fetch more results than needed so we can filter
            fetch_count = min(max_results * 3, 50)
            
            results = DDGS().text(
                query,
                max_results=fetch_count,
            )
            
            print(f"   Raw results: {len(results)}")
            
            # Parse and filter LinkedIn job URLs
            jobs = []
            excluded_count = 0
            
            for result in results:
                url = result.get("href", "")
                
                # Accept various LinkedIn job URL patterns
                if "linkedin.com/jobs" in url:
                    job = self._parse_search_result(result, location)
                    
                    if job:
                        # Filter by location
                        if self._matches_location(job, location):
                            jobs.append(job)
                            print(f"   ✓ Found: {job.get('title', 'Unknown')[:50]}")
                        else:
                            excluded_count += 1
                            print(f"   ✗ Excluded (location): {job.get('title', 'Unknown')[:40]}")
                
                # Stop if we have enough
                if len(jobs) >= max_results:
                    break
            
            print(f"   Jobs parsed: {len(jobs)}, excluded: {excluded_count}")
            return jobs
            
        except Exception as e:
            print(f"❌ DuckDuckGo search error: {e}")
            return []
    
    def _get_location_search_terms(self, location: str) -> str:
        """Convert user location to search terms."""
        loc_lower = location.lower().strip()
        
        if not loc_lower or loc_lower == "remote":
            return "remote"
        
        # Map common abbreviations
        location_map = {
            "uk": '"United Kingdom" OR "London" OR "UK"',
            "united kingdom": '"United Kingdom" OR "London" OR "UK"',
            "us": '"United States" OR "USA"',
            "usa": '"United States" OR "USA"',
        }
        
        return location_map.get(loc_lower, f'"{location}"')
    
    def _matches_location(self, job: dict, target_location: str) -> bool:
        """Check if a job matches the target location."""
        if not target_location or target_location.lower() == "remote":
            return True
        
        target = target_location.lower().strip()
        
        # Get exclusion list for this target
        if target in ["uk", "united kingdom", "london", "england"]:
            exclusions = LOCATION_EXCLUSIONS["uk"]
        elif target in ["us", "usa", "united states"]:
            exclusions = LOCATION_EXCLUSIONS["us"]
        else:
            # No specific exclusions for other locations
            return True
        
        # Check title and snippet for excluded locations
        text_to_check = (
            job.get("title", "").lower() + " " +
            job.get("snippet", "").lower() + " " +
            job.get("company", "").lower()
        )
        
        for exclusion in exclusions:
            if exclusion in text_to_check:
                return False
        
        return True
    
    def search_indeed_jobs(
        self,
        keywords: str,
        location: str = "",
        max_results: int = 20,
    ) -> list[dict]:
        """Search for Indeed job postings."""
        query = f"site:indeed.com/viewjob {keywords}"
        if location:
            query += f" {location}"
        
        try:
            results = DDGS().text(query, max_results=max_results)
            
            jobs = []
            for result in results:
                url = result.get("href", "")
                if "indeed.com" in url and "viewjob" in url:
                    job = self._parse_search_result(result, location, source="indeed")
                    if job and self._matches_location(job, location):
                        jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []
    
    def search_all_sources(
        self,
        keywords: str,
        location: str = "",
        max_per_source: int = 10,
    ) -> dict:
        """
        Search across all job sources.
        
        Returns:
            Dict with jobs from each source
        """
        return {
            "linkedin": self.search_linkedin_jobs(keywords, location, max_per_source),
            "indeed": self.search_indeed_jobs(keywords, location, max_per_source),
            "total": 0,  # Will be calculated
        }
    
    def _parse_search_result(self, result: dict, location: str = "", source: str = "linkedin") -> Optional[dict]:
        """Parse a DuckDuckGo search result into job format."""
        title = result.get("title", "")
        url = result.get("href", "")
        snippet = result.get("body", "")
        
        if not url:
            return None
        
        # Filter out job listing pages (not specific jobs)
        if "/jobs/search" in url or "/jobs/collections" in url:
            return None
        
        # Try to extract job ID from LinkedIn URL
        external_id = None
        if "linkedin.com/jobs/view" in url:
            match = re.search(r"/jobs/view/(\d+)", url)
            if match:
                external_id = f"linkedin-{match.group(1)}"
        
        # Try to extract company from title (often in format "Job Title at Company")
        company = "Unknown"
        job_title = title
        
        # Handle "... hiring ... in ..." format
        if " hiring " in title.lower():
            parts = title.split(" hiring ")
            if len(parts) >= 2:
                company = parts[0].strip()
                job_title = parts[1].split(" in ")[0].strip()
                job_title = job_title.split(" | ")[0].strip()
        elif " at " in title:
            parts = title.split(" at ")
            if len(parts) >= 2:
                job_title = parts[0].strip()
                company = parts[1].split(" - ")[0].strip()
                company = company.split(" | ")[0].strip()
        elif " - " in title:
            parts = title.split(" - ")
            if len(parts) >= 2:
                company = parts[1].strip()
                company = company.split(" | ")[0].strip()
        
        # Clean up LinkedIn suffix
        company = company.replace(" | LinkedIn", "").strip()
        job_title = job_title.replace(" | LinkedIn", "").strip()
        
        # Extract location from snippet if possible
        job_location = None
        loc_match = re.search(r'(?:in|at|location:)\s*([^.·,]+)', snippet.lower())
        if loc_match:
            job_location = loc_match.group(1).strip()[:50]
        
        # Extract applicant count from snippet
        # Patterns: "45 applicants", "Be an early applicant", "Over 100 applicants"
        applicants = None
        applicants_match = re.search(
            r'(\d+)\s*applicant|over\s+(\d+)\s*applicant|be\s+an?\s+early\s+applicant',
            snippet.lower()
        )
        if applicants_match:
            if "early applicant" in snippet.lower():
                applicants = 0  # Very few applicants
            elif applicants_match.group(1):
                applicants = int(applicants_match.group(1))
            elif applicants_match.group(2):
                applicants = int(applicants_match.group(2)) + 50  # "Over X" means more
        
        # Extract posted time from snippet
        # Patterns: "1 month ago", "2 weeks ago", "3 days ago", "1 hour ago"
        posted_ago = None
        time_match = re.search(
            r'(\d+)\s*(hour|day|week|month)s?\s*ago',
            snippet.lower()
        )
        if time_match:
            num = int(time_match.group(1))
            unit = time_match.group(2)
            posted_ago = f"{num} {unit}{'s' if num > 1 else ''} ago"
        
        return {
            "external_id": external_id,
            "title": job_title[:200],
            "company": company[:100],
            "location": job_location,
            "link": url,
            "snippet": snippet[:500],
            "source": source,
            "discovery_method": "duckduckgo",
            "applicants": applicants,
            "posted_ago": posted_ago,
        }


# Singleton instance
job_discovery = JobDiscovery()

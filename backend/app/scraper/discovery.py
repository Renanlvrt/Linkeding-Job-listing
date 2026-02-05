"""
Job Discovery Module
=====================
Hybrid job discovery using LinkedIn Guest API (primary) with DuckDuckGo fallback.

Guest API (Primary):
- Direct LinkedIn API with native filter support
- Experience levels, job types, workplace types work correctly
- 5 second delay between requests

DuckDuckGo (Fallback):
- Used when Guest API fails or is rate limited
- Free, unlimited, but filters are hint-only

Enhanced 2026:
- Guest API with native filters
- Automatic fallback with status notification
- Robust applicant parsing from snippets
"""

from ddgs import DDGS
from typing import Optional
import re
import logging
import asyncio

from app.scraper.filters import (
    parse_applicant_count,
    parse_posted_time,
    job_passes_filters,
    days_to_linkedin_param,
    CLOSED_PATTERNS,
    REPOSTED_PATTERNS,
    build_ddg_exclude_query,
)
from app.scraper.anti_detect import sync_random_delay
from app.scraper.linkedin_guest_api import search_jobs_via_guest_api
from app.scraper.validator import validate_jobs

# Set up logging
logger = logging.getLogger(__name__)


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
        self.filter_stats = {
            "total_found": 0,
            "passed": 0,
            "filtered_location": 0,
            "filtered_applicants": 0,
            "filtered_age": 0,
            "filtered_closed": 0,
            "filtered_reposted": 0,
        }
    
    async def search_linkedin_jobs(
        self,
        keywords: str,
        location: str = "",
        max_results: int = 20,
        posted_within_days: int = 7,
        max_applicants: int = 100,
        date_filter: str = None,  # DEPRECATED: use posted_within_days
        experience_levels: list[str] = None,  # ["entry", "mid-senior"]
        job_types: list[str] = None,  # ["full-time", "contract"]
        workplace_types: list[str] = None,  # ["remote", "hybrid"]
        easy_apply: bool = False,
    ) -> dict:
        """
        Search for LinkedIn job postings.
        
        Uses Guest API as primary (native filters work correctly).
        Falls back to DuckDuckGo if Guest API fails.
        
        Args:
            keywords: Job title or keywords
            location: Location filter (e.g., "UK", "London", "Remote")
            max_results: Maximum results to return
            posted_within_days: Max job age in days (default 7)
            max_applicants: Max applicants to include (default 100)
            date_filter: DEPRECATED - use posted_within_days instead
            experience_levels: Filter by experience (entry, mid-senior, etc.)
            job_types: Filter by job type (full-time, contract, etc.)
            workplace_types: Filter by workplace (remote, hybrid, on-site)
            easy_apply: Only show Easy Apply jobs
        
        Returns:
            Dict with 'jobs' list, 'search_method' (guest_api/duckduckgo), 
            and 'fallback_used' boolean
        """
        # Reset stats
        self.filter_stats = {
            "total_found": 0,
            "passed": 0,
            "filtered_location": 0,
            "filtered_applicants": 0,
            "filtered_age": 0,
            "filtered_closed": 0,
            "filtered_reposted": 0,
        }
        
        # Handle legacy date_filter param
        if date_filter and not posted_within_days:
            date_map = {"day": 1, "week": 7, "month": 30}
            posted_within_days = date_map.get(date_filter, 7)
        
        max_hours_old = posted_within_days * 24
        
        # Try Guest API first (native filter support)
        logger.info(f"🔍 Trying LinkedIn Guest API: keywords='{keywords}', location='{location}'")
        logger.info(f"   Filters: experience={experience_levels}, job_types={job_types}, workplace={workplace_types}")
        
        try:
            # Run async Guest API search
            guest_jobs, guest_success = await search_jobs_via_guest_api(
                keywords=keywords,
                location=location,
                max_results=max_results,
                posted_within_days=posted_within_days,
                experience_levels=experience_levels,
                job_types=job_types,
                workplace_types=workplace_types,
                easy_apply=easy_apply,
            )
            
            if guest_success and len(guest_jobs) > 0:
                # Apply applicant filter to Guest API results
                filtered_jobs = []
                for job in guest_jobs:
                    # Apply max_applicants filter if we have that data
                    if job.get("applicant_count") and job["applicant_count"] > max_applicants:
                        continue
                    filtered_jobs.append(job)
                
                logger.info(f"✓ Guest API success: {len(filtered_jobs)} jobs found")
                return {
                    "jobs": filtered_jobs[:max_results],
                    "search_method": "linkedin_guest_api",
                    "fallback_used": False,
                }
            else:
                logger.warning("Guest API returned no results, falling back to DuckDuckGo")
        
        except Exception as e:
            logger.warning(f"Guest API failed ({e}), falling back to DuckDuckGo")
        
        # Fallback to DuckDuckGo
        logger.info(f"🦆 Using DuckDuckGo fallback (filters are hints only)")
        
        # Run synchronous DuckDuckGo search in a separate thread to avoid blocking main loop
        loop = asyncio.get_running_loop()
        ddg_jobs = await loop.run_in_executor(
            None,
            lambda: self._search_via_duckduckgo(
                keywords=keywords,
                location=location,
                max_results=max_results,
                posted_within_days=posted_within_days,
                max_applicants=max_applicants,
            )
        )
        
        # Validate job status (check for "No longer accepting applications")
        if ddg_jobs:
            logger.info(f"Validating {len(ddg_jobs)} fallback jobs...")
            ddg_jobs = await validate_jobs(ddg_jobs, max_concurrent=5)
        
        return {
            "jobs": ddg_jobs,
            "search_method": "duckduckgo",
            "fallback_used": True,
            "fallback_reason": "LinkedIn Guest API unavailable. Filters (experience, job type) are hints only with DuckDuckGo.",
        }
    
    def _search_via_duckduckgo(
        self,
        keywords: str,
        location: str,
        max_results: int,
        posted_within_days: int,
        max_applicants: int,
    ) -> list[dict]:
        """
        Search via DuckDuckGo (fallback method).
        Note: Filters like experience_level are hints only, not enforced.
        """
        max_hours_old = posted_within_days * 24
        
        # Build optimized search query with LinkedIn hints
        location_terms = self._get_location_search_terms(location)
        
        # Include f_TPR hint for DDG to prefer recent results
        tpr_param = days_to_linkedin_param(posted_within_days)
        query = f'site:linkedin.com/jobs "{keywords}" {location_terms}'
        
        # Add recency hints
        if posted_within_days <= 1:
            query += ' "posted today" OR "1 day ago"'
        elif posted_within_days <= 7:
            query += ' "posted this week" OR "days ago"'
        
        logger.info(f"🔍 DuckDuckGo query: {query}")
        logger.info(f"   Filters: max_applicants={max_applicants}, posted_within_days={posted_within_days}")
        
        try:
            # Fetch more results than needed so we can filter aggressively
            fetch_count = min(max_results * 4, 60)
            
            results = DDGS().text(
                query,
                max_results=fetch_count,
            )
            
            self.filter_stats["total_found"] = len(results)
            logger.info(f"   Raw results: {len(results)}")
            
            # Parse and filter LinkedIn job URLs
            jobs = []
            
            for result in results:
                url = result.get("href", "")
                
                # Accept various LinkedIn job URL patterns
                if "linkedin.com/jobs" in url:
                    job = self._parse_search_result(result, location)
                    
                    if not job:
                        continue
                    
                    # Extract applicant count from snippet
                    snippet = job.get("snippet", "")
                    job["applicants"] = parse_applicant_count(snippet)
                    
                    # Extract posted time from snippet
                    posted_hours = parse_posted_time(snippet)
                    if posted_hours:
                        job["posted_hours_ago"] = posted_hours
                    
                    # TIER 1: Snippet filter for closed/reposted (FIRST CHECK)
                    snippet_passes, snippet_reason = self._filter_by_snippet(snippet)
                    if not snippet_passes:
                        if "closed" in snippet_reason:
                            self.filter_stats["filtered_closed"] += 1
                        elif "reposted" in snippet_reason:
                            self.filter_stats["filtered_reposted"] += 1
                        logger.debug(f"   ✗ Excluded ({snippet_reason}): {job.get('title', 'Unknown')[:40]}")
                        job["filter_reason"] = snippet_reason
                        job["validation_tier"] = "snippet"
                        continue
                    
                    # Filter by location
                    if not self._matches_location(job, location):
                        self.filter_stats["filtered_location"] += 1
                        logger.debug(f"   ✗ Excluded (location): {job.get('title', 'Unknown')[:40]}")
                        continue
                    
                    # Filter by applicants and age
                    passes, reason = job_passes_filters(
                        job, 
                        max_applicants=max_applicants,
                        max_hours_old=max_hours_old
                    )
                    
                    if not passes:
                        if "applicants" in reason:
                            self.filter_stats["filtered_applicants"] += 1
                        elif "old" in reason:
                            self.filter_stats["filtered_age"] += 1
                        logger.debug(f"   ✗ Excluded ({reason}): {job.get('title', 'Unknown')[:40]}")
                        continue
                    
                    # Job passed all filters
                    job["filter_passed"] = True
                    jobs.append(job)
                    self.filter_stats["passed"] += 1
                    
                    applicants_str = f"{job.get('applicants', '?')} applicants" if job.get('applicants') is not None else "unknown applicants"
                    logger.info(f"   ✓ Found: {job.get('title', 'Unknown')[:50]} ({applicants_str})")
                
                # Stop if we have enough
                if len(jobs) >= max_results:
                    break
            
            logger.info(f"   Results: {len(jobs)} passed, {self.filter_stats}")
            return jobs
            
        except Exception as e:
            logger.error(f"❌ DuckDuckGo search error: {e}")
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
    
    def _filter_by_snippet(self, snippet: str) -> tuple[bool, str]:
        """
        Tier 1: Pre-filter by DDG snippet text for closed/reposted jobs.
        
        Args:
            snippet: DDG result snippet text
        
        Returns:
            (passes, reason) - False if closed/reposted detected
        """
        if not snippet:
            return True, "no_snippet"
        
        text_lower = snippet.lower()
        
        # Check for CLOSED patterns
        for pattern in CLOSED_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "closed_in_snippet"
        
        # Check for REPOSTED patterns
        for pattern in REPOSTED_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "reposted_in_snippet"
        
        return True, "passed"

    
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
            "url": url,  # Frontend expects 'link'
            "snippet": snippet[:500],
            "source": source,
            "discovery_method": "duckduckgo",
            "applicants": applicants,
            "posted_ago": posted_ago,
        }


# Singleton instance
job_discovery = JobDiscovery()

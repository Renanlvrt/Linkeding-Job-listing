"""
LinkedIn Guest API Client

Calls LinkedIn's public Guest API directly to search for jobs with native filter support.
This bypasses the DuckDuckGo discovery method and uses LinkedIn's native filtering.

API Endpoint: https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
"""

import httpx
import asyncio
import logging
import random
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# LinkedIn Guest API base URL
GUEST_API_BASE = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

# Filter code mappings (LinkedIn's internal codes)
EXPERIENCE_LEVEL_CODES = {
    "internship": "1",
    "entry": "2",
    "associate": "3",
    "mid-senior": "4",
    "director": "5",
    "executive": "6",
}

JOB_TYPE_CODES = {
    "full-time": "F",
    "part-time": "P",
    "contract": "C",
    "temporary": "T",
    "internship": "I",
    "volunteer": "V",
    "other": "O",
}

WORKPLACE_TYPE_CODES = {
    "on-site": "1",
    "remote": "2",
    "hybrid": "3",
}

# Time filter in seconds
TIME_FILTERS = {
    1: 86400,      # 24 hours
    3: 259200,     # 3 days
    7: 604800,     # 1 week
    14: 1209600,   # 2 weeks
    30: 2592000,   # 1 month
}

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


@dataclass
class GuestAPIJob:
    """Job result from Guest API."""
    job_id: str
    title: str
    company: str
    location: str
    url: str
    posted_time: Optional[str] = None
    applicant_count: Optional[int] = None
    is_easy_apply: bool = False
    snippet: Optional[str] = None  # Added snippet field


class LinkedInGuestAPI:
    """
    Client for LinkedIn's public Guest API.
    
    This API allows job searching without authentication, with native filter support.
    """
    
    def __init__(self, delay_seconds: float = 5.0):
        """
        Initialize Guest API client.
        
        Args:
            delay_seconds: Delay between requests to avoid rate limiting
        """
        self.delay_seconds = delay_seconds
        self._last_request_time = 0
    
    def _get_headers(self) -> dict:
        """Get request headers with random user agent."""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }
    
    def _build_search_url(
        self,
        keywords: str,
        location: str = "",
        start: int = 0,
        posted_within_days: int = 7,
        experience_levels: list[str] = None,
        job_types: list[str] = None,
        workplace_types: list[str] = None,
        easy_apply: bool = False,
    ) -> str:
        """
        Build Guest API search URL with filters.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            start: Pagination offset
            posted_within_days: Filter by days since posted
            experience_levels: List of experience levels (internship, entry, etc.)
            job_types: List of job types (full-time, contract, etc.)
            workplace_types: List of workplace types (remote, hybrid, on-site)
            easy_apply: Filter for Easy Apply jobs only
        
        Returns:
            Full API URL with query parameters
        """
        params = {
            "keywords": keywords,
            "location": location,
            "start": start,
            "sortBy": "DD",  # Sort by date (most recent first)
        }
        
        # Time filter
        if posted_within_days and posted_within_days in TIME_FILTERS:
            params["f_TPR"] = f"r{TIME_FILTERS[posted_within_days]}"
        
        # Experience level filter (f_E)
        if experience_levels:
            codes = [EXPERIENCE_LEVEL_CODES.get(lvl.lower()) for lvl in experience_levels]
            codes = [c for c in codes if c]
            if codes:
                params["f_E"] = ",".join(codes)
        
        # Job type filter (f_JT)
        if job_types:
            codes = [JOB_TYPE_CODES.get(jt.lower()) for jt in job_types]
            codes = [c for c in codes if c]
            if codes:
                params["f_JT"] = ",".join(codes)
        
        # Workplace type filter (f_WT)
        if workplace_types:
            codes = [WORKPLACE_TYPE_CODES.get(wt.lower()) for wt in workplace_types]
            codes = [c for c in codes if c]
            if codes:
                params["f_WT"] = ",".join(codes)
        
        # Easy Apply filter
        if easy_apply:
            params["f_AL"] = "true"
        
        return f"{GUEST_API_BASE}?{urlencode(params)}"
    
    def _parse_job_card(self, card_element) -> Optional[GuestAPIJob]:
        """
        Parse a job card from the API response HTML.
        
        Args:
            card_element: BeautifulSoup element for a job card
        
        Returns:
            GuestAPIJob object or None if parsing fails
        """
        try:
            # Extract job ID from data-entity-urn
            entity_urn = card_element.get("data-entity-urn", "")
            job_id_match = re.search(r"jobPosting:(\d+)", entity_urn)
            if not job_id_match:
                # Try to get from link
                link = card_element.select_one("a.base-card__full-link")
                if link and link.get("href"):
                    job_id_match = re.search(r"/jobs/view/(\d+)", link.get("href", ""))
            
            if not job_id_match:
                return None
            
            job_id = job_id_match.group(1)
            
            # Extract title
            title_elem = card_element.select_one("h3.base-search-card__title, .job-search-card__title")
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
            
            # Extract company
            company_elem = card_element.select_one("h4.base-search-card__subtitle, .job-search-card__subtitle")
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = card_element.select_one(".job-search-card__location, .base-search-card__metadata")
            location = location_elem.get_text(strip=True) if location_elem else ""
            
            # Extract posted time
            time_elem = card_element.select_one("time, .job-search-card__listdate")
            posted_time = time_elem.get_text(strip=True) if time_elem else None
            
            # Check for Easy Apply
            easy_apply_elem = card_element.select_one(".job-search-card__easy-apply-label")
            is_easy_apply = easy_apply_elem is not None

            # Extract applicants (if available) - usually not on search card, but we check
            applicants = None
            applicant_elem = card_element.select_one(".job-search-card__num-applicants")
            if applicant_elem:
                text = applicant_elem.get_text(strip=True)
                match = re.search(r'(\d+)', text)
                if match:
                    applicants = int(match.group(1))

            # Extract snippet/benefits (often hidden or limited)
            snippet_elem = card_element.select_one(".job-search-card__snippet, .job-search-card__benefits")
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else f"{title} at {company}"
            
            # Build job URL
            url = f"https://www.linkedin.com/jobs/view/{job_id}"
            
            return GuestAPIJob(
                job_id=job_id,
                title=title,
                company=company,
                location=location,
                url=url,
                posted_time=posted_time,
                applicant_count=applicants,
                is_easy_apply=is_easy_apply,
                snippet=snippet
            )
        except Exception as e:
            logger.warning(f"Failed to parse job card: {e}")
            return None
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        import time
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.delay_seconds:
            wait_time = self.delay_seconds - elapsed + random.uniform(0.5, 1.5)
            logger.debug(f"Rate limiting: waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        self._last_request_time = time.time()
    
    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        max_results: int = 25,
        posted_within_days: int = 7,
        experience_levels: list[str] = None,
        job_types: list[str] = None,
        workplace_types: list[str] = None,
        easy_apply: bool = False,
    ) -> tuple[list[GuestAPIJob], bool]:
        """
        Search for jobs using LinkedIn Guest API.
        
        Args:
            keywords: Job search keywords
            location: Location filter
            max_results: Maximum number of results to return
            posted_within_days: Filter by days since posted
            experience_levels: List of experience levels
            job_types: List of job types
            workplace_types: List of workplace types
            easy_apply: Filter for Easy Apply only
        
        Returns:
            Tuple of (list of jobs, success boolean)
        """
        jobs = []
        start = 0
        page_size = 25  # LinkedIn returns 25 jobs per page
        
        logger.info(f"Guest API search: keywords='{keywords}', location='{location}', "
                   f"experience={experience_levels}, job_types={job_types}, "
                   f"workplace={workplace_types}, easy_apply={easy_apply}")
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            while len(jobs) < max_results:
                await self._rate_limit()
                
                url = self._build_search_url(
                    keywords=keywords,
                    location=location,
                    start=start,
                    posted_within_days=posted_within_days,
                    experience_levels=experience_levels,
                    job_types=job_types,
                    workplace_types=workplace_types,
                    easy_apply=easy_apply,
                )
                
                logger.debug(f"Fetching: {url}")
                
                try:
                    response = await client.get(url, headers=self._get_headers())
                    
                    if response.status_code == 429:
                        logger.warning("Guest API rate limited (429). Triggering fallback.")
                        return jobs, False  # Fail fast to trigger fallback
                    
                    if response.status_code != 200:
                        logger.error(f"Guest API returned {response.status_code}")
                        return jobs, False
                    
                    html = response.text
                    soup = BeautifulSoup(html, "html.parser")
                    
                    # Find job cards
                    cards = soup.select("li, .base-card, .job-search-card")
                    
                    if not cards:
                        logger.info("No more job cards found")
                        break
                    
                    page_jobs = 0
                    for card in cards:
                        job = self._parse_job_card(card)
                        if job and job.job_id not in [j.job_id for j in jobs]:
                            jobs.append(job)
                            page_jobs += 1
                            if len(jobs) >= max_results:
                                break
                    
                    logger.info(f"Page {start // page_size + 1}: found {page_jobs} jobs (total: {len(jobs)})")
                    
                    if page_jobs == 0:
                        # No new jobs found, stop pagination
                        break
                    
                    start += page_size
                    
                except httpx.TimeoutException:
                    logger.error("Request timeout")
                    return jobs, len(jobs) > 0
                except Exception as e:
                    logger.error(f"Guest API error: {e}")
                    return jobs, len(jobs) > 0
        
        logger.info(f"Guest API search complete: {len(jobs)} jobs found")
        return jobs, True
    
    def to_job_dict(self, job: GuestAPIJob) -> dict:
        """Convert GuestAPIJob to dictionary format matching existing code."""
        return {
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "url": job.url,
            "link": job.url,  # Frontend expects 'link'
            "posted_time": job.posted_time,
            "is_easy_apply": job.is_easy_apply,
            "applicants": job.applicant_count,
            "applicant_count": job.applicant_count,
            "snippet": job.snippet,
            "description": job.snippet, # Fallback
            "source": "linkedin_guest_api",
        }


# Singleton instance
_guest_api = None


def get_guest_api(delay_seconds: float = 5.0) -> LinkedInGuestAPI:
    """Get or create Guest API client singleton."""
    global _guest_api
    if _guest_api is None:
        _guest_api = LinkedInGuestAPI(delay_seconds=delay_seconds)
    return _guest_api


async def search_jobs_via_guest_api(
    keywords: str,
    location: str = "",
    max_results: int = 25,
    posted_within_days: int = 7,
    experience_levels: list[str] = None,
    job_types: list[str] = None,
    workplace_types: list[str] = None,
    easy_apply: bool = False,
) -> tuple[list[dict], bool]:
    """
    Convenience function to search jobs via Guest API.
    
    Returns:
        Tuple of (list of job dicts, success boolean)
    """
    api = get_guest_api()
    jobs, success = await api.search_jobs(
        keywords=keywords,
        location=location,
        max_results=max_results,
        posted_within_days=posted_within_days,
        experience_levels=experience_levels,
        job_types=job_types,
        workplace_types=workplace_types,
        easy_apply=easy_apply,
    )
    return [api.to_job_dict(job) for job in jobs], success

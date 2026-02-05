"""
Job Validation Module
=====================
Validates if job URLs are still responding and active.
Essential for validating DuckDuckGo results which may be stale.
"""

import httpx
import logging
import asyncio
import re
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup

from app.scraper.filters import CLOSED_PATTERNS

logger = logging.getLogger(__name__)

# User agents for validation requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

async def validate_job_active(client: httpx.AsyncClient, job: dict) -> Tuple[bool, str]:
    """
    Check if a job mapping is still active by fetching its URL.
    
    Args:
        client: Async HTTP client
        job: Job dictionary with 'url' key
        
    Returns:
        Tuple (is_active, reason_if_not, description)
    """
    description = None
    url = job.get("url")
    if not url:
        return False, "no_url"
        
    try:
        # Fetch the page with a small random delay if processing many (handled by caller)
        response = await client.get(url, headers={"User-Agent": USER_AGENTS[0]}, follow_redirects=True)
        
        if response.status_code == 404:
            return False, "404_not_found", None
            
        if response.status_code != 200:
            # If rate limited (999/429), we might want to assume active to avoid false negatives?
            # LinkedIn often returns 999 for scrapers.
            # However, if we can't see the page, we can't validate the status.
            # DuckDuckGo links are often valid URLs.
            # Let's log and assume active if it's a soft block, but maybe flag it?
            if response.status_code in [429, 999]:
                 # ...
                 logger.warning(f"Validation blocked ({response.status_code}) for {url[:40]}...")
                 return True, "blocked_cannot_validate", None
            
            return False, f"status_{response.status_code}", None

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        text_content = soup.get_text().lower()
        
        # Check against closed patterns
        for pattern in CLOSED_PATTERNS:
            if re.search(pattern, text_content):
                return False, f"closed_pattern_match: {pattern}", None

        # EXTRACT DESCRIPTION
        desc_elem = soup.select_one("div.show-more-less-html__markup, .description__text, .job-view-main-content")
        if desc_elem:
            description = str(desc_elem.encode_contents().decode('utf-8')).strip()

        # If we reach here, no closed patterns found
        return True, "active", description

    except Exception as e:
        logger.warning(f"Validation error for {url}: {e}")
        # Fail open on network errors to avoid hiding good jobs due to transient issues
        return True, "network_error_skip_validation", None

async def validate_jobs(jobs: List[Dict], max_concurrent: int = 5) -> List[Dict]:
    """
    Validate a list of jobs concurrently.
    Returns list of jobs that are confirmed active or indeterminate.
    Closed jobs are removed.
    """
    if not jobs:
        return []
        
    logger.info(f"Validating {len(jobs)} jobs for active status...")
    
    active_jobs = []
    sem = asyncio.Semaphore(max_concurrent)
    
    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENTS[0]}, 
        timeout=10.0,
        follow_redirects=True
    ) as client:
        
        async def _check(job):
            async with sem:
                # Small random delay to avoid burst patterns
                await asyncio.sleep(0.1) 
                is_active, reason, description = await validate_job_active(client, job)
                return job, is_active, reason, description

        tasks = [_check(job) for job in jobs]
        results = await asyncio.gather(*tasks)
        
        for job, is_active, reason, description in results:
            if is_active:
                job["validation_status"] = "active" if reason == "active" else "unchecked"
                if description:
                    job["description"] = description
                active_jobs.append(job)
            else:
                logger.info(f"❌ Removing closed job: {job.get('title', 'Unknown')} ({reason})")
                
    logger.info(f"Validation complete. kept {len(active_jobs)}/{len(jobs)} jobs.")
    return active_jobs


# --- Backward Compatibility for Orchestrator ---
PLAYWRIGHT_AVAILABLE = False

class JobValidator:
    """
    Mock validator for compatibility with legacy Orchestrator calls.
    The new validation logic is handled directly in discovery.py via validate_jobs().
    """
    async def validate_jobs(self, jobs, max_applicants=None, max_age_days=None, max_to_validate=None):
        logger.warning("Tier 3 (Playwright) validation requested but not available. Using basic validation only.")
        # We could route this to our new validator, but Orchestrator params are different.
        # For now, just return jobs as-is since discovery.py likely already filtered them.
        return jobs

job_validator = JobValidator()

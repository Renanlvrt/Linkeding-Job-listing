"""
HTML Validator (Tier 2)
========================
Lightweight HTTP + BeautifulSoup validation for job pages.

Features:
- No browser needed (fast, low overhead)
- Detects closed/reposted from page text
- Parses applicant count from HTML
- Works on public LinkedIn job pages

Usage:
    from app.scraper.html_validator import validate_job_html, validate_jobs_html
    
    result = await validate_job_html(url, max_applicants=70)
    # result = {"passes": True/False, "reason": str, "applicants": int, "tier": "html"}

NOTE: Public LinkedIn pages may have limited data. Use as Tier 2 between
snippet filtering and Playwright validation for best accuracy.
"""

import re
import asyncio
import logging
from typing import Optional

import httpx

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from app.scraper.filters import (
    CLOSED_PATTERNS,
    REPOSTED_PATTERNS,
    parse_applicant_count,
    parse_posted_time,
)
from app.scraper.anti_detect import (
    get_browser_headers,
    random_delay,
    rate_limiter,
)

logger = logging.getLogger(__name__)


async def validate_job_html(
    url: str,
    max_applicants: int = 100,
    max_age_hours: int = 168,  # 7 days
    timeout: float = 15.0,
) -> dict:
    """
    Tier 2: Validate job by fetching HTML (no browser).
    
    Args:
        url: LinkedIn job URL
        max_applicants: Max applicant count to pass
        max_age_hours: Max age in hours to pass
        timeout: Request timeout in seconds
    
    Returns:
        Validation result dict:
        - passes: bool
        - reason: str (e.g., "closed", "reposted", "too_many_applicants")
        - applicants: int or None
        - posted_hours_ago: int or None
        - tier: "html"
    """
    result = {
        "url": url,
        "passes": True,
        "reason": "passed",
        "applicants": None,
        "posted_hours_ago": None,
        "tier": "html",
        "is_closed": False,
        "is_reposted": False,
    }
    
    if not BS4_AVAILABLE:
        logger.warning("BeautifulSoup not installed, skipping HTML validation")
        result["reason"] = "bs4_unavailable"
        return result
    
    try:
        # Rate limit
        if not rate_limiter.can_request():
            result["reason"] = "rate_limit_exceeded"
            result["passes"] = True  # Don't filter, just skip validation
            return result
        
        rate_limiter.request_count += 1
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = get_browser_headers()
            response = await client.get(url, headers=headers, follow_redirects=True)
            
            if response.status_code != 200:
                result["reason"] = f"http_{response.status_code}"
                result["passes"] = False
                return result
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True).lower()
            
            # Check for CLOSED indicators
            for pattern in CLOSED_PATTERNS:
                if re.search(pattern, page_text, re.IGNORECASE):
                    result["passes"] = False
                    result["reason"] = "closed"
                    result["is_closed"] = True
                    logger.debug(f"   ✗ HTML: Closed detected - {url[:50]}")
                    return result
            
            # Check for REPOSTED indicators
            for pattern in REPOSTED_PATTERNS:
                if re.search(pattern, page_text, re.IGNORECASE):
                    result["passes"] = False
                    result["reason"] = "reposted"
                    result["is_reposted"] = True
                    logger.debug(f"   ✗ HTML: Reposted detected - {url[:50]}")
                    return result
            
            # Extract applicant count
            applicants = parse_applicant_count(page_text)
            if applicants is not None:
                result["applicants"] = applicants
                if applicants > max_applicants:
                    result["passes"] = False
                    result["reason"] = f"too_many_applicants:{applicants}"
                    logger.debug(f"   ✗ HTML: {applicants} applicants > {max_applicants} - {url[:50]}")
                    return result
            
            # Extract posted time
            posted_hours = parse_posted_time(page_text)
            if posted_hours is not None:
                result["posted_hours_ago"] = posted_hours
                if posted_hours > max_age_hours:
                    result["passes"] = False
                    result["reason"] = f"too_old:{posted_hours}h"
                    logger.debug(f"   ✗ HTML: {posted_hours}h old > {max_age_hours}h - {url[:50]}")
                    return result
            
            logger.debug(f"   ✓ HTML: Passed - {url[:50]} (applicants={applicants})")
            return result
    
    except httpx.TimeoutException:
        result["reason"] = "timeout"
        result["passes"] = True  # Don't filter on timeout, let Playwright handle
        logger.warning(f"   ⚠ HTML: Timeout - {url[:50]}")
        return result
    
    except Exception as e:
        result["reason"] = f"error:{str(e)[:30]}"
        result["passes"] = True  # Don't filter on errors
        logger.error(f"   ⚠ HTML: Error - {url[:50]}: {e}")
        return result


async def validate_jobs_html(
    jobs: list[dict],
    max_applicants: int = 100,
    max_age_days: int = 7,
    max_concurrent: int = 5,
    skip_validated: bool = True,
) -> tuple[list[dict], dict]:
    """
    Tier 2: Batch validate jobs via HTML fetch.
    
    Args:
        jobs: List of job dicts with 'link' or 'job_url'
        max_applicants: Max applicant filter
        max_age_days: Max age filter in days
        max_concurrent: Max parallel requests
        skip_validated: Skip jobs already marked as validated
    
    Returns:
        (filtered_jobs, stats) - Jobs that passed, validation stats
    """
    stats = {
        "total": len(jobs),
        "validated": 0,
        "passed": 0,
        "filtered_closed": 0,
        "filtered_reposted": 0,
        "filtered_applicants": 0,
        "filtered_age": 0,
        "errors": 0,
    }
    
    if not jobs:
        return jobs, stats
    
    max_age_hours = max_age_days * 24
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def validate_with_semaphore(job: dict) -> tuple[dict, bool]:
        # Skip if already validated
        if skip_validated and job.get("validation_tier"):
            return job, job.get("passes_validation", True)
        
        url = job.get("link") or job.get("job_url", "")
        if not url:
            return job, True  # No URL, pass through
        
        async with semaphore:
            await random_delay(0.5, 1.5)  # Rate limiting
            result = await validate_job_html(url, max_applicants, max_age_hours)
        
        # Merge result into job
        job["html_applicants"] = result.get("applicants")
        job["html_posted_hours_ago"] = result.get("posted_hours_ago")
        job["html_is_closed"] = result.get("is_closed", False)
        job["html_is_reposted"] = result.get("is_reposted", False)
        job["validation_tier"] = "html"
        job["validation_reason"] = result.get("reason")
        
        return job, result.get("passes", True)
    
    # Run all validations
    tasks = [validate_with_semaphore(job) for job in jobs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    passed_jobs = []
    for result in results:
        if isinstance(result, Exception):
            stats["errors"] += 1
            continue
        
        job, passed = result
        stats["validated"] += 1
        
        if passed:
            stats["passed"] += 1
            passed_jobs.append(job)
        else:
            reason = job.get("validation_reason", "")
            if "closed" in reason:
                stats["filtered_closed"] += 1
            elif "reposted" in reason:
                stats["filtered_reposted"] += 1
            elif "applicants" in reason:
                stats["filtered_applicants"] += 1
            elif "old" in reason:
                stats["filtered_age"] += 1
    
    logger.info(f"🔍 HTML Validation: {stats['passed']}/{stats['total']} passed | Stats: {stats}")
    
    return passed_jobs, stats


# Convenience instance
html_validator = type('HTMLValidator', (), {
    'validate_job': staticmethod(validate_job_html),
    'validate_jobs': staticmethod(validate_jobs_html),
})()

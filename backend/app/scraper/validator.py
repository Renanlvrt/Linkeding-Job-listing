"""
Job Validator (Playwright)
===========================
Validates job listings by visiting actual LinkedIn pages.

Features:
- Extract real applicant count
- Verify job is still accepting applications
- Parse accurate posted date
- Anti-detection via stealth browser

Usage:
    validator = JobValidator()
    result = await validator.validate_job(url, max_applicants=70, max_age_days=7)
    
NOTE: Use sparingly! Each validation adds 2-5 seconds latency.
Recommended: Validate top 10-20 jobs from initial scrape only.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from app.scraper.filters import (
    parse_applicant_count,
    parse_posted_time,
    LINKEDIN_SELECTORS,
)
from app.scraper.anti_detect import (
    setup_stealth_page,
    random_delay,
    rate_limiter,
    get_random_viewport,
    get_random_user_agent,
    STEALTH_BROWSER_ARGS,
)

logger = logging.getLogger(__name__)


class JobValidator:
    """
    Validates job listings via Playwright browser automation.
    
    Extracts:
    - Actual applicant count
    - Whether job is still active (apply button exists)
    - Posted date/time
    """
    
    def __init__(self, max_concurrent: int = 5):
        """
        Args:
            max_concurrent: Max parallel validations (semaphore limit)
        """
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._browser: Optional[Browser] = None
        self._playwright = None
    
    async def _ensure_browser(self) -> Browser:
        """Lazy-initialize browser."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )
        
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=STEALTH_BROWSER_ARGS,
            )
            logger.info("🌐 Playwright browser started")
        
        return self._browser
    
    async def close(self) -> None:
        """Close browser and cleanup."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
    
    async def validate_job(
        self,
        url: str,
        max_applicants: int = 100,
        max_age_days: int = 7,
    ) -> dict:
        """
        Validate a single job by visiting its LinkedIn page.
        
        Args:
            url: LinkedIn job URL
            max_applicants: Max applicants to pass filter
            max_age_days: Max age in days to pass filter
        
        Returns:
            Validation result dict with:
            - applicant_count: int or None
            - is_active: bool
            - posted_hours_ago: int or None
            - passes_filters: bool
            - failure_reason: str or None
            - validated_at: ISO timestamp
        """
        async with self._semaphore:
            return await self._validate_job_internal(url, max_applicants, max_age_days)
    
    async def _validate_job_internal(
        self,
        url: str,
        max_applicants: int,
        max_age_days: int,
    ) -> dict:
        """Internal validation logic."""
        result = {
            "url": url,
            "applicant_count": None,
            "is_active": True,  # Assume active unless proven otherwise
            "is_reposted": False,  # Phase 10: reposted detection
            "posted_hours_ago": None,
            "passes_filters": False,
            "failure_reason": None,
            "validation_tier": "playwright",
            "validated_at": datetime.utcnow().isoformat(),
        }
        
        try:
            # Rate limit check
            if not await rate_limiter.wait_and_increment():
                result["failure_reason"] = "rate_limit_exceeded"
                return result
            
            browser = await self._ensure_browser()
            page, context = await setup_stealth_page(browser)
            
            try:
                # Navigate to job page
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await random_delay(1, 2)  # Wait for dynamic content
                
                # Extract applicant count
                applicant_count = await self._extract_applicants(page)
                result["applicant_count"] = applicant_count
                
                # Check if job is active (includes closed detection)
                is_active = await self._check_job_active(page)
                result["is_active"] = is_active
                
                # Phase 10: Check if job is reposted
                is_reposted = await self._check_reposted(page)
                result["is_reposted"] = is_reposted
                
                # Extract posted time
                posted_hours = await self._extract_posted_time(page)
                result["posted_hours_ago"] = posted_hours
                
                # Apply filters (order matters for reason clarity)
                max_hours = max_age_days * 24
                
                if not is_active:
                    result["failure_reason"] = "job_closed"
                    result["passes_filters"] = False
                elif is_reposted:
                    result["failure_reason"] = "reposted"
                    result["passes_filters"] = False
                elif applicant_count is not None and applicant_count > max_applicants:
                    result["failure_reason"] = f"too_many_applicants:{applicant_count}"
                    result["passes_filters"] = False
                elif posted_hours is not None and posted_hours > max_hours:
                    result["failure_reason"] = f"too_old:{posted_hours}h"
                    result["passes_filters"] = False
                else:
                    result["passes_filters"] = True
                
                logger.info(
                    f"✓ Validated: {url[:60]}... | "
                    f"applicants={applicant_count}, active={is_active}, "
                    f"hours_old={posted_hours}, passed={result['passes_filters']}"
                )
                
            finally:
                await context.close()
            
        except Exception as e:
            logger.error(f"❌ Validation error for {url}: {e}")
            result["failure_reason"] = f"error:{str(e)[:50]}"
        
        return result
    
    async def _extract_applicants(self, page: Page) -> Optional[int]:
        """Extract applicant count from job page."""
        for selector in LINKEDIN_SELECTORS["applicants"]:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    text = await element.text_content()
                    count = parse_applicant_count(text or "")
                    if count is not None:
                        return count
            except Exception:
                continue
        
        # Fallback: search full page text
        try:
            page_text = await page.content()
            return parse_applicant_count(page_text)
        except Exception:
            return None
    
    async def _check_job_active(self, page: Page) -> bool:
        """Check if job is still accepting applications."""
        # Check for CLOSED selectors (updated for Phase 10)
        for selector in LINKEDIN_SELECTORS.get("closed", []):
            try:
                if await page.locator(selector).count() > 0:
                    return False
            except Exception:
                continue
        
        # Legacy: closed_indicators (backward compatibility)
        for indicator in LINKEDIN_SELECTORS.get("closed_indicators", []):
            try:
                if await page.locator(f'text="{indicator}"').count() > 0:
                    return False
            except Exception:
                continue
        
        # Check for apply button
        for selector in LINKEDIN_SELECTORS["apply_button"]:
            try:
                if await page.locator(selector).count() > 0:
                    return True
            except Exception:
                continue
        
        # If no apply button found but no closed indicator, assume active
        return True
    
    async def _check_reposted(self, page: Page) -> bool:
        """
        Check if job is reposted.
        
        Returns:
            True if reposted detected, False otherwise
        """
        for selector in LINKEDIN_SELECTORS.get("reposted", []):
            try:
                if await page.locator(selector).count() > 0:
                    return True
            except Exception:
                continue
        return False
    
    async def _extract_posted_time(self, page: Page) -> Optional[int]:
        """Extract posted time in hours."""
        for selector in LINKEDIN_SELECTORS["posted_time"]:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    # Try datetime attribute first
                    dt_attr = await element.get_attribute("datetime")
                    if dt_attr:
                        try:
                            posted_dt = datetime.fromisoformat(dt_attr.replace("Z", "+00:00"))
                            hours_ago = (datetime.utcnow() - posted_dt.replace(tzinfo=None)).total_seconds() / 3600
                            return int(hours_ago)
                        except Exception:
                            pass
                    
                    # Fallback to text parsing
                    text = await element.text_content()
                    hours = parse_posted_time(text or "")
                    if hours is not None:
                        return hours
            except Exception:
                continue
        
        return None
    
    async def validate_jobs(
        self,
        jobs: list[dict],
        max_applicants: int = 100,
        max_age_days: int = 7,
        max_to_validate: int = 20,
    ) -> list[dict]:
        """
        Validate multiple jobs in parallel.
        
        Args:
            jobs: List of job dicts with 'link' field
            max_applicants: Max applicants filter
            max_age_days: Max age filter
            max_to_validate: Max jobs to validate (top N)
        
        Returns:
            Jobs with validation data merged
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, skipping validation")
            return jobs
        
        # Only validate top N
        to_validate = jobs[:max_to_validate]
        
        logger.info(f"🔍 Validating {len(to_validate)} jobs...")
        
        # Create validation tasks
        tasks = []
        for job in to_validate:
            url = job.get("link") or job.get("job_url", "")
            if url:
                tasks.append(self.validate_job(url, max_applicants, max_age_days))
        
        # Run in parallel (limited by semaphore)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results back into jobs
        validated_jobs = []
        for i, (job, result) in enumerate(zip(to_validate, results)):
            if isinstance(result, Exception):
                logger.error(f"Validation task failed: {result}")
                job["validation_error"] = str(result)
                validated_jobs.append(job)
            else:
                job.update({
                    "applicant_count": result.get("applicant_count"),
                    "is_active": result.get("is_active"),
                    "posted_hours_ago": result.get("posted_hours_ago"),
                    "passes_validation": result.get("passes_filters", False),
                    "validation_reason": result.get("failure_reason"),
                    "validated_at": result.get("validated_at"),
                })
                
                # Only include jobs that pass validation
                if result.get("passes_filters", True):
                    validated_jobs.append(job)
                else:
                    logger.debug(f"   ✗ Filtered: {job.get('title', 'Unknown')[:40]} - {result.get('failure_reason')}")
        
        # Add remaining unvalidated jobs
        validated_jobs.extend(jobs[max_to_validate:])
        
        await self.close()
        
        logger.info(f"   Validation complete: {len(validated_jobs)} jobs remaining")
        return validated_jobs


# Singleton validator
job_validator = JobValidator()

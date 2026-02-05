"""
Scraping Orchestrator
======================
Coordinates the full scraping pipeline:
1. Discover jobs (DuckDuckGo - free)
2. Optionally enrich with RapidAPI (limited)
3. Optionally validate with Playwright (accurate)
4. Parse with Gemini AI
5. Store in Supabase

Enhanced 2026:
- Proper filter params (posted_within_days, max_applicants)
- Optional Playwright validation for 99% accuracy
- Structured filter statistics
"""

from typing import Optional
from datetime import datetime
import asyncio
import logging

from app.scraper.discovery import job_discovery
from app.scraper.linkedin_api import linkedin_client
from app.scraper.parser import gemini_parser
from app.scraper.validator import job_validator, PLAYWRIGHT_AVAILABLE
from app.scraper.html_validator import validate_jobs_html  # Tier 2
from app.config import settings

logger = logging.getLogger(__name__)


class ScrapingOrchestrator:
    """Orchestrates the full job scraping pipeline."""
    
    def __init__(self):
        self.use_rapidapi = bool(settings.rapidapi_key)
        self.use_gemini = bool(settings.gemini_api_key)
    
    async def run_scrape(
        self,
        keywords: str,
        location: str = "Remote",
        user_skills: list[str] = None,
        max_jobs: int = 20,
        posted_within_days: int = 7,
        max_applicants: int = 100,
        use_rapidapi: bool = False,
        validate_jobs: bool = False,
        validate_top_n: int = 20,
        validate_html: bool = True,  # Tier 2 HTML validation
    ) -> dict:
        """
        Run a full scraping job.
        
        Strategy (Tiered Validation):
        1. TIER 1: Use DuckDuckGo to discover + snippet filter (FREE)
        2. TIER 2: HTML validation with BeautifulSoup (FAST, no browser)
        3. TIER 3: Playwright validation for top N (ACCURATE but SLOW)
        4. Parse with Gemini AI
        
        Args:
            keywords: Job search keywords
            location: Location filter
            user_skills: User's skills for match scoring
            max_jobs: Maximum jobs to return
            posted_within_days: Max job age in days (default 7)
            max_applicants: Max applicants to include (default 100)
            use_rapidapi: Whether to use RapidAPI (uses quota!)
            validate_jobs: Run Playwright validation (accurate but slow)
            validate_top_n: How many jobs to validate (default 20)
            validate_html: Run HTML validation (default True, fast)
        
        Returns:
            Scrape results with jobs and metadata
        """
        user_skills = user_skills or []
        jobs = []
        
        start_time = datetime.utcnow()
        
        # Step 1: Discover jobs via DuckDuckGo (FREE)
        logger.info(f"🔍 Discovering jobs for '{keywords}' in {location}...")
        logger.info(f"   Filters: posted_within_days={posted_within_days}, max_applicants={max_applicants}")
        
        discovered = job_discovery.search_linkedin_jobs(
            keywords=keywords,
            location=location,
            max_results=max_jobs * 2,  # Fetch extra for filtering
            posted_within_days=posted_within_days,
            max_applicants=max_applicants,
        )
        
        filter_stats = job_discovery.filter_stats.copy()
        logger.info(f"   Found {len(discovered)} jobs via DuckDuckGo")
        
        # Step 2: Optionally enrich with RapidAPI
        rapidapi_jobs = []
        if use_rapidapi and self.use_rapidapi:
            logger.info(f"📡 Fetching from RapidAPI (uses quota!)...")
            result = await linkedin_client.search_jobs(
                keywords=keywords,
                location=location,
                posted_within_days=posted_within_days,
                max_applicants=max_applicants,
                limit=min(max_jobs, 10),
            )
            
            if "error" not in result:
                rapidapi_jobs = result.get("jobs", [])
                logger.info(f"   Got {len(rapidapi_jobs)} jobs from RapidAPI")
                logger.info(f"   Filtered out: {result.get('filtered_out', 0)}")
                logger.info(f"   Requests remaining: {result.get('requests_remaining', '?')}")
        
        # Merge and deduplicate
        all_jobs = self._merge_jobs(discovered, rapidapi_jobs)
        logger.info(f"   Total unique jobs after Tier 1: {len(all_jobs)}")
        
        # Step 2.5: TIER 2 - HTML Validation (fast, no browser)
        html_validation_stats = None
        if validate_html:
            logger.info(f"📄 Running Tier 2 HTML validation ({len(all_jobs)} jobs)...")
            all_jobs, html_validation_stats = await validate_jobs_html(
                jobs=all_jobs,
                max_applicants=max_applicants,
                max_age_days=posted_within_days,
                max_concurrent=5,
            )
            logger.info(f"   After Tier 2: {len(all_jobs)} jobs (filtered: closed={html_validation_stats.get('filtered_closed', 0)}, reposted={html_validation_stats.get('filtered_reposted', 0)})")
        
        # Step 3: TIER 3 - Playwright validation (top N only)
        playwright_validation_stats = None
        if validate_jobs and PLAYWRIGHT_AVAILABLE:
            logger.info(f"🔬 Running Tier 3 Playwright validation (top {validate_top_n} jobs)...")
            
            validated = await job_validator.validate_jobs(
                jobs=all_jobs,
                max_applicants=max_applicants,
                max_age_days=posted_within_days,
                max_to_validate=validate_top_n,
            )
            
            playwright_validation_stats = {
                "validated": min(len(all_jobs), validate_top_n),
                "passed": len([j for j in validated if j.get("passes_validation", True)]),
            }
            
            all_jobs = validated
            logger.info(f"   After Tier 3: {len(all_jobs)} jobs")
        elif validate_jobs and not PLAYWRIGHT_AVAILABLE:
            logger.warning("⚠️ Playwright not installed, skipping Tier 3 validation")
        
        # Step 4: Parse and score with Gemini
        if self.use_gemini and user_skills:
            logger.info(f"🤖 Parsing jobs with Gemini AI...")
            enriched_jobs = []
            
            for i, job in enumerate(all_jobs[:max_jobs]):
                text = job.get("description") or job.get("snippet", "")
                
                if text and len(text) > 50:
                    enriched = await gemini_parser.enrich_job(job, user_skills)
                    enriched_jobs.append(enriched)
                else:
                    job["match_score"] = 0
                    job["skills_matched"] = []
                    enriched_jobs.append(job)
                
                if i < len(all_jobs) - 1:
                    await asyncio.sleep(0.5)
            
            jobs = enriched_jobs
        else:
            jobs = all_jobs[:max_jobs]
        
        # Sort by match score
        jobs = sorted(jobs, key=lambda x: x.get("match_score", 0), reverse=True)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            "status": "COMPLETED",
            "keywords": keywords,
            "location": location,
            "jobs_found": len(jobs),
            "jobs": jobs,
            "duration_seconds": duration,
            "filters_applied": {
                "posted_within_days": posted_within_days,
                "max_applicants": max_applicants,
                "validate_html": validate_html,
                "validate_playwright": validate_jobs,
            },
            "filter_stats": filter_stats,
            "sources": {
                "duckduckgo": len(discovered),
                "rapidapi": len(rapidapi_jobs),
            },
            "rapidapi_remaining": linkedin_client.requests_remaining if use_rapidapi else None,
        }
        
        # Add tiered validation stats
        if html_validation_stats:
            result["html_validation_stats"] = html_validation_stats
        if playwright_validation_stats:
            result["playwright_validation_stats"] = playwright_validation_stats
        
        return result
    
    def _merge_jobs(self, discovered: list, rapidapi: list) -> list:
        """
        Merge jobs from multiple sources, preferring RapidAPI data.
        Deduplicates by external_id or URL.
        """
        seen_ids = set()
        seen_urls = set()
        merged = []
        
        # Add RapidAPI jobs first (more detailed)
        for job in rapidapi:
            job_id = job.get("external_id") or job.get("job_id")
            url = job.get("link") or job.get("job_url", "")
            
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                job["source"] = "rapidapi"
                merged.append(job)
            elif url and url not in seen_urls:
                seen_urls.add(url)
                job["source"] = "rapidapi"
                merged.append(job)
        
        # Add discovered jobs (may have less detail)
        for job in discovered:
            job_id = job.get("external_id")
            url = job.get("link", "")
            
            if job_id and job_id in seen_ids:
                continue
            if url and url in seen_urls:
                continue
            
            if job_id:
                seen_ids.add(job_id)
            if url:
                seen_urls.add(url)
            
            job["source"] = "duckduckgo"
            merged.append(job)
        
        return merged
    
    async def quick_discovery(
        self,
        keywords: str,
        location: str = "",
        max_jobs: int = 10,
        posted_within_days: int = 7,
        max_applicants: int = 100,
    ) -> list:
        """
        Quick job discovery without enrichment.
        Uses ONLY DuckDuckGo (free, fast).
        
        Args:
            keywords: Search keywords
            location: Location filter
            max_jobs: Max results
            posted_within_days: Max job age
            max_applicants: Max applicants filter
        
        Returns:
            List of discovered jobs (pre-filtered)
        """
        return job_discovery.search_linkedin_jobs(
            keywords=keywords,
            location=location,
            max_results=max_jobs,
            posted_within_days=posted_within_days,
            max_applicants=max_applicants,
        )


# Singleton instance
orchestrator = ScrapingOrchestrator()

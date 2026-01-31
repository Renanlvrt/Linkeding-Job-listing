"""
Scraping Orchestrator
======================
Coordinates the full scraping pipeline:
1. Discover jobs (DuckDuckGo - free)
2. Optionally enrich with RapidAPI (limited)
3. Parse with Gemini AI
4. Store in Supabase
"""

from typing import Optional
from datetime import datetime
import asyncio

from app.scraper.discovery import job_discovery
from app.scraper.linkedin_api import linkedin_client
from app.scraper.parser import gemini_parser
from app.config import settings


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
        use_rapidapi: bool = False,  # Default to free method
    ) -> dict:
        """
        Run a full scraping job.
        
        Strategy:
        1. Use DuckDuckGo to discover job URLs (FREE, UNLIMITED)
        2. Optionally use RapidAPI to get full details (LIMITED)
        3. Use Gemini to parse and score jobs
        
        Args:
            keywords: Job search keywords
            location: Location filter
            user_skills: User's skills for match scoring
            max_jobs: Maximum jobs to return
            use_rapidapi: Whether to use RapidAPI (uses quota!)
        
        Returns:
            Scrape results with jobs and metadata
        """
        user_skills = user_skills or []
        jobs = []
        
        start_time = datetime.utcnow()
        
        # Step 1: Discover jobs via DuckDuckGo (FREE)
        print(f"🔍 Discovering jobs for '{keywords}' in {location}...")
        discovered = job_discovery.search_linkedin_jobs(
            keywords=keywords,
            location=location,
            max_results=max_jobs,
        )
        
        print(f"   Found {len(discovered)} jobs via DuckDuckGo")
        
        # Step 2: Optionally enrich with RapidAPI
        rapidapi_jobs = []
        if use_rapidapi and self.use_rapidapi:
            print(f"📡 Fetching from RapidAPI (uses quota!)...")
            result = await linkedin_client.search_jobs(
                keywords=keywords,
                location=location,
                limit=min(max_jobs, 10),  # Keep low to save quota
            )
            
            if "error" not in result:
                rapidapi_jobs = result.get("jobs", [])
                print(f"   Got {len(rapidapi_jobs)} jobs from RapidAPI")
                print(f"   Requests remaining: {result.get('requests_remaining', '?')}")
        
        # Merge and deduplicate
        all_jobs = self._merge_jobs(discovered, rapidapi_jobs)
        print(f"   Total unique jobs: {len(all_jobs)}")
        
        # Step 3: Parse and score with Gemini
        if self.use_gemini and user_skills:
            print(f"🤖 Parsing jobs with Gemini AI...")
            enriched_jobs = []
            
            for i, job in enumerate(all_jobs[:max_jobs]):
                # Get text to parse
                text = job.get("description") or job.get("snippet", "")
                
                if text and len(text) > 50:
                    enriched = await gemini_parser.enrich_job(job, user_skills)
                    enriched_jobs.append(enriched)
                else:
                    # No description to parse, set default score
                    job["match_score"] = 0
                    job["skills_matched"] = []
                    enriched_jobs.append(job)
                
                # Rate limit Gemini calls
                if i < len(all_jobs) - 1:
                    await asyncio.sleep(0.5)
            
            jobs = enriched_jobs
        else:
            jobs = all_jobs[:max_jobs]
        
        # Sort by match score
        jobs = sorted(jobs, key=lambda x: x.get("match_score", 0), reverse=True)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "COMPLETED",
            "keywords": keywords,
            "location": location,
            "jobs_found": len(jobs),
            "jobs": jobs,
            "duration_seconds": duration,
            "sources": {
                "duckduckgo": len(discovered),
                "rapidapi": len(rapidapi_jobs),
            },
            "rapidapi_remaining": linkedin_client.requests_remaining if use_rapidapi else None,
        }
    
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
    ) -> list:
        """
        Quick job discovery without enrichment.
        Uses ONLY DuckDuckGo (free, fast).
        
        Great for testing or when you don't need match scores.
        """
        return job_discovery.search_linkedin_jobs(
            keywords=keywords,
            location=location,
            max_results=max_jobs,
        )


# Singleton instance
orchestrator = ScrapingOrchestrator()
